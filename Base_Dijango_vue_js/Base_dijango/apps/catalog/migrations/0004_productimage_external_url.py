import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0003_alter_stockmovement_kind")]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=models.FileField(
                blank=True,
                upload_to="products/%Y/%m/",
                validators=[
                    django.core.validators.FileExtensionValidator(["jpg", "jpeg", "png", "webp"])
                ],
            ),
        ),
        migrations.AddField(
            model_name="productimage",
            name="external_url",
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
