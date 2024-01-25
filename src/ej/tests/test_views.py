import pytest
from constance import config
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.test import Client
from ej import views
from ej.testing import UrlTester
from ej_conversations.tests.test_views import ConversationSetup


class TestBasicUrls(UrlTester):
    # Urls visible to every one (even without login)
    public_urls = ["/login/"]


class TestViews(ConversationSetup):
    def test_index_route_logged_user(self, logged_admin):
        response = logged_admin.get(reverse("index"))
        assert response.status_code == 302
        assert response.url == reverse("profile:home")

    @pytest.mark.django_db
    def test_index_anonymous_user(self, rf):
        client = Client()
        response = client.get(reverse("index"))
        assert response.status_code == 302
        assert response.url == config.EJ_LANDING_PAGE_DOMAIN
