from allauth.account.forms import SignupForm, LoginForm, ResetPasswordForm
from django.forms import BooleanField

class BootstrapAllauthFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.label and not isinstance(field, BooleanField):
                prefix = "Выберите" if hasattr(field.widget, 'choices') else "Введите"
                label_text = field.label.lower()
                field.widget.attrs['placeholder'] = f"{prefix} {label_text}"

class CustomSignupForm(BootstrapAllauthFormMixin, SignupForm): pass
class CustomLoginForm(BootstrapAllauthFormMixin, LoginForm): pass
class CustomResetPasswordForm(BootstrapAllauthFormMixin, ResetPasswordForm): pass
