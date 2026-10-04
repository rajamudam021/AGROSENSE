from django.db import migrations, models


class Migration(migrations.Migration):
    """Add database indexes for fast query filtering on user and date."""

    dependencies = [
        ('recommender', '0002_prediction_city_prediction_confidence_scores_etc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
