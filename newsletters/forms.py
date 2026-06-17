from django import forms
from django.forms import BooleanField

from newsletters.models import Newsletter, Recipient, Message, UserRecipientLink


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field, in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

            if field.label and not isinstance(field, BooleanField):
                prefix = "Выберите" if hasattr(field.widget, 'choices') else "Введите"

                label_text = field.label.lower()
                if label_text:
                    label_text = label_text[0].lower() + label_text[1:]

                field.widget.attrs['placeholder'] = f"{prefix} {label_text}"


class NewsletterForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['message'].help_text = "Выберите сообщение из вашего списка."
        self.fields['recipients'].help_text = "Зажмите Ctrl (или Cmd на Mac), чтобы выбрать несколько получателей."
        if user:
            self.fields['message'].queryset = Message.objects.filter(owner=user)
            user_recipient_ids = UserRecipientLink.objects.filter(user=user).values_list('recipient_id', flat=True)
            self.fields['recipients'].queryset = Recipient.objects.filter(id__in=user_recipient_ids)


class MessageForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'message']


class RecipientCreateForm(StyleFormMixin, forms.ModelForm):
    email = forms.EmailField(max_length=50, label="Почта")

    class Meta:
        model = UserRecipientLink
        fields = ['full_name', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        email_field = self.fields.pop('email')
        self.fields = {'email': email_field, **self.fields}


class RecipientUpdateForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = UserRecipientLink
        fields = ['full_name', 'comment']
