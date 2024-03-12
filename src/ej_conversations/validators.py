from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


FIVE_MB = 5242880


def is_not_empty(text):
    if not text.strip():
        raise ValidationError(_("Field cannot be empty!"))


def validate_file_size(value):
    """
    Validates image size in form to be less than 5MB.
    This method is above the class attributes as it was
    not possible to access the validator if it is below.
    """

    filesize = value.size

    if filesize > FIVE_MB:
        raise ValidationError(_("The maximum file size must be 5MB"))
    else:
        return value
