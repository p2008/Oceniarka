# Generated by Django 2.1.3 on 2019-01-02 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oceniarka', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='control_year',
            field=models.PositiveSmallIntegerField(),
        ),
    ]