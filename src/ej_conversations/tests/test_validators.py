import pytest
from django.core.exceptions import ValidationError

from ..validators import FIVE_MB, validate_file_size


def test_utils_validator_invalid_file_size():
    test_file = type("FileMock", (object,), {"size": FIVE_MB + 1})()
    with pytest.raises(ValidationError):
        validate_file_size(test_file)


def test_utils_validator_valid_file_size():
    test_file = type("FileMock", (object,), {"size": FIVE_MB})()
    assert validate_file_size(test_file) == test_file
