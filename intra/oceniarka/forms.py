from pprint import pprint

from django import forms

from oceniarka.models import Topic, ControlTopic


class DocumentZk(forms.Form):

    """ choice = [('id tematu', nazwa tematu),] """
    def __init__(self, instance, *args, **kwargs):
        super(DocumentZk, self).__init__(*args, **kwargs)
        topics = ControlTopic.objects.using('kontrole').filter(
            kontrola=instance[0].kontrola_id
        )

        self.topic_choices = []
        for t in topics:
            choice = (f'{t.pk}', f'{t.temat}')
            self.topic_choices.append(choice)

        self.fields['topic'].choices = self.topic_choices
        self.fields['topic'].initial = list(range(1, len(topics)+1))

        new_topic_number_of_fields = range(8 - len(topics))
        for nt in new_topic_number_of_fields:
            field_name = f'new_topic_{nt + len(topics) + 1}'
            self.fields[field_name] = forms.ModelChoiceField(
                label='',
                queryset=Topic.objects.filter(is_active=True))

    topic = forms.MultipleChoiceField(choices=[],
                                      widget=forms.CheckboxSelectMultiple)


class DocumentOtherDocs(forms.ModelForm):
    #     def __init__(self, instance, *args, **kwargs):
    #         super(DocumentZk, self).__init__(*args, **kwargs)
    #         topics = ControlTopic.objects.using('kontrole').filter(
    #             kontrola=instance[0].kontrola_id
    #         )
    #
    #         self.topic_choices = []
    #         for t in topics:
    #             choice = (f'{t.pk}', f'{t.temat}')
    #             self.topic_choices.append(choice)
    #
    #         self.fields['topic'].choices = self.topic_choices
    #         self.fields['topic'].initial = list(range(1, len(topics) + 1))
    #
    #         new_topic_number_of_fields = range(4 - len(topics))
    #         for nt in new_topic_number_of_fields:
    #             field_name = f'new_topic_{nt + len(topics) + 1}'
    #             self.fields[field_name] = forms.ModelChoiceField(
    #                 label='',
    #                 queryset=Topic.objects.filter(is_active=True))
    #
    #     topic = forms.MultipleChoiceField(choices=[],
    #                                       widget=forms.CheckboxSelectMultiple)
    pass

