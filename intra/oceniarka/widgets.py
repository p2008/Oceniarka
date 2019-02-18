from dal import autocomplete
from django.db.models import Q

from oceniarka.models import Document


class ControlAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):

        qs = Document.objects.filter(
            coordinator=self.request.user.coordinators.first(),
            is_evaluated=True,
        ).order_by('evaluation_date')

        if self.q:
            qs = qs.filter(Q(control_number__icontains=self.q) |
                           Q(inspector__username__icontains=self.q) |
                           Q(control_year=self.q))

        return qs
