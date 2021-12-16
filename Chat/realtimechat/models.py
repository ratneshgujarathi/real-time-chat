from django.db import models
from django.contrib.auth.models import User

import uuid
from django.contrib.auth import get_user_model
from django.db.models import Q

# Create your models here.


class message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="sender", null=True, blank=True
    )
    receipent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="received_messages",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    body = models.TextField()
    created_at = models.TimeField(auto_now_add=True)
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ["-is_read", "-created_at"]
        unique_together = ["sender", "receipent"]


user = get_user_model()

# Create your models here.


class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get("user")
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    first_person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="thread_first_person",
    )
    second_person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="thread_second_person",
    )
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ["first_person", "second_person"]


class NewMessage(models.Model):
    thread_id = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="thread_id",
    )
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_by")
    msg = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
