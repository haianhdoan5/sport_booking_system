from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Field(models.Model):
    class Type(models.TextChoices):
        BADMINTON = "BADMINTON", "Sân Cầu Lông"
        FOOTBALL = "FOOTBALL", "Sân Bóng Đá"

    name = models.CharField(
        max_length=100,
        verbose_name="Tên sân",
    )

    field_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.BADMINTON,
        verbose_name="Loại sân",
    )

    price_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Giá theo giờ",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Trạng thái hoạt động",
    )

    def __str__(self):
        return f"{self.name} - {self.get_field_type_display()}"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Chờ xác nhận"
        CONFIRMED = "CONFIRMED", "Đã đặt thành công"
        CANCELLED = "CANCELLED", "Đã hủy"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Khách hàng",
    )

    field = models.ForeignKey(
        Field,
        on_delete=models.PROTECT,
        verbose_name="Sân thể thao",
    )

    start_time = models.DateTimeField(
        verbose_name="Giờ bắt đầu",
    )

    end_time = models.DateTimeField(
        verbose_name="Giờ kết thúc",
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Tổng tiền",
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Trạng thái",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo đơn",
    )

    def clean(self):
        super().clean()

        if not self.start_time or not self.end_time:
            return

        if self.start_time >= self.end_time:
            raise ValidationError("Thời gian kết thúc phải lớn hơn thời gian bắt đầu.")

        # Chỉ kiểm tra thời gian quá khứ khi tạo booking mới.
        if self._state.adding and self.start_time < timezone.now():
            raise ValidationError("Không thể đặt sân trong quá khứ.")

        if not self.field_id:
            return

        # Chỉ chặn sân ngừng hoạt động khi tạo booking mới.
        # Booking cũ vẫn có thể được cập nhật trạng thái.
        if self._state.adding and not self.field.is_active:
            raise ValidationError("Sân này hiện đang tạm ngưng nhận đặt lịch.")

        # Booking đã hủy không cần kiểm tra trùng lịch.
        active_statuses = [
            self.Status.PENDING,
            self.Status.CONFIRMED,
        ]

        if self.status not in active_statuses:
            return

        overlapping_bookings = Booking.objects.filter(
            field_id=self.field_id,
            status__in=active_statuses,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )

        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError("Sân đã có người đặt trong khung giờ bạn chọn.")

    def calculate_total_price(self):
        duration = self.end_time - self.start_time

        duration_seconds = Decimal(str(duration.total_seconds()))

        hours = duration_seconds / Decimal("3600")

        return (self.field.price_per_hour * hours).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def save(self, *args, **kwargs):
        # Kiểm tra dữ liệu trước khi tính tiền.
        self.full_clean(exclude=["total_price"])

        if self.start_time and self.end_time and self.field_id:
            self.total_price = self.calculate_total_price()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Đơn đặt {self.field.name} - "
            f"{self.start_time.strftime('%H:%M %d/%m/%Y')}"
        )
