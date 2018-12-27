from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Document(models.Model):
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE,
                                    related_name='documents')
    inspector = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='documents')
    control_number = models.CharField(max_length=4)
    control_year = models.PositiveSmallIntegerField(max_length=4)
    document_type = models.CharField(max_length=4)
    field_type = models.CharField(max_length=32)
    field_current_value = models.CharField(max_length=32)
    evaluation_date = models.DateTimeField(auto_now_add=True)


class Coordinator(models.Model):
    inspector = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='coordinators')
    year = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    topic = models.ManyToManyField(Topic, related_name='coordinators')


class Topic(models.Model):
    name = models.CharField(max_length=4)
    year = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
