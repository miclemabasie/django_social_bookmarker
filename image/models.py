from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Image(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="images_created",
        on_delete=models.CASCADE,
    )
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    slug = models.SlugField(verbose_name=_("Slug"), max_length=200, blank=True)
    url = models.URLField(verbose_name=_("URL"))
    image = models.ImageField(upload_to="image/%Y/%m/%d/")
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    users_like = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="images_liked", blank=True
    )

    def __str__(self) -> str:
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("image:image_details", kwargs={"slug": self.slug})
