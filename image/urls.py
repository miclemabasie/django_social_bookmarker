from django.urls import path
from . import views

app_name = "image"

urlpatterns = [
    path("create/", views.image_create, name="create"),
    path("image/<slug:slug>/", views.image_detail, name="image_details"),
    path("like/", views.image_like, name="like"),
]
