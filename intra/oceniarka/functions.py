from .models import Coordinator
from oceniarka import outer_models


def get_list_of_coordinated_topics(user):
    coordinator = Coordinator.objects.get(inspector__username=user)
    topics_to_eval = coordinator.topic.all()
    return topics_to_eval.values_list('name', flat=True)[::1]


def queryset_to_list(queryset, field_name):
    return queryset.values_list(field_name, flat=True)[::1]


def queryset_to_list_of_tuples(queryset, field_name):
    return [list(filter(None, _)) for _ in queryset.values_list(*field_name)[::1]]


def get_document_types_in_control(control_id, model):
    main_model = get_main_and_topic_model(model)['main_model']
    return main_model.objects.using('kontrole').filter(
        id_kontroli=control_id).order_by('id_dok')


def get_field_name_for_order_by(model):
    topic_model = get_main_and_topic_model(model)['topic_model']
    return topic_model._meta.get_fields()[0].name


def get_main_and_topic_model(model):
    main_model = getattr(outer_models, model)
    topic_model = getattr(outer_models, model + 'Topic')
    return {'main_model': main_model, 'topic_model': topic_model}


def get_document_instance_and_name(model, document):
    topic_model = get_main_and_topic_model(model)['topic_model']
    document_instance = topic_model.objects.using('kontrole').filter(
        id_dok=document
    ).order_by(get_field_name_for_order_by(model))

    document_name = f'{document.rodzaj_dok[:2]}{document.ident_dok}'

    return document_instance, document_name


def get_all_new_topics(form, initial_control_topics, MAX_TOPICS, addon=''):
    all_new_topics = list()
    new_topics_fields_position = range(len(initial_control_topics) + 1, MAX_TOPICS + 1)
    for nt in new_topics_fields_position:
        field_name = f'new_topic_{addon}_{nt}'
        new_topic = form.cleaned_data.get(field_name)

        if form.cleaned_data.get(field_name):
            new_topic = form.cleaned_data.get(field_name)

            if new_topic.name in all_new_topics:
                form.add_error(field_name, 'Duplicate')
            else:
                all_new_topics.append(new_topic.name)

    return all_new_topics


def get_topics_not_coordinated(initial_control_topics, user):
    list_of_coordinated_topics = get_list_of_coordinated_topics(
        user)

    return [_ for _ in initial_control_topics if _ not in list_of_coordinated_topics]


def get_topics_for_delete(initial_row_topics, coordinated_topics_left_in_row, topics_not_coordinated):

    return [set(initial_row_topics) - set(coordinated_topics_left_in_row) - set(topics_not_coordinated)]
