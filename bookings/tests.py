from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Booking, Field


class BookingModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="customer", password="Test@12345")
        self.field = Field.objects.create(
            name="Sân cầu lông A1",
            field_type=Field.Type.BADMINTON,
            address="Quận 1, TP. Hồ Chí Minh",
            price_per_hour=Decimal("120000"),
        )
        self.start_time = timezone.now() + timedelta(days=1)

    def test_project_supports_only_two_field_types(self):
        self.assertEqual(
            set(Field.Type.values),
            {Field.Type.BADMINTON, Field.Type.PICKLEBALL},
        )

    def test_booking_calculates_price_for_one_and_a_half_hours(self):
        booking = Booking.objects.create(
            user=self.user,
            field=self.field,
            start_time=self.start_time,
            end_time=self.start_time + timedelta(minutes=90),
        )

        self.assertEqual(booking.total_price, Decimal("180000.00"))
        self.assertTrue(booking.booking_code.startswith("BK-"))

    def test_booking_rejects_end_time_before_start_time(self):
        booking = Booking(
            user=self.user,
            field=self.field,
            start_time=self.start_time,
            end_time=self.start_time - timedelta(minutes=30),
        )

        with self.assertRaises(ValidationError):
            booking.save()

    def test_booking_rejects_overlapping_time(self):
        Booking.objects.create(
            user=self.user,
            field=self.field,
            start_time=self.start_time,
            end_time=self.start_time + timedelta(hours=1),
        )

        overlapping_booking = Booking(
            user=self.user,
            field=self.field,
            start_time=self.start_time + timedelta(minutes=30),
            end_time=self.start_time + timedelta(minutes=90),
        )

        with self.assertRaises(ValidationError):
            overlapping_booking.save()

    def test_booking_allows_adjacent_time(self):
        Booking.objects.create(
            user=self.user,
            field=self.field,
            start_time=self.start_time,
            end_time=self.start_time + timedelta(hours=1),
        )

        adjacent_booking = Booking.objects.create(
            user=self.user,
            field=self.field,
            start_time=self.start_time + timedelta(hours=1),
            end_time=self.start_time + timedelta(hours=2),
        )

        self.assertIsNotNone(adjacent_booking.pk)

    def test_booking_rejects_inactive_field(self):
        self.field.is_active = False
        self.field.save(update_fields=["is_active"])
        booking = Booking(
            user=self.user,
            field=self.field,
            start_time=self.start_time,
            end_time=self.start_time + timedelta(hours=1),
        )

        with self.assertRaises(ValidationError):
            booking.save()
