from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("engagement", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="voucher",
            name="required_points",
            field=models.PositiveIntegerField(default=0),
        )
    ]
