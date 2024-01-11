from django import forms


class DictationForm(forms.Form):
    """Dictation form."""

    textarea = forms.CharField(
        required=False,
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control w-100 p-2",
                "rows": 4,
                "placeholder": "Transcribe the sentences you hear...",
                "autofocus": True,
                "autocomplete": "off",
                "autocapitalize": "off",
                "spellcheck": "false",
                "data-gramm": "false",
                "data-gramm_editor": "false",
                "data-enable-grammarly": "false",
            }
        ),
    )

    def clean(self):
        """Clean."""
        cleaned_data = super().clean()
        data = cleaned_data.get("textarea")
        return data
