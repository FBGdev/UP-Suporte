from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def is_gestor(user):
    return user.is_authenticated and user.groups.filter(name="Gestor").exists()

def gestor_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.groups.filter(name="Gestor").exists():
            return redirect("home")
        return view_func(request, *args, **kwargs)

    return _wrapped
