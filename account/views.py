from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm


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
