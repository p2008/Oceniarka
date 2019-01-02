from django.shortcuts import render

# Create your views here.


class control_list():
    """lista kontroli z danego roku.
    Na zielono te, które są do oceny ujęte w grupie Nowe.
    Poniżej grupa Ocenione w kolorze mniej więcej tła.
    Po naciśnięciu kontroli przenosi do widoku control_documents"""
    pass


class control_documents():
    """Wypisane są dokumenty: karta statystyczna i wszystkie dokumenty,
    gdzie pojawił się temat.
    Odhaczenie checkboxa w KS odhacza checkboxy w dokumnetach
    Po prawej stronie okna podgląd pdf ze ścieżki sieciowej
    Kliknięcie przycisku Utwórz Email przenosi do widoku email."""
    pass


class email():
    """autogenerowany email w oparciu o formę z widoku control_documents.
    Pozwala przeczytać wygenerowany email. Kliknięcie przycisku wyślij i oceń
    przenosi do control_list i wysyłany jest email do inspektora i statystyka"""
    pass
