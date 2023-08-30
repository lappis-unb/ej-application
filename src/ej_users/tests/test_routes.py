from ej.testing import UrlTester
from ej_users.mommy_recipes import UserRecipes


class TestRoutes(UserRecipes, UrlTester):
    public_urls = [
        "/register/",
        "/login/",
        "/recover-password/",
        # '/recover-password/<token>' -- requires special initialization
    ]
    user_urls = [
        "/account/",
        "/account/logout/",
        "/account/remove/",
        "/account/manage-email/",
        "/account/change-password/",
    ]
