from dj_rest_auth.views import UserDetailsView
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from dj_rest_auth.views import LoginView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

UserDetailsView.__doc__ = """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name, birth_date, gender, total_balance, buy_margin, sell_margin
    Default display fields: pk, username, email, first_name, last_name, birth_date, gender, total_balance, buy_margin, sell_margin
    Read-only fields: pk, email

    Returns UserModel fields.
    """

class CustomLoginView(LoginView):
    
    def get_response(self):
        user = self.user  # Get the authenticated user
        refresh = RefreshToken.for_user(user)  # Generate refresh and access tokens

        return Response({
            "token_type": "Bearer",
            "expires_in": 86400,  # Example: 24 hours (adjust as needed)
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        })
