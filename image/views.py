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
from actions.utils import create_action
import redis
from django.conf import settings

# Connect to redis
r = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
)


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
            create_action(request.user, "bookmarked image", new_item)
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
    # increment total image views by 1
    total_views = r.incr(f"image:{image.id}:views")
    # increment image ranking by 1
    r.zincrby("image_ranking", 1, image.id)
    user = request.user
    context = {
        "image": image,
        "user": user,
        "total_views": total_views,
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
                create_action(request.user, "likes", image)
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
    images = Image.objects.order_by("-total_likes")
    paginator = Paginator(images, 6)
    page = request.GET.get("page")
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
def image_ranking(request):
    # Get image ranking dictionary
    image_ranking = r.zrange("image_ranking", 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # get most viewe images
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    template_name = "images/image/ranking.html"
    context = {
        "section": "images",
        "most_viewed": most_viewed,
    }
    return render(request, template_name, context)
