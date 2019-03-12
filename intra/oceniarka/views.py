from datetime import date, datetime
from pprint import pprint

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from oceniarka.functions import get_list_of_coordinated_topics, queryset_to_list, queryset_to_list_of_tuples, \
    get_document_types_in_control, get_field_name_for_order_by, get_main_and_topic_model, \
    get_document_instance_and_name, get_all_new_topics, get_topics_not_coordinated, get_topics_for_delete
from intra.secret import ZK_MAX_TOPICS, OTHER_MAX_TOPICS
from oceniarka.forms import DocumentZkForm, EmailForm, SearchForm, DocumentOtherForm
from oceniarka.models import Control, Document, Coordinator, ControlTopic, Email
from oceniarka import outer_models


# Create your views here.


class ControlList(LoginRequiredMixin, View):
    """lista kontroli z danego roku.
    Pobiera kontrole z historii i bazy po czym wypisuje te których nie ma w historii.
    Przenosi do widoku control_documents"""

    def get(self, request):
        start_year_of_check = date.today().year - 1
        list_of_coordinated_topics = \
            get_list_of_coordinated_topics(request.user)

        controls_in_history = Document.objects. \
            filter(is_evaluated=True,
                   control_year__gt=start_year_of_check,
                   coordinator__inspector__username=request.user)

        list_of_controls = queryset_to_list(controls_in_history, 'control_id')

        # pobierz kontrole według roku i koordynowanych przez usera tematów
        controls = Control.objects.using('kontrole'). \
            filter(rok__gt=start_year_of_check,
                   control_topics__nr_tematu__in=list_of_coordinated_topics)

        if len(controls_in_history) > 0:
            # wyklucz już ocenione kontrole
            controls = controls.exclude(pk__in=list_of_controls)

        controls = controls.distinct()
        ctx = {'controls': controls,
               'evaluated_controls': controls_in_history[0:10]
               }

        if not controls:
            messages.info(request, 'Nie masz kontroli do oceny')
        return render(request, 'oceniarka/control_list_template.html', ctx)


class ControlDocuments(LoginRequiredMixin, View):
    """Wypisane są dokumenty: karta statystyczna i wszystkie dokumenty,
    gdzie pojawił się nr_tematu.
    Odhaczenie checkboxa w karcie stat. odhacza checkboxy w dokumnetach
    Po prawej stronie okna podgląd pdf ze ścieżki sieciowej
    Kliknięcie przycisku Utwórz Email tworzy email i przenosi do widoku listy kontroli."""

    def dispatch(self, request, *args, **kwargs):
        control_topics = Control.objects.using('kontrole'). \
            get(pk=kwargs.get('control_id')).control_topics.all()
        list_control_topics = queryset_to_list(control_topics, 'nr_tematu')
        list_of_coordinated_topics = \
            get_list_of_coordinated_topics(request.user)

        if request.method == 'GET':
            if len(control_topics) > 0:
                if len(set(list_control_topics) - set(
                        list_of_coordinated_topics)) \
                        != len(control_topics):
                    return self.get(request, *args, **kwargs)

            return redirect(reverse('lista-kontroli'))
        else:
            return self.post(request, *args, **kwargs)

    def get(self, request, control_id):
        control = Control.objects.using('kontrole').get(pk=control_id)
        # każdy wiersz to temat
        instance = ControlTopic.objects.using('kontrole').filter(
            id_kontroli=control)

        zk_form = DocumentZkForm(instance=instance)

        ctx = {'control': control,
               'zk_form': zk_form,
               }

        document_forms = {}
        for model in outer_models.DOCUMENTS_IN_CONTROL:  # DOCUMENTS_IN_CONTROL jest listą modeli
            document_types_in_control = get_document_types_in_control(control_id, model)

            # Pętla wykonuje się dla każdego nakazu w kontroli
            for document in document_types_in_control:
                # każdy wiersz to decyzja, która może mieć kilka tematów
                document_instance, document_name = get_document_instance_and_name(model, document)

                document_forms[document_name] = DocumentOtherForm(instance=document_instance, prefix=document_name)

        ctx['document_forms'] = document_forms

        print(ctx)
        return render(request, 'oceniarka/control_document_template.html', ctx)

    def post(self, request, control_id):
        control = Control.objects.using('kontrole').get(pk=control_id)
        instance = ControlTopic.objects.using('kontrole').filter(
            id_kontroli=control)

        form = DocumentZkForm(data=request.POST, instance=instance)

        if form.is_valid():
            coordinated_topics_left_in_control = form.cleaned_data.get('topic')
            initial_control_topics = queryset_to_list(instance, 'nr_tematu')
            topics_not_coordinated = get_topics_not_coordinated(initial_control_topics, request.user)
            all_new_topics = get_all_new_topics(form, initial_control_topics, ZK_MAX_TOPICS)
            nr_prac = outer_models.get_full_nr_prac(control)
            control_number = outer_models.get_full_control_number(control)
            inspector = User.objects.get(username=nr_prac)
            coordinator = Coordinator.objects.get(inspector__username=request.user)
            topics_for_delete = get_topics_for_delete(initial_control_topics,
                                                      coordinated_topics_left_in_control,
                                                      topics_not_coordinated)

            email_topic = f'Kontrola {nr_prac}-{control_number}:'
            email_message = ''
            if len(topics_for_delete) > 0 or len(all_new_topics) > 0:
                email_message = f'Proszę o wykreślenie tematów:' \
                                f' {topics_for_delete} i dodanie: {all_new_topics} w karcie {control.typ_dok}'

            # region Utworzenie listy i dodanie historii oceny
            string_of_topics_to_db = ','.join(
                coordinated_topics_left_in_control +
                all_new_topics +
                topics_not_coordinated
            )

            Document.objects.update_or_create(
                control_id=control_id,
                coordinator=coordinator,
                defaults={
                    'inspector': inspector,
                    'control_number': control_number,
                    'control_year': control.rok,
                    'document_type': control.typ_dok,
                    'field_current_value': string_of_topics_to_db,
                    'is_evaluated': True,
                    'evaluation_date': datetime.now()}
            )
            # endregion

        #Inne Dokumenty
        for model in outer_models.DOCUMENTS_IN_CONTROL:  # DOCUMENTS_IN_CONTROL jest listą modeli
            document_types_in_control = get_document_types_in_control(control_id, model)

            # Pętla wykonuje się dla każdego nakazu w kontroli
            for document in document_types_in_control:
                # każdy wiersz to decyzja, która może mieć kilka tematów
                document_instance, document_name = get_document_instance_and_name(model, document)
                form_document = DocumentOtherForm(data=request.POST, instance=document_instance, prefix=document_name)
                initial_row_topics_list_of_tuples = \
                     queryset_to_list_of_tuples(document_instance, outer_models.topic_fields_in_document())

                if form_document.is_valid():
                    for indx, row in enumerate(document_instance):
                        addon = str(row) + f'{row.number}'
                        coordinated_topics_left_in_row = form_document.cleaned_data.get(f'topic_{addon}') or []
                        initial_row_topics = initial_row_topics_list_of_tuples[indx]
                        topics_not_coordinated = get_topics_not_coordinated(initial_row_topics, request.user)
                        all_new_topics = get_all_new_topics(form_document, initial_row_topics, OTHER_MAX_TOPICS, addon)
                        topics_for_delete = get_topics_for_delete(initial_row_topics,
                                                                  coordinated_topics_left_in_row,
                                                                  topics_not_coordinated)

                        if len(topics_for_delete) > 0 or len(all_new_topics) > 0:
                            email_message += f'\nProszę o wykreślenie tematów w karcie {document_name}/{addon}:' \
                                            f' {topics_for_delete} i dodanie: {all_new_topics} '

        if len(email_message) > 0:
            Email.objects.update_or_create(
                email_to=inspector.email,
                email_from=coordinator.inspector.email,
                control_number=control_number,
                defaults={
                    'email_message': email_message,
                }
            )

            # region Utworzenie listy i dodanie historii oceny
            string_of_topics_to_db = ','.join(
                coordinated_topics_left_in_control +
                all_new_topics +
                topics_not_coordinated
            )

            Document.objects.update_or_create(
                control_id=control_id,
                coordinator=coordinator,
                defaults={
                    'inspector': inspector,
                    'control_number': control_number,
                    'control_year': control.rok,
                    'document_type': control.typ_dok,
                    'field_current_value': string_of_topics_to_db,
                    'is_evaluated': True,
                    'evaluation_date': datetime.now()}
            )
            # endregion


        return redirect(reverse('lista-kontroli'))


class EmailView(LoginRequiredMixin, View):
    """autogenerowany email w oparciu o formę z widoku control_documents.
    Pozwala przeczytać wygenerowany email. Kliknięcie przycisku wyślij i oceń
    przenosi do control_list i wysyłany jest email do inspektora i statystyka"""

    def __init__(self, **kwargs):
        super(EmailView, self).__init__(**kwargs)
        self.EmailFormSet = formset_factory(EmailForm, extra=0)
        self.ctx = {}

    def get(self, request):
        coordinator_email = request.user.email
        coordinator_emails_from_db = request.user.coordinators.first().coordinator_emails_from_db()

        if len(coordinator_emails_from_db) == 0:
            info_message = 'Lista emaili jest pusta. Nie zostały wprowadzone zmiany do ocenianych kontroli'
            messages.info(request, info_message)
            return render(request, 'oceniarka/email.html')
        else:
            inspectors_emails = [x for x in coordinator_emails_from_db.distinct('email_to')]

            initials = []
            for inspector in inspectors_emails:
                complete_emails_dict = {'email_from': coordinator_email}
                inspector_email = inspector.email_to
                single_inspector_emails = coordinator_emails_from_db.filter(
                    email_to=inspector.email_to
                )

                email_message_to_inspector = ''
                for single_email in single_inspector_emails:
                    single_message = single_email.email_message
                    email_message_to_inspector = email_message_to_inspector + single_message + '\n'

                complete_emails_dict['email_to'] = inspector_email
                complete_emails_dict[
                    'email_message'] = email_message_to_inspector
                initials.append(complete_emails_dict)

            email_formset = self.EmailFormSet(initial=initials)

            self.ctx = {'email_formset': email_formset}

            return render(request, 'oceniarka/email.html', self.ctx)

    def post(self, request):
        email_formset = self.EmailFormSet(request.POST)

        if email_formset.is_valid():
            subject = 'Ocena kontroli'
            all_emails_tuple = ()
            email_from = email_formset[0].cleaned_data.get('email_from')
            email_statisticians = [User.objects.get(id=1).email]
            all_messages = ''

            for email_form in email_formset:
                email_message = email_form.cleaned_data.get('email_message')
                # email_to = [email_form.cleaned_data.get('email_to')]
                email_to = secret.email_to  # tymczasowe
                all_messages += email_message + '\n'
                all_emails_tuple += ((subject,
                                      email_message,
                                      email_from,
                                      email_to),)

            subject = 'do statystyka'  # tymczasowe
            all_emails_tuple += ((subject,
                                  all_messages,
                                  email_from,
                                  email_statisticians
                                  ),)

            send_mass_mail(datatuple=all_emails_tuple, fail_silently=False)

            # emails_to_delete
            request.user.coordinators.first(). \
                coordinator_emails_from_db().delete()

            messages.info(request, 'Emaile wysłane pomyślnie')
            return redirect(reverse('lista-kontroli'))
        else:
            messages.info(request, 'Nastąpiły błędy, emaile nie wysłane')
            return render(request, 'oceniarka/email.html', self.ctx)


class History(LoginRequiredMixin, View):
    """Wyszukiwarka już ocenionych kontroli.
    Szukanie po dacie oceny i dacie kontroli, nr kontroli, nr pracownika"""

    def get(self, request):

        controls_list = Document.objects.filter(
            coordinator=self.request.user.coordinators.first(),
            is_evaluated=True,
        ).order_by('evaluation_date')
        page = request.GET.get('page', 1)

        paginator = Paginator(controls_list, 1)
        try:
            controls = paginator.page(page)
        except PageNotAnInteger:
            controls = paginator.page(1)
        except EmptyPage:
            controls = paginator.page(paginator.num_pages)

        search_form = SearchForm()
        ctx = {'controls': controls,
               'searchform': search_form}

        if len(controls) == 0:
            messages.info(request, 'Brak ocenionych kontroli')

        return render(request, 'oceniarka/control_list_template.html', ctx)

    def post(self, request):

        control_number = request.POST.get('search_field')
        found_control_id = Document.objects.get(pk=control_number).control_id

        return redirect('podglad-kontroli', found_control_id)
