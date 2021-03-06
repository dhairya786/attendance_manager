# Generated by Django 3.2.3 on 2021-07-12 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('role', '0009_auto_20210709_0830'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('obtained', models.IntegerField()),
                ('total', models.IntegerField()),
                ('field', models.CharField(choices=[('LE1', 'LE1'), ('LE2', 'LE2'), ('LE3', 'LE3'), ('SES1', 'SES1'), ('SES2', 'SES2'), ('SES3', 'SES3'), ('MST', 'MST'), ('EST', 'EST')], max_length=30)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='role.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='role.student')),
            ],
        ),
    ]
