from django.contrib import admin

from chatapp.models import Message, Room, Topic

# Register your models here.
admin.site.register(Topic)
admin.site.register(Room)
admin.site.register(Message)