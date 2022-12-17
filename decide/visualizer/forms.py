from django import forms

class TranslateForm(forms.Form):
    language = forms.ChoiceField(
        label="Language",
        choices=[("en_US", "English"), ("es_ES", "Español")],
        widget=forms.RadioSelect
    )
