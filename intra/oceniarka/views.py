from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from datetime import date, datetime
from oceniarka.forms import DocumentOtherDocs, DocumentZk
from oceniarka.models import Control, Document, Coordinator, ControlTopic, \
    Topic

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

        if len(controls_in_history) > 0:
            # pobierz kontrole według roku i koordynowanych przez usera tematów
            controls = Control.objects.using('kontrole'). \
                filter(rok__gt=start_year_of_check,
                       control_topics__temat__in=list_of_coordinated_topics). \
                exclude(pk__in=list_of_controls).distinct()
        else:
            controls = Control.objects.using('kontrole'). \
                filter(rok__gt=start_year_of_check,
                       control_topics__temat__in=list_of_coordinated_topics).distinct()

        ctx = {'controls': controls}
        return render(request, 'oceniarka/control_list_template.html', ctx)


class ControlDocuments(View):
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
            topic = form.cleaned_data.get('topic')

            all_new_topics = list()
            for nt in range(len(topic) + 1, ZK_MAX_TOPICS + 1):
                field_name = f'new_topic_{nt}'

                if form.cleaned_data.get(field_name):
                    new_topic = form.cleaned_data.get(field_name)
                    pprint(new_topic)
                    if new_topic.name in all_new_topics:
                        form.add_error(field_name, 'Duplicate')
                    else:
                        all_new_topics.append(new_topic.name)

            nr_prac = '010' if control.nr_prac > 99 else '0100' + str(
                control.nr_prac)
            id_kont = 'K' + str(control.id_kont).zfill(3)
            string_of_topics = ','.join(topic + all_new_topics)

            Document.objects.update_or_create(
                control_id=control_id,
                coordinator=Coordinator.objects.get(
                    inspector__username=request.user),
                defaults={
                    'inspector': User.objects.get(username=nr_prac),
                    'control_number': id_kont,
                    'control_year': control.rok,
                    'document_type': control.typ_dok,
                    'field_current_value': string_of_topics,
                    'is_evaluated': True,
                    'evaluation_date': datetime.now()}
            )

        return redirect(reverse('lista-kontroli'))


class Email():
    """autogenerowany email w oparciu o formę z widoku control_documents.
    Pozwala przeczytać wygenerowany email. Kliknięcie przycisku wyślij i oceń
    przenosi do control_list i wysyłany jest email do inspektora i statystyka"""
    pass


class History():
    """Wyszukiwarka już ocenionych kontroli.
    Szukanie po dacie oceny i dacie kontroli, nr kontroli, nr pracownika"""
    pass
