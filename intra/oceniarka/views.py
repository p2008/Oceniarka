from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.shortcuts import render
from django.views import View
from datetime import date

# Create your views here.
from django.views.generic import FormView

from oceniarka.forms import DocumentOtherDocs, DocumentZk
from oceniarka.models import Control, Document, Coordinator, ControlTopic


def list_of_topics_function(user):
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
        list_of_topics = list_of_topics_function(request.user)

        controls_in_history = Document.objects.\
            filter(is_evaluated=False,
                   control_year__gt=start_year_of_check,
                   coordinator__inspector__username=request.user)

        controls = Control.objects.using('kontrole').\
            filter(rok__gt=start_year_of_check,
                   control_topics__temat__in=list_of_topics).distinct()

        if len(controls_in_history) > 0:
            controls.exclude(pk__in=controls_in_history.pk)

        ctx = {'controls': controls}
        return render(request, 'oceniarka/control_list_template.html', ctx)


class ControlDocuments(View):
    """Wypisane są dokumenty: karta statystyczna i wszystkie dokumenty,
    gdzie pojawił się temat.
    Odhaczenie checkboxa w KS odhacza checkboxy w dokumnetach
    Po prawej stronie okna podgląd pdf ze ścieżki sieciowej
    Kliknięcie przycisku Utwórz Email przenosi do widoku email."""

    def get(self, request, control_id):

        #region pdf
        file_server = '127.0.0.1:8080'
        control = Control.objects.using('kontrole').get(pk=control_id)
        nr_prac = '010' if control.nr_prac > 99 else '0100' + str(control.nr_prac)
        id_kont = 'K' + str(control.id_kont).zfill(3)
        list_of_topics = list_of_topics_function(request.user)
        search_topics = ' '.join(list_of_topics)
        #endregion

        instance = ControlTopic.objects.using('kontrole').filter(kontrola=control)

        form = DocumentZk(instance=instance)

        ctx = {'control': control,
               'file_server': file_server,
               'nr_prac': nr_prac,
               'id_kont': id_kont,
               'search_topics': search_topics,
               'form': form}

        return render(request, 'oceniarka/control_document_template.html', ctx)

    def post(self, request, control_id):
        form = DocumentZk(request.POST)

        if form.is_valid():
            """przypisać do tabeli document"""

        pass


class Email():
    """autogenerowany email w oparciu o formę z widoku control_documents.
    Pozwala przeczytać wygenerowany email. Kliknięcie przycisku wyślij i oceń
    przenosi do control_list i wysyłany jest email do inspektora i statystyka"""
    pass


class History():
    """Wyszukiwarka już ocenionych kontroli.
    Szukanie po dacie oceny i dacie kontroli, nr kontroli, nr pracownika"""
    pass
