
import io

import filetype
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64FileField, Base64ImageField
from drf_yasg import openapi
from rest_framework import serializers


class Base64ImageField(Base64ImageField):
    """
    A django-rest-framework field for handling image-uploads through raw post data.
    It uses base64 for en-/decoding the contents of the file.
    """

    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_STRING,
            "title": "Image Content",
            "description": "Content of the base64 Image encoded",
            "read_only": False,  # <-- FIX
            "format": openapi.FORMAT_BASE64,
        }

    ALLOWED_TYPES = ("jpeg", "jpg", "png", "gif", "webp")
    INVALID_FILE_MESSAGE = _("Please upload a valid image.")
    INVALID_TYPE_MESSAGE = _("The type of the image couldn't be determined.")

    def get_file_extension(self, filename, decoded_file):
        extension = filetype.guess_extension(decoded_file)
        if extension is None:
            try:
                # Try with PIL as fallback if format not detected
                # with `filetype` module
                from PIL import Image

                image = Image.open(io.BytesIO(decoded_file))
            except (ImportError, OSError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)
            else:
                extension = image.format.lower()

        return "jpg" if extension == "jpeg" else extension