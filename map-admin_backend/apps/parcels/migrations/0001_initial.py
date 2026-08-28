import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_location', models.CharField(max_length=255)),
                ('pickup_lat', models.FloatField()),
                ('pickup_lng', models.FloatField()),
                ('destination_location', models.CharField(max_length=255)),
                ('destination_lat', models.FloatField()),
                ('destination_lng', models.FloatField()),
                ('current_location', models.CharField(blank=True, max_length=255)),
                ('current_lat', models.FloatField(blank=True, null=True)),
                ('current_lng', models.FloatField(blank=True, null=True)),
                ('weight_category', models.CharField(max_length=20)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_transit', 'In Transit'), ('delivered', 'Delivered')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parcels', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
