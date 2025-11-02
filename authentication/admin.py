from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    readonly_fields = ("client_id", "client_secret", "created",
                       "created_by", "modified", "updated_by")

    list_display = (
        "client_id", "client_secret",
        "username",
        "is_active",
        "is_staff",
        "is_superuser",

    )
    list_filter = ("is_active", "is_staff", "is_superuser")

    search_fields = ("email", "username")
    ordering = ("email", "username")

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Record Info",
            {"fields": ("client_id", "client_secret", "created",
                        "created_by", "modified", "updated_by")},
        ),
    )

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('username', 'email', 'password1', 'password2'),
    #     }),
    # )
