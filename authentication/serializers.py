from dj_rest_auth.serializers import PasswordResetSerializer, UserDetailsSerializer
        
from django.contrib.auth import authenticate, get_user_model
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model


# Get the UserModel
UserModel = get_user_model()


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta:
        extra_fields = []
        # see https://github.com/iMerica/dj-rest-auth/issues/181
        # UserModel.XYZ causing attribute error while importing other
        # classes from `serializers.py`. So, we need to check whether the auth model has
        # the attribute or not
        if hasattr(UserModel, "USERNAME_FIELD"):
            extra_fields.append(UserModel.USERNAME_FIELD)
        if hasattr(UserModel, "EMAIL_FIELD"):
            extra_fields.append(UserModel.EMAIL_FIELD)
        if hasattr(UserModel, "client_id"):
            extra_fields.append("client_id")
        if hasattr(UserModel, "client_secret"):
            extra_fields.append("client_secret")

        model = UserModel
        fields = ("pk", *extra_fields)

class CustomLoginSerializer(LoginSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    dashboard_login = serializers.BooleanField(required=False)
    client_id = serializers.CharField(required=True)
    client_secret = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        client_id = attrs.get("client_id")
        client_secret = attrs.get("client_secret")
        dashboard_login = attrs.get("dashboard_login")

        if not all([username, password, client_id, client_secret]):
            raise ValidationError("All fields (username, password, client_id, client_secret) are required.")

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if not user:
            raise ValidationError("Invalid username or password.")

        # Validate client_id and client_secret (Example: You might store these in the User model)
        if not (str(user.client_id == client_id) and str(user.client_secret) == client_secret) and not dashboard_login:
            raise ValidationError("Invalid client credentials.")

        attrs["user"] = user
        return attrs
    




