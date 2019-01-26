from pprint import pprint

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.forms import model_to_dict, formset_factory
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from datetime import date, datetime
from oceniarka.forms import DocumentOtherDocs, DocumentZk, EmailForm
from oceniarka.models import Control, Document, Coordinator, ControlTopic, \
    Email

# Create your views here.


ZK_MAX_TOPICS = 8  # max możliwych tematów w ZK


def list_of_coordinated_topics_function(user):
    coordinator = Coordinator.objects.get(inspector__username=user)
    topics_to_eval = coordinator.topic.all()
    list_of_topics = [topic.name for topic in topics_to_eval]
    return list_of_topics


class ControlList(LoginRequiredMixin, View):
    """lista kontroli z danego roku.
    Na zielono te, które są do oceny ujęte w grupie Nowe.
    Po naciśnięciu kontroli przenosi do widoku control_documents"""

    def get(self, request):
        start_year_of_check = date.today().year - 1
        list_of_coordinated_topics = \
            list_of_coordinated_topics_function(request.user)

        controls_in_history = Document.objects. \
            filter(is_evaluated=True,
                   control_year__gt=start_year_of_check,
                   coordinator__inspector__username=request.user)

        list_of_controls = list()
        for c in controls_in_history:
            list_of_controls.append(c.control_id)

        controls = Control.objects.using('kontrole'). \
            filter(rok__gt=start_year_of_check,
                   control_topics__temat__in=list_of_coordinated_topics)
        if len(controls_in_history) > 0:
            # pobierz kontrole według roku i koordynowanych przez usera tematów
            # wyklucz już ocenione kontrole
            controls = controls.exclude(pk__in=list_of_controls)

        controls = controls.distinct()
        ctx = {'controls': controls}
        return render(request, 'oceniarka/control_list_template.html', ctx)


class ControlDocuments(LoginRequiredMixin, View):
    """Wypisane są dokumenty: karta statystyczna i wszystkie dokumenty,
    gdzie pojawił się temat.
    Odhaczenie checkboxa w KS odhacza checkboxy w dokumnetach
    Po prawej stronie okna podgląd pdf ze ścieżki sieciowej
    Kliknięcie przycisku Utwórz Email przenosi do widoku email."""

    def get(self, request, control_id):

        # region pdf
        file_server = '127.0.0.1:8080'
        control = Control.objects.using('kontrole').get(pk=control_id)
        nr_prac = '010' if control.nr_prac > 99 else '0100' + str(
            control.nr_prac)
        id_kont = 'K' + str(control.id_kont).zfill(3)
        list_of_topics = list_of_coordinated_topics_function(request.user)
        search_topics = ' '.join(list_of_topics)
        # endregion

        instance = ControlTopic.objects.using('kontrole').filter(
            kontrola=control)

        form = DocumentZk(instance=instance)

        ctx = {'control': control,
               'file_server': file_server,
               'nr_prac': nr_prac,
               'id_kont': id_kont,
               'search_topics': search_topics,
               'form': form}

        return render(request, 'oceniarka/control_document_template.html', ctx)

    def post(self, request, control_id):
        control = Control.objects.using('kontrole').get(pk=control_id)
        instance = ControlTopic.objects.using('kontrole').filter(
            kontrola=control)

        form = DocumentZk(data=request.POST, instance=instance)

        if form.is_valid():
            list_of_coordinated_topics = list_of_coordinated_topics_function(
                request.user)
            coordinated_topics_left_in_control = form.cleaned_data.get('topic')

            initial_control_topics = []
            for t in instance:
                initial_control_topics.append(t.temat)

            topics_not_coordinated = [
                x for x in initial_control_topics
                if x not in list_of_coordinated_topics
            ]

            all_new_topics = list()
            new_topics_fields_position = \
                range(len(initial_control_topics) + 1, ZK_MAX_TOPICS + 1)
            for nt in new_topics_fields_position:
                field_name = f'new_topic_{nt}'

                if form.cleaned_data.get(field_name):
                    new_topic = form.cleaned_data.get(field_name)
                    pprint(new_topic)
                    if new_topic.name in all_new_topics:
                        form.add_error(field_name, 'Duplicate')
                    else:
                        all_new_topics.append(new_topic.name)

            nr_prac = '010' if control.nr_prac > 99 else '0100'
            nr_prac = nr_prac + str(control.nr_prac)
            control_number = 'K' + str(control.id_kont).zfill(3)
            string_of_topics_to_db = ','.join(
                coordinated_topics_left_in_control +
                all_new_topics +
                topics_not_coordinated
            )
            inspector = User.objects.get(username=nr_prac)
            coordinator = Coordinator.objects.get(
                inspector__username=request.user)
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

            # topics_left_in_control + topics_not_coordinated
            topics_for_delete = list(
                set(initial_control_topics) -
                set(coordinated_topics_left_in_control) -
                set(topics_not_coordinated)
            )

            if topics_for_delete is not None or all_new_topics is not None:
                email_message = f'{nr_prac}-{control_number}: ' \
                                f'Proszę o wykreślenie tematów:' \
                                f' {topics_for_delete} i dodanie: ' \
                                f'{all_new_topics} w karcie {control.typ_dok}'

                Email.objects.update_or_create(
                    email_to=inspector.email,
                    email_from=coordinator.inspector.email,
                    control_number=control_number,
                    defaults={
                        'email_message': email_message,
                    }
                )

        return redirect(reverse('lista-kontroli'))


class EmailView(LoginRequiredMixin, View):
    """autogenerowany email w oparciu o formę z widoku control_documents.
    Pozwala przeczytać wygenerowany email. Kliknięcie przycisku wyślij i oceń
    przenosi do control_list i wysyłany jest email do inspektora i statystyka"""

    def __init__(self, **kwargs):
        super(EmailView, self).__init__(**kwargs)
        self.EmailFormSet = formset_factory(EmailForm, extra=0)

    def get(self, request):
        coordinator = Coordinator.objects.get(
            inspector__username=request.user)
        coordinator_email = coordinator.inspector.email
        coordinator_emails_from_db = \
            Email.objects.filter(email_from=coordinator_email)

        if coordinator_emails_from_db is None:
            info_message = 'Brak e-mailów do wysłania'
            messages.info(request, info_message)
            return render(request, 'oceniarka/email.html')
        else:
            inspectors_emails = \
                [x for x in coordinator_emails_from_db.distinct('email_to')]

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
                    email_message_to_inspector = email_message_to_inspector + \
                                                 single_message + '\n'

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
            # email_from = secret.EMAIL_HOST_USER
            email_statisticians = [User.objects.get(id=1).email]
            all_messages = ''

            for email_form in email_formset:
                pprint(email_form)
                email_message = email_form.cleaned_data.get('email_message')
                # email_to = [email_form.cleaned_data.get('email_to')]
                email_to = secret.email_to
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

            # emails_to_delete = request.user.coordinators. \
            #     coordinator_emails_from_db()
            messages.info(request, 'Emaile wysłane pomyślnie')
            return redirect(reverse('lista-kontroli'))
        else:
            messages.info(request, 'Nastąpiły błędy, emaile nie wysłane')
            email_formset.errors()
            return render(request, 'oceniarka/email.html', self.ctx)



class History(LoginRequiredMixin, View):
    """Wyszukiwarka już ocenionych kontroli.
    Szukanie po dacie oceny i dacie kontroli, nr kontroli, nr pracownika"""
    pass
