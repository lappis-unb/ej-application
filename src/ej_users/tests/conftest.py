import pytest

from ej.tests.pytest.conftest import patch_jinja2
from ej_users.models import User


@pytest.fixture
def user(db):
    user = User.objects.create_user("email@server.com", "password")
    user.board_name = "testboard"

    # TODO: Fix this dirty way to set user permissions
    user.has_perm = lambda x, y=None: True

    user.save()
    return user


@pytest.fixture
def another_user(db):
    user = User.objects.create_user("anotheruser@server.com", "password")
    user.board_name = "testboard"

    # TODO: Fix this dirty way to set user permissions
    user.has_perm = lambda x, y=None: True

    user.save()
    return user


patch_jinja2()
