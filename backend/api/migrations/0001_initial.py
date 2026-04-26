"""
Initial migration for ELD API models
"""

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('license_number', models.CharField(max_length=50, unique=True)),
                ('current_location', models.CharField(default='Unknown', max_length=255)),
                ('cycle_hours_used', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0)])),
                ('cycle_start', models.DateTimeField(auto_now_add=True)),
                ('violations_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_location', models.CharField(max_length=255)),
                ('pickup_location', models.CharField(max_length=255)),
                ('dropoff_location', models.CharField(max_length=255)),
                ('distance_miles', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')],
                    default='PENDING',
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trips', to='api.driver')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ELDLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_date', models.DateField()),
                ('events_json', models.JSONField(default=list)),
                ('total_driving_minutes', models.IntegerField(default=0)),
                ('total_on_duty_minutes', models.IntegerField(default=0)),
                ('total_miles', models.FloatField(default=0.0)),
                ('violations', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='api.driver')),
                ('trip', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='api.trip')),
            ],
            options={
                'ordering': ['-log_date'],
                'unique_together': {('driver', 'log_date')},
            },
        ),
    ]
