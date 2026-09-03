from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
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


class FieldBrowsingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.badminton_field = Field.objects.create(
            name="Sân cầu lông Trung Tâm",
            field_type=Field.Type.BADMINTON,
            address="Quận 3, TP. Hồ Chí Minh",
            description="Sân cầu lông trong nhà.",
            price_per_hour=Decimal("120000"),
        )
        cls.pickleball_field = Field.objects.create(
            name="Pickleball Thủ Đức",
            field_type=Field.Type.PICKLEBALL,
            address="TP. Thủ Đức, TP. Hồ Chí Minh",
            description="Cụm sân pickleball có mái che.",
            price_per_hour=Decimal("160000"),
        )
        cls.inactive_field = Field.objects.create(
            name="Sân đang bảo trì",
            field_type=Field.Type.BADMINTON,
            address="Quận 7, TP. Hồ Chí Minh",
            price_per_hour=Decimal("90000"),
            is_active=False,
        )

    def test_home_searches_name_address_and_description(self):
        response = self.client.get(reverse("home"), {"q": "Thủ Đức"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["fields"]), [self.pickleball_field])
        self.assertEqual(response.context["query"], "Thủ Đức")

    def test_home_filters_by_field_type(self):
        response = self.client.get(reverse("home"), {"type": Field.Type.BADMINTON})

        self.assertEqual(list(response.context["fields"]), [self.badminton_field])
        self.assertEqual(response.context["selected_type"], Field.Type.BADMINTON)

    def test_home_combines_search_and_type_filter(self):
        response = self.client.get(
            reverse("home"),
            {"q": "sân", "type": Field.Type.PICKLEBALL},
        )

        self.assertEqual(list(response.context["fields"]), [self.pickleball_field])

    def test_home_ignores_unknown_type_and_excludes_inactive_fields(self):
        response = self.client.get(reverse("home"), {"type": "FOOTBALL"})

        self.assertEqual(
            list(response.context["fields"]),
            [self.badminton_field, self.pickleball_field],
        )
        self.assertEqual(response.context["selected_type"], "")
        self.assertNotContains(response, self.inactive_field.name)

    def test_active_field_detail_is_available(self):
        response = self.client.get(reverse("field_detail", args=[self.badminton_field.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/field_detail.html")
        self.assertEqual(response.context["field"], self.badminton_field)

    def test_inactive_field_detail_returns_not_found(self):
        response = self.client.get(reverse("field_detail", args=[self.inactive_field.id]))

        self.assertEqual(response.status_code, 404)
