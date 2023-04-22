from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .forms import ImageCreateForm
from .models import Image


@login_required
def image_create(request):
    if request.method == "POST":
        # form is sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            # Assign the current user to the image
            new_item.user = request.user
            new_item.save()
            messages.success(request, "Image added successfully")

            # redirect to the newly created item details
            return redirect(new_item.get_absolute_url())
        else:
            print("There was an error ")
    else:
        # build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)

    template_name = "images/image/create.html"
    context = {
        "form": form,
    }
    return render(request, template_name, context)


@login_required
def image_detail(request, slug):
    image = get_object_or_404(Image, slug=slug)
    user = request.user
    context = {
        "image": image,
        "user": user,
    }
    template_name = "images/image/details.html"
    return render(request, template_name, context)