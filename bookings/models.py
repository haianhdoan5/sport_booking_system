from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Field(models.Model):
    FIELD_TYPES = [
        ("BADMINTON", "Sân Cầu Lông"),
        ("FOOTBALL", "Sân Bóng Đá"),
    ]
    name = models.CharField(max_length=100, verbose_name="Tên sân")
    field_type = models.CharField(
        max_length=20, choices=FIELD_TYPES, default="BADMINTON", verbose_name="Loại sân"
    )
    price_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Giá theo giờ"
    )
    is_active = models.BooleanField(default=True, verbose_name="Trạng thái hoạt động")

    def __str__(self):
        return f"{self.name} - {self.get_field_type_display()}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Chờ xác nhận"),
        ("CONFIRMED", "Đã đặt thành công"),
        ("CANCELLED", "Đã hủy"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Khách hàng")
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, verbose_name="Sân thể thao"
    )
    start_time = models.DateTimeField(verbose_name="Giờ bắt đầu")
    end_time = models.DateTimeField(verbose_name="Giờ kết thúc")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Tổng tiền"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Trạng thái",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo đơn")

    def clean(self):
        # 1. Kiểm tra thời gian logic
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(
                    "Thời gian kết thúc phải lớn hơn thời gian bắt đầu!"
                )

            if self.start_time < timezone.now():
                raise ValidationError("Không thể đặt sân trong quá khứ!")

            # 2. Thuật toán kiểm tra trùng lịch đặt sân
            # Dùng trực tiếp field_id để hệ thống không bị lỗi nếu form chưa load xong sân
            if self.field_id is not None:
                checking_status = ["PENDING", "CONFIRMED"]

                # Biến overlapping_bookings được tạo bên trong lệnh if
                overlapping_bookings = Booking.objects.filter(
                    field_id=self.field_id, status__in=checking_status
                ).filter(
                    models.Q(start_time__lt=self.end_time)
                    & models.Q(end_time__gt=self.start_time)
                )

                if self.pk:
                    overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)

                # Kiểm tra exists() cũng nằm GỌN BÊN TRONG lệnh if này
                if overlapping_bookings.exists():
                    raise ValidationError(
                        "Rất tiếc! Sân này đã có người đặt trong khung giờ bạn chọn."
                    )

    def save(self, *args, **kwargs):
        self.full_clean()

        # 3. Tự động tính tổng tiền
        times = self.end_time - self.start_time
        times_bookings = times.total_seconds() / 3600.0  # Chuyển từ giây sang giờ
        self.total_price = models.DecimalField(max_digits=10, decimal_places=2)
        self.total_price = float(self.field.price_per_hour) * times_bookings

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Đơn đặt {self.field.name} - {self.start_time.strftime('%H:%M %d/%m')}"
