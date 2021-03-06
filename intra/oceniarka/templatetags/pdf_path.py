from oceniarka.functions import get_list_of_coordinated_topics
from intra.secret import FILE_SERVER
from django import template

register = template.Library()


@register.filter
def pdf_path(control, user):
    nr_prac = '010' if control.nr_prac > 99 else '0100' + str(control.nr_prac)
    id_kont = 'K' + str(control.ident_kont).zfill(3)
    list_of_topics = get_list_of_coordinated_topics(user)
    search_topics = ' '.join(list_of_topics)

    # return f"http://{FILE_SERVER}/Desktop/New/{control.rok}/{nr_prac}/{id_kont}/{control.typ_dok}.pdf" \
    #        f"?#search={search_topics}&zoom=85&scrollbar=1&toolbar=0&navpanes=0&pagemode=thumbs"
    return f"file://///01bssv04/Archiwum%20skan%C3%B3w/2019/010002/010002-53-K003_2019.pdf" \
           f"?#search={search_topics}&zoom=85&scrollbar=1&toolbar=0&navpanes=0&pagemode=thumbs"


