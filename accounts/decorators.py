from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(role):
    """View decorator enforcing role-based access (SPEC §8).

    Requires the user to be logged in AND to have the given role
    ("candidate" or "employer"). A logged-in user with the wrong role gets a
    403 (PermissionDenied); an anonymous user is sent to the login page.
    Enforced server-side, so hiding a link in the template is not relied upon.
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role != role:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
