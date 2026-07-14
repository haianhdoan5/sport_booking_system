from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["start_time", "end_time"]  # Khách chỉ cần nhập 2 ô này
        # Chuyển ô nhập liệu thành dạng chọn Ngày - Giờ
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
        }


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        help_texts = {
            "username": "",
            "password1": "",
            "password2": "",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
