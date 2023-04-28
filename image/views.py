from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .forms import ImageCreateForm
from .models import Image
import time


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
                data["count"] = image.users_like.all().count()
            else:
                image.users_like.remove(request.user)
                print("subtract")
                data["count"] = image.users_like.all().count()
            data["status"] = "ok"
            return JsonResponse(data, safe=False)
        except:
            pass
    return JsonResponse({"status": "error"})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 3)
    page = request.GET.get("page")
    time.sleep(3)
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # if the request is ajax and the page is not of range
            # return an empty page
            return HttpResponse("")
        # if page is out of range deliver last page of results
    context = {"section": "images", "images": images}
    if request.is_ajax():
        template_name = "images/image/list_ajax.html"
        return render(request, template_name, context)
    template_name = "images/image/list.html"
    return render(request, template_name, context)


@login_required
def list_view(request):
    images = Image.objects.all()

    template_name = "images/image/list.html"
    context = {
        "images": images,
    }

    return render(request, template_name, context)
