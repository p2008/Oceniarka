from pprint import pprint

from django import forms

from oceniarka.models import Topic

ZK_MAX_TOPICS = 8


class DocumentZk(forms.Form):

    # def __init__(self, instance, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        self.topics = kwargs.pop('instance')
        super(DocumentZk, self).__init__(*args, **kwargs)

        # self.topics = instance
        self.topic_choices = []
        for t in self.topics:
            choice = (f'{t.temat}', f'{t.temat}')
            self.topic_choices.append(choice)

        self.fields['topic'].choices = self.topic_choices
        tuple_of_topics = list(zip(*self.topic_choices))[0]
        self.fields['topic'].initial = tuple_of_topics

        new_topic_number_of_fields = range(ZK_MAX_TOPICS - len(self.topics))
        for nt in new_topic_number_of_fields:
            field_name = f'new_topic_{nt + len(self.topics) + 1}'
            self.fields[field_name] = forms.ModelChoiceField(
                label='',
                required=False,
                queryset=Topic.objects.filter(is_active=True).
                    exclude(name__in=tuple_of_topics)
            )

    topic = forms.MultipleChoiceField(choices=[], required=False,
                                      widget=forms.CheckboxSelectMultiple)


class DocumentOtherDocs(forms.Form):
    pass


class EmailForm(forms.Form):
    email_from = forms.EmailField()
    email_to = forms.EmailField()
    email_message = forms.CharField(widget=forms.Textarea)
