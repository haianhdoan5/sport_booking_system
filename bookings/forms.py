from django import forms

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
