from django.contrib.auth.models import User
from django.db import models
from .outer_models import Control, ControlTopic, OrderTopic, Order


# Create your models here.

class Document(models.Model):
    coordinator = models.ForeignKey('Coordinator', on_delete=models.CASCADE,
                                    related_name='documents')
    inspector = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='documents')
    control_id = models.DecimalField(max_digits=21, decimal_places=0, null=False, default=-1)
    control_number = models.CharField(max_length=4)
    control_year = models.PositiveSmallIntegerField()
    document_type = models.CharField(max_length=4)  # ZK, NK ...
    # dwa poniższe pola mają określać czy checkbox dla dec/ws jest zaznaczony
    # ma to służyć do sprawdzenia przy porównaniu z bazą produkcyjną, czy wpis jest zgodny z oczekiwaniami koordynatora
    field_type = models.CharField(max_length=32)  # Przenieść do innej tabeli lub usunąć
    field_current_value = models.CharField(
        max_length=32)  # Przenieść do innej tabeli lub traktować jako długi string z nazwami pól, np. dla dokumentu NK dec1T, dec2F
    is_evaluated = models.BooleanField(default=False, null=False)
    evaluation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Ip: {self.inspector} k: {self.control_number}'

    def control_list_name(self):
        return f'Kontrola { self.inspector }-{ self.control_number }'

    def eval_date(self):
        return f'{ self.evaluation_date.strftime("%m-%d-%Y %H:%M")}'


class Coordinator(models.Model):
    inspector = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='coordinators')
    year = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    topic = models.ManyToManyField('Topic', related_name='coordinators')

    def name(self):
        return f'{self.inspector.first_name} {self.inspector.last_name}'

    def username(self):
        return f'{self.inspector.username}'

    def coordinator_emails_from_db(self):
        return Email.objects.filter(email_from=self.inspector.email)


class Topic(models.Model):
    name = models.CharField(max_length=4)
    year = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Email(models.Model):
    email_from = models.EmailField()
    email_to = models.EmailField()
    control_number = models.CharField(max_length=4)
    email_message = models.TextField()
    email_topic = models.CharField(max_length=32)
