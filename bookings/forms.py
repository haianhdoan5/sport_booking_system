from datetime import timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["start_time", "end_time"]
        widgets = {
            "start_time": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "autocomplete": "off",
                    "step": "1800",
                },
            ),
            "end_time": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "autocomplete": "off",
                    "step": "1800",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        now = timezone.localtime()
        rounded_time = now.replace(second=0, microsecond=0)
        minutes_to_add = (-now.minute) % 30

        if minutes_to_add or now.second or now.microsecond:
            rounded_time += timedelta(minutes=minutes_to_add or 30)

        minimum_time = rounded_time.strftime("%Y-%m-%dT%H:%M")
        self.fields["start_time"].widget.attrs["min"] = minimum_time
        self.fields["end_time"].widget.attrs["min"] = minimum_time

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            start_date = timezone.localtime(start_time).date()
            end_date = timezone.localtime(end_time).date()

            if start_date != end_date:
                self.add_error(
                    "end_time",
                    "Vui lòng chọn giờ kết thúc trong cùng ngày.",
                )

        return cleaned_data


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)

        self.fields["username"].label = "Tên đăng nhập"
        self.fields["password"].label = "Mật khẩu"

        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Nhập tên đăng nhập",
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Nhập mật khẩu",
                "autocomplete": "current-password",
            }
        )


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = {
            "username": "Tên đăng nhập",
            "password1": "Mật khẩu",
            "password2": "Nhập lại mật khẩu",
        }
        placeholders = {
            "username": "Nhập tên đăng nhập",
            "password1": "Nhập mật khẩu",
            "password2": "Nhập lại mật khẩu",
        }
        autocomplete = {
            "username": "username",
            "password1": "new-password",
            "password2": "new-password",
        }

        for name, field in self.fields.items():
            field.label = labels.get(name, field.label)
            field.help_text = None
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": placeholders.get(name, ""),
                    "autocomplete": autocomplete.get(name, "off"),
                }
            )
