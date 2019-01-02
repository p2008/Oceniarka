# Generated by Django 2.1.3 on 2019-01-02 16:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coordinator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('inspector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coordinators', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('control_number', models.CharField(max_length=4)),
                ('control_year', models.PositiveSmallIntegerField(max_length=4)),
                ('document_type', models.CharField(max_length=4)),
                ('field_type', models.CharField(max_length=32)),
                ('field_current_value', models.CharField(max_length=32)),
                ('is_evaluated', models.BooleanField(default=False)),
                ('evaluation_date', models.DateTimeField(auto_now_add=True)),
                ('coordinator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='oceniarka.Coordinator')),
                ('inspector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4)),
                ('year', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='coordinator',
            name='topic',
            field=models.ManyToManyField(related_name='coordinators', to='oceniarka.Topic'),
        ),
    ]
