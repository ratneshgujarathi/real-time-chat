from django.contrib import admin
from .models import NewMessage, Thread

# Register your models here.
admin.site.register(NewMessage)


class ChatMessage(admin.TabularInline):
    model = NewMessage


class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]

    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)
