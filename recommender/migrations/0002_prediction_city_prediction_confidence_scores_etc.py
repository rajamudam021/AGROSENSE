from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prediction',
            name='city',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='prediction',
            name='confidence_scores',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='prediction',
            name='soil_health_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='prediction',
            name='land_size',
            field=models.FloatField(blank=True, help_text='Land size in acres', null=True),
        ),
        migrations.AddField(
            model_name='prediction',
            name='top2_crop',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='prediction',
            name='top3_crop',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
