from crispy_forms.helper import FormHelper
from dal import autocomplete
from django import forms

from oceniarka.models import Topic
from secret import ZK_MAX_TOPICS


class DocumentZkForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.topics = kwargs.pop('instance')
        super(DocumentZkForm, self).__init__(*args, **kwargs)

        self.topic_choices = []
        for t in self.topics:
            choice = (f'{t.temat}', f'{t.temat}')
            self.topic_choices.append(choice)

        self.fields['topic'].choices = self.topic_choices
        if len(self.topic_choices) > 0:
            tuple_of_topics = list(zip(*self.topic_choices))[0]
        else:
            tuple_of_topics = []
        self.fields['topic'].initial = tuple_of_topics

        new_topic_number_of_fields = range(ZK_MAX_TOPICS - len(self.topics))

        for nt in new_topic_number_of_fields:
            field_name = f'new_topic_{nt + len(self.topics) + 1}'
            self.fields[field_name] = forms.ModelChoiceField(
                label='',
                required=False,
                queryset=Topic.objects.filter(is_active=True).
                    exclude(name__in=tuple_of_topics),
            )

    topic = forms.MultipleChoiceField(label='topic', choices=[], required=False,
                                      widget=forms.CheckboxSelectMultiple())


class EmailForm(forms.Form):
    # Wyłączenie helper wymagane przez crispy do właściwego renderowania formy
    # bez tego nie zadziała submit
    helper = FormHelper()
    helper.form_tag = False

    email_from = forms.EmailField(label='',
        widget=forms.EmailInput(attrs={'hidden': True}))
    email_to = forms.EmailField(label='Inspektor',
                                widget=forms.EmailInput(attrs={
                                    'readonly': True,
                                }))
    email_message = forms.CharField(label='Wiadomość', min_length=15,
                                    required=True,
                                    widget=forms.Textarea(attrs={
                                        'rows': 5,
                                        'required': True
                                    }))


class SearchForm(forms.Form):

    search_field = forms.ChoiceField(label='', required=False,
                             widget=autocomplete.Select2(
                                 url='control-autocomplete',
                                 attrs={'data-placeholder': 'Podaj co najmniej 3 znaki',
                                        'data-minimum-input-length': 3,
                                        'data-html': True
                                        }
                             ))
