from django.shortcuts import redirect
from django.urls import reverse


class AdminSuperuserRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin"):
            if not request.user.is_authenticated:
                login_url = reverse("login")
                return redirect(f"{login_url}?next={request.path}")
            if not request.user.is_superuser:
                return redirect("home")

        return self.get_response(request)
