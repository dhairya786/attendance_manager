# Generated by Django 3.2.3 on 2021-12-04 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('role', '0017_auto_20210930_0819'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendancepic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='attendance_pics/')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='role.teacher')),
            ],
        ),
    ]
