from ej_users.models import User
from ej_conversations.tests.conftest import API_V1_URL
from rest_framework.test import APIClient
from enum import Enum
import json


class UserType(Enum):
    ANONYMOUS = "anonymous"
    AUTH = "auth"


class UserFake:
    USERS = {
        UserType.ANONYMOUS: {
            "name": "anonymous user",
            "email": "anonymous@mail.com",
            "password": "pass123",
            "password_confirm": "pass123",
        },
        UserType.AUTH: {
            "name": "Giovanni Giampauli",
            "email": "giovanni@mail.com",
            "password": "pass123@123",
            "password_confirm": "pass123@123",
        },
    }


class EJRequests:
    def __init__(self, client):
        self.client = client

    def get_token(self, user_type: UserType, secret_id=None):
        user = UserFake.USERS[user_type]
        data = {
            "email": user["email"],
            "password": user["password"],
        }

        if secret_id:
            data["secret_id"] = secret_id

        response = self.client.post(
            API_V1_URL + "/login/",
            data=data,
            content_type="application/json",
        )
        response_data = response.json()
        return response_data["access_token"]

    def create_user(self, user_type: UserType, secret_id=None):
        user = UserFake.USERS[user_type]
        data = user

        if secret_id:
            data["secret_id"] = secret_id

        response = self.client.post(
            API_V1_URL + "/users/",
            data=data,
            content_type="application/json",
        )

        return response

    def get_user(self, user_type: UserType, token):
        user = UserFake.USERS[user_type]
        email = user["email"]
        response = self.client.get(
            API_V1_URL + f"/users/{email}/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        return response

    def update_user(self, user_type: UserType, secret_id, token):
        user = UserFake.USERS[user_type]
        data = {"email": user["email"]}

        response = self.client.put(
            API_V1_URL + f"/users/{secret_id}/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        return response

    def delete_user(self, email, token):
        response = self.client.delete(
            API_V1_URL + f"/users/{email}/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        return response

    def get_users(self, token):
        response = self.client.get(
            API_V1_URL + "/users/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        return response


class TestUserAPI:
    def test_generate_access_token(self, db, user):
        api = APIClient()
        response = api.post(
            API_V1_URL + "/token/",
            {"email": user.email, "password": "password"},
            format="json",
        )
        data = response.json()
        assert response.status_code == 200
        assert data["access_token"]
        assert data["refresh_token"]

    def test_refresh_token(self, db, user):
        api = APIClient()
        response = api.post(
            API_V1_URL + "/token/",
            {"email": user.email, "password": "password"},
            format="json",
        )
        data = response.json()
        old_access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        response = api.post(
            API_V1_URL + "/refresh-token/",
            {"refresh": refresh_token},
            format="json",
        )
        data = response.json()
        assert data["access"]
        assert data["access"] != old_access_token

    def test_registration_auth_valid_user(self, client, db):
        client.post(
            API_V1_URL + "/users/",
            data={
                "name": "David Silva",
                "email": "david@example.com",
                "password": "pass123",
                "password_confirm": "pass123",
            },
            content_type="application/json",
        )
        user = User.objects.get(email="david@example.com")
        assert user.name == "David Silva"
        assert user.email == "david@example.com"

    def test_registration_rest_auth_incorrect_confirm_password(self, client, db):
        response = client.post(
            API_V1_URL + "/users/",
            data={
                "name": "jonatas Silva",
                "email": "jonatassilva@example.com",
                "password": "pass123",
                "password_confirm": "pass1234",
            },
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_registration_rest_auth_missing_password(self, client, db):
        response = client.post(
            API_V1_URL + "/users/",
            data={
                "name": "jonatas Silva",
                "email": "jonatasgomes@mail.com",
                "password_confirm": "pass123",
            },
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_user_endpoint_post_with_already_created_user(self, client, db):
        User.objects.create_user("user@user.com", "password")
        response = client.post(
            API_V1_URL + "/users/",
            data={
                "email": "user@user.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_get_token_after_user_registration(self, client, db):
        response = client.post(
            API_V1_URL + "/users/",
            data={
                "name": "tester",
                "email": "tester@example.com",
                "password": "pass123",
                "password_confirm": "pass123",
            },
            content_type="application/json",
        )
        assert response.json()["access_token"]
        assert response.status_code == 201

    def test_missing_credentials_in_login_should_return_error(self, client, db):
        User.objects.create_user("user@user.com", "password")
        response = client.post(
            API_V1_URL + "/users/",
            data={
                "email": "user@user.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 400

        response = client.post(
            API_V1_URL + "/login/",
            data={"password": "password"},
            content_type="application/json",
        )
        assert response.status_code == 400

        response = client.post(
            API_V1_URL + "/login/",
            data={"email": "user@user.com", "password": ""},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_get_token_after_user_login(self, client, db):
        User.objects.create_user("user@user.com", "password")
        response = client.post(
            "/api/v1/login/",
            data={"email": "user@user.com", "password": "password"},
            content_type="application/json",
        )

        assert response.json()["access_token"]
        assert response.status_code == 200

    def test_create_user_with_secret_id(self, client, db):
        ej_requests = EJRequests(client)
        SECRET_ID = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"

        response = ej_requests.create_user(UserType.AUTH, secret_id=SECRET_ID)
        assert response.status_code == 201

        user = User.objects.get(email=UserFake.USERS[UserType.AUTH]["email"])
        assert user.name == UserFake.USERS[UserType.AUTH]["name"]
        assert user.email == UserFake.USERS[UserType.AUTH]["email"]
        assert user.secret_id == SECRET_ID

    def test_create_auth_user(self, client, db):
        ej_requests = EJRequests(client)
        SECRET_ID = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"

        # Create anonymous user
        response = ej_requests.create_user(UserType.ANONYMOUS, secret_id=SECRET_ID)
        assert response.status_code == 201

        # Create auth user
        response = ej_requests.create_user(UserType.AUTH)
        assert response.status_code == 201

        access_token = ej_requests.get_token(UserType.AUTH)

        # Link secret_id to auth user
        response = ej_requests.update_user(
            SECRET_ID, access_token, {"email": UserFake.USERS[UserType.AUTH]["email"]}
        )
        assert response.status_code == 200

        user = User.objects.get(secret_id=SECRET_ID)
        assert user.name == UserFake.USERS[UserType.AUTH]["name"]
        assert user.email == UserFake.USERS[UserType.AUTH]["email"]
        assert user.secret_id == SECRET_ID

        user = User.objects.get(email=UserFake.USERS[UserType.AUTH]["email"])
        assert user.name == UserFake.USERS[UserType.AUTH]["name"]
        assert user.email == UserFake.USERS[UserType.AUTH]["email"]
        assert user.secret_id == SECRET_ID

        user = None
        try:
            user = User.objects.get(email=UserFake.USERS[UserType.ANONYMOUS]["email"])
        except User.DoesNotExist:
            pass
        assert user is None

    def test_get_token_by_secret_id(self, client, db):
        ej_requests = EJRequests(client)
        SECRET_ID = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"

        response = ej_requests.create_user(UserType.ANONYMOUS, secret_id=SECRET_ID)
        assert response.status_code == 201

        access_token = ej_requests.get_token(UserType.ANONYMOUS, secret_id=SECRET_ID)
        assert access_token

    def test_get_token_by_secret_id_after_link(self, client, db):
        ej_requests = EJRequests(client)
        SECRET_ID = "123456"

        response = ej_requests.create_user(UserType.ANONYMOUS, secret_id=SECRET_ID)
        assert response.status_code == 201

        access_token = ej_requests.get_token(UserType.ANONYMOUS, secret_id=SECRET_ID)
        assert access_token
