from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Action(models.Model):
    user = models.ForeignKey(
        "auth.User", related_name="actions", db_index=True, on_delete=models.CASCADE
    )
    # Describing the action the user takes
    verb = models.CharField(verbose_name=_("Verb"), max_length=255)

    target_ct = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="target_obj",
        on_delete=models.CASCADE,
    )

    target_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )
    target = GenericForeignKey("target_ct", "target_id")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"{self.user.username} did {self.verb}"
