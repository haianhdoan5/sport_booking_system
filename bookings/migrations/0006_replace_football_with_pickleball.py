from django.db import migrations, models


def replace_football_with_pickleball(apps, schema_editor):
    field_model = apps.get_model("bookings", "Field")
    field_model.objects.filter(field_type="FOOTBALL").update(field_type="PICKLEBALL")


def restore_football(apps, schema_editor):
    field_model = apps.get_model("bookings", "Field")
    field_model.objects.filter(field_type="PICKLEBALL").update(field_type="FOOTBALL")


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0005_review"),
    ]

    operations = [
        migrations.RunPython(replace_football_with_pickleball, restore_football),
        migrations.AlterField(
            model_name="field",
            name="field_type",
            field=models.CharField(
                choices=[
                    ("BADMINTON", "Sân Cầu Lông"),
                    ("PICKLEBALL", "Sân Pickleball"),
                ],
                default="BADMINTON",
                max_length=20,
                verbose_name="Loại sân",
            ),
        ),
    ]
