from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm, UserRgistrationForm
from django.contrib.auth.models import User


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
    template_name = "account/dashboard.html"
    context = {}
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
        template_name = "account/register_done.html"
        context = {
            "new_user": new_user,
            "username": user_form.cleaned_data.get("username"),
        }
        return render(request, template_name, context)
    else:
        print(user_form.errors)

    template_name = "account/register.html"
    context = {"user_form": user_form}
    return render(request, template_name, context)
