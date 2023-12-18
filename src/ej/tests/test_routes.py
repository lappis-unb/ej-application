from constance import config
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from ej import routes
from ej.testing import UrlTester
import pytest


class TestBasicUrls(UrlTester):
    # Urls visible to every one (even without login)
    public_urls = ["/login/"]


class TestViews:
    def test_index_route_logged_user(self, rf, db, user):
        request = rf.get("", {})
        user.save()
        request.user = user
        response = routes.index(request)
        assert response.status_code == 302
        assert response.url == reverse("profile:home")

    @pytest.mark.django_db
    def test_index_anonymous_user(self, rf):
        request = rf.get("", {})
        request.user = AnonymousUser()
        response = routes.index(request)
        assert response.status_code == 302
        assert response.url == config.EJ_LANDING_PAGE_DOMAIN
