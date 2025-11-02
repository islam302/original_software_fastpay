from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    UserDetailsView,
    
)
from django.conf import settings
from django.urls import include, path

from .views import CustomLoginView

app_name = "authentication"


urlpatterns = [
    path("auth/token", CustomLoginView.as_view(), name="rest_login"),
    path("auth/login/", LoginView.as_view(), name="rest_login"),
    
    # URLs that require a user to be logged in with a valid session / token.
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
]


if getattr(settings, "REST_USE_JWT", False):
    from dj_rest_auth.jwt_auth import get_refresh_view
    from rest_framework_simplejwt.views import TokenVerifyView

    urlpatterns += [
        path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
        path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    ]
