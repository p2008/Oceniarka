from .models import Coordinator


def list_of_coordinated_topics_function(user):
    coordinator = Coordinator.objects.get(inspector__username=user)
    topics_to_eval = coordinator.topic.all()
    return topics_to_eval.values_list('name', flat=True)[::1]


def queryset_to_list(queryset, field_name):
    return queryset.values_list(field_name, flat=True)[::1]



