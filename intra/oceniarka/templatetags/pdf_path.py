from oceniarka.functions import list_of_coordinated_topics_function
from intra.secret import FILE_SERVER
from django import template

register = template.Library()


@register.filter
def pdf_path(control, user):
    nr_prac = '010' if control.nr_prac > 99 else '0100' + str(control.nr_prac)
    id_kont = 'K' + str(control.id_kont).zfill(3)
    list_of_topics = list_of_coordinated_topics_function(user)
    search_topics = ' '.join(list_of_topics)

    return f"http://{FILE_SERVER}/Desktop/New/{control.rok}/{nr_prac}/{id_kont}/{control.typ_dok}.pdf" \
           f"?#search={search_topics}&zoom=85&scrollbar=1&toolbar=0&navpanes=0&pagemode=thumbs"
