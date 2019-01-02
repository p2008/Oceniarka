from django.contrib import admin
from .models import Coordinator, Topic, Document
# Register your models here.

admin.site.register(Topic)
admin.site.register(Document)


def topics(obj):
    return [x.name for x in obj.topic.all()]


@admin.register(Coordinator)
class ProductAdmin(admin.ModelAdmin):
    list_display = (Coordinator.username, Coordinator.name, topics,)



