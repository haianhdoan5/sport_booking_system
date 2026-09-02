from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking, Field


FIELDS = [
    {
        "name": "Sân cầu lông A1",
        "field_type": Field.Type.BADMINTON,
        "address": "Quận 1, TP. Hồ Chí Minh",
        "description": "Sân thảm tiêu chuẩn, ánh sáng tốt, phù hợp tập luyện và thi đấu.",
        "price_per_hour": Decimal("120000"),
    },
    {
        "name": "Sân cầu lông A2",
        "field_type": Field.Type.BADMINTON,
        "address": "Quận 3, TP. Hồ Chí Minh",
        "description": "Không gian thông thoáng, có khu vực nghỉ và gửi xe.",
        "price_per_hour": Decimal("110000"),
    },
    {
        "name": "Sân cầu lông A3",
        "field_type": Field.Type.BADMINTON,
        "address": "Quận 5, TP. Hồ Chí Minh",
        "description": "Sân trong nhà, hạn chế gió và có hệ thống chiếu sáng ổn định.",
        "price_per_hour": Decimal("100000"),
    },
    {
        "name": "Sân cầu lông A4",
        "field_type": Field.Type.BADMINTON,
        "address": "Quận 7, TP. Hồ Chí Minh",
        "description": "Mặt sân êm, khuôn viên sạch và có phòng thay đồ.",
        "price_per_hour": Decimal("130000"),
    },
    {
        "name": "Sân cầu lông A5",
        "field_type": Field.Type.BADMINTON,
        "address": "Quận Bình Thạnh, TP. Hồ Chí Minh",
        "description": "Sân dành cho nhóm bạn và câu lạc bộ, mở cửa cả ngày.",
        "price_per_hour": Decimal("115000"),
    },
    {
        "name": "Sân pickleball P1",
        "field_type": Field.Type.PICKLEBALL,
        "address": "Quận 2, TP. Hồ Chí Minh",
        "description": "Sân pickleball tiêu chuẩn với mặt sân chống trượt.",
        "price_per_hour": Decimal("150000"),
    },
    {
        "name": "Sân pickleball P2",
        "field_type": Field.Type.PICKLEBALL,
        "address": "Quận 4, TP. Hồ Chí Minh",
        "description": "Sân mới, hệ thống lưới và đèn chiếu sáng chất lượng cao.",
        "price_per_hour": Decimal("160000"),
    },
    {
        "name": "Sân pickleball P3",
        "field_type": Field.Type.PICKLEBALL,
        "address": "Quận 7, TP. Hồ Chí Minh",
        "description": "Không gian rộng, phù hợp luyện tập cá nhân và thi đấu đôi.",
        "price_per_hour": Decimal("170000"),
    },
    {
        "name": "Sân pickleball P4",
        "field_type": Field.Type.PICKLEBALL,
        "address": "Quận 10, TP. Hồ Chí Minh",
        "description": "Sân có mái che, khu vực chờ và bãi giữ xe thuận tiện.",
        "price_per_hour": Decimal("155000"),
    },
    {
        "name": "Sân pickleball P5",
        "field_type": Field.Type.PICKLEBALL,
        "address": "TP. Thủ Đức, TP. Hồ Chí Minh",
        "description": "Cụm sân hiện đại, phù hợp người mới chơi và câu lạc bộ.",
        "price_per_hour": Decimal("165000"),
    },
]


class Command(BaseCommand):
    help = "Tạo 10 sân cầu lông/pickleball và dữ liệu booking phục vụ demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-bookings",
            action="store_true",
            help="Tạo tài khoản demo và một số booking trong tương lai.",
        )

    def handle(self, *args, **options):
        fields = []

        for data in FIELDS:
            field, created = Field.objects.update_or_create(
                name=data["name"],
                defaults={**data, "is_active": True},
            )
            fields.append(field)
            action = "Tạo" if created else "Cập nhật"
            self.stdout.write(f"{action}: {field.name}")

        if options["with_bookings"]:
            self._create_bookings(fields)

        self.stdout.write(self.style.SUCCESS("Dữ liệu demo đã sẵn sàng."))

    def _create_bookings(self, fields):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username="demo")

        if created:
            user.set_password("Demo@12345")
            user.save(update_fields=["password"])
            self.stdout.write("Tạo tài khoản demo: demo / Demo@12345")

        tomorrow = timezone.localdate() + timedelta(days=1)
        slots = [
            (fields[0], time(8, 0), time(9, 0), Booking.Status.CONFIRMED),
            (fields[1], time(18, 0), time(19, 30), Booking.Status.PENDING),
            (fields[5], time(9, 0), time(10, 0), Booking.Status.CONFIRMED),
            (fields[6], time(19, 0), time(20, 0), Booking.Status.PENDING),
        ]

        for field, start_clock, end_clock, status in slots:
            start_time = timezone.make_aware(datetime.combine(tomorrow, start_clock))
            end_time = timezone.make_aware(datetime.combine(tomorrow, end_clock))
            booking, created = Booking.objects.get_or_create(
                user=user,
                field=field,
                start_time=start_time,
                end_time=end_time,
                defaults={"status": status, "note": "Dữ liệu phục vụ demo"},
            )
            action = "Tạo" if created else "Đã có"
            self.stdout.write(f"{action} booking: {booking.booking_code}")
