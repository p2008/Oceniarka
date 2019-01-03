from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


# Create your views here.


class ControlList(LoginRequiredMixin, View):
    """lista kontroli z danego roku.
    Na zielono te, które są do oceny ujęte w grupie Nowe.
    Poniżej grupa Ocenione w kolorze mniej więcej tła.
    Po naciśnięciu kontroli przenosi do widoku control_documents"""

    def get(self, request):
        ctx = {'xxx': 'xxx'}
        return render(request, 'oceniarka/control_list_template.html', ctx)


class ControlDocuments():
    """Wypisane są dokumenty: karta statystyczna i wszystkie dokumenty,
    gdzie pojawił się temat.
    Odhaczenie checkboxa w KS odhacza checkboxy w dokumnetach
    Po prawej stronie okna podgląd pdf ze ścieżki sieciowej
    Kliknięcie przycisku Utwórz Email przenosi do widoku email."""
    pass


class Email():
    """autogenerowany email w oparciu o formę z widoku control_documents.
    Pozwala przeczytać wygenerowany email. Kliknięcie przycisku wyślij i oceń
    przenosi do control_list i wysyłany jest email do inspektora i statystyka"""
    pass
