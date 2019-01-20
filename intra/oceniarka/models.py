from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Document(models.Model):
    coordinator = models.ForeignKey('Coordinator', on_delete=models.CASCADE,
                                    related_name='documents')
    inspector = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='documents')
    control_id = models.BigIntegerField(null=False, default=-1)
    control_number = models.CharField(max_length=4)
    control_year = models.PositiveSmallIntegerField()
    document_type = models.CharField(max_length=4)  # ZK, NK ...
    # dwa poniższe pola mają określać czy checkbox dla dec/ws jest zaznaczony
    # ma to służyć do sprawdzenia przy porównaniu z bazą produkcyjną, czy wpis jest zgodny z oczekiwaniami koordynatora
    field_type = models.CharField(max_length=32)  # Przenieść do innej tabeli lub usunąć
    field_current_value = models.CharField(max_length=32)  # Przenieść do innej tabeli lub traktować jako długi string z nazwami pól, np. dla dokumentu NK dec1T, dec2F
    is_evaluated = models.BooleanField(default=False)
    evaluation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Ip: {self.inspector} k: {self.document_type}'


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


class Topic(models.Model):
    name = models.CharField(max_length=4)
    year = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Email(models.Model):
    email_from = models.EmailField()
    email_to = models.EmailField()
    email_message = models.TextField()


# Outer database models


class ControlTopic(models.Model):
    kontrola = models.ForeignKey('Control', on_delete=models.CASCADE,
                                related_name='control_topics', db_column='kontrola')
    temat = models.CharField(max_length=4)                      # ControlTopic.kontrola == Control.id

    class Meta:
        db_table = 'kontrola_tematy'
        managed = False


class Control(models.Model):
    typ_dok = models.CharField(max_length=2, null=False)
    rok = models.PositiveSmallIntegerField(null=None)
    nr_prac = models.PositiveSmallIntegerField(null=None)
    id_kont = models.PositiveSmallIntegerField(null=None)
    data_kont = models.DateField(null=False)
    regon = models.CharField(max_length=14, null=False)

    class Meta:
        db_table = 'kontrole'
        managed = False
