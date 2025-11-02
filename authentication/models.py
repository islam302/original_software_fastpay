from crum import get_current_user
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
import uuid


class UserStampedModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="created_by",
        related_name="%(class)ss_created_by",
        related_query_name="%(class)s_created_by",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="updated_by",
        related_name="%(class)ss_updated_by",
        related_query_name="%(class)s_updated_by",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.created_by = user
        self.updated_by = user
        super().save(*args, **kwargs)


class User(AbstractUser, TimeStampedModel, UserStampedModel):
    client_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client_secret = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super().save(force_insert, force_update, *args, **kwargs)
