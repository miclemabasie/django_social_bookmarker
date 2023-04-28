from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get("image_id")
    action = request.POST.get("action")
    data = {}
    if image_id and action:
        try:
            image = get_object_or_404(Image, id=image_id)
            if action == "like":
                image.users_like.add(request.user)
                print("Added")
                data['count'] = image.users_like.all().count()
            else:
                image.users_like.remove(request.user)
                print("subtract")
                data['count'] = image.users_like.all().count()
            data['status'] = "ok"
            return JsonResponse(data, safe=False)
        except:
            pass
    return JsonResponse({"status": "error"})


@login_required
def list_view(request):
    images = Image.objects.all()

    template_name = "images/image/list.html"
    context = {
        "images": images,
    }

    return render(request, template_name, context)
