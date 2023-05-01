from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .forms import LoginForm, UserRgistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from actions.utils import create_action
from actions.models import Action


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        # Get the user data from the form
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        # Get the user from the database
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponse("Authenticated Successfully")
            else:
                return HttpResponse("Disabled Account!")
        else:
            return HttpResponse("Invalid Login!")

    context = {
        "form": form,
    }
    template_name = "account/login.html"
    return render(request, template_name, context)


@login_required
def dashboard(request):
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list("id", flat=True)
    if following_ids:
        # if user is following others, retrieve only their actions
        actons = actions.filter(user_id__in=following_ids)
    actions = actions.select_related("user", "user__profile").prefetch_related(
        "target"
    )[:10]
    template_name = "account/dashboard.html"
    context = {
        "section": "dashboard",
        "actions": actions,
        "user": request.user,
    }
    return render(request, template_name, context)


def register(request):
    user_form = UserRgistrationForm(request.POST or None)
    if user_form.is_valid():
        # Create a new User object
        new_user = user_form.save(commit=False)
        # Set the chosen password
        password = user_form.cleaned_data.get("password")
        new_user.set_password(password)
        new_user.save()
        Profile.objects.create(user=new_user)
        template_name = "account/register_done.html"
        context = {
            "new_user": new_user,
            "username": user_form.cleaned_data.get("username"),
        }
        print("Creating activity stream ######################")
        create_action(new_user, "created account")
        return render(request, template_name, context)
    else:
        print(user_form.errors)

    template_name = "account/register.html"
    context = {"user_form": user_form}
    return render(request, template_name, context)


@login_required
def edit(request):
    user = request.user
    user_profile = Profile.objects.get(user=user)
    if request.method == "POST":
        user_form = UserEditForm(instance=user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=user_profile, data=request.POST, files=request.FILES
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            create_action(request.user, "edited their profile")

    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=user_profile)

    template_name = "account/edit.html"
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, template_name, context)


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    template_name = "account/user/list.html"
    context = {
        "section": "people",
        "users": users,
    }
    return render(request, template_name, context)


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    template_name = "account/user/detail.html"
    context = {
        "section": "people",
        "user": user,
        "total_followers": user.followers.count(),
    }
    return render(request, template_name, context)


@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get("id")
    action = request.POST.get("action")
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == "follow":
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user,
                )
                create_action(request.user, "following", user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                create_action(request.user, "stoped followig", user)
            return JsonResponse({"status": "ok"})
        except User.DoesNotExist:
            return JsonResponse({"status": "error"})
    return JsonResponse({"status": "error"})
