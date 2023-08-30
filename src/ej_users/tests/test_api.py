from ej_users.models import User
from ej_users.mommy_recipes import UserRecipes


class TestUserAPI(UserRecipes):
    def test_registration_auth_valid_user(self, client, db):
        client.post(
            "/api/v1/users/",
            data={
                "name": "David Silva",
                "email": "david@example.com",
                "password": "pass123",
                "password_confirm": "pass123",
                "metadata": {"analytics_id": "GA.1.1234", "mautic_id": 123456},
            },
            content_type="application/json",
        )
        user = User.objects.get(email="david@example.com")
        assert user.metadata_set.first().analytics_id == "GA.1.1234"
        assert user.metadata_set.first().mautic_id == 123456

    def test_registration_rest_auth_valid_user(self, client, db):
        client.post(
            "/api/v1/users/",
            data={
                "name": "jonatas Silva",
                "email": "jonatas@example.com",
                "password": "pass123",
                "password_confirm": "pass123",
                "metadata": {"analytics_id": "GA.1.1234", "mautic_id": 123456},
            },
            content_type="application/json",
        )
        user = User.objects.get(email="jonatas@example.com")
        assert user.metadata_set.first().analytics_id == "GA.1.1234"
        assert user.metadata_set.first().mautic_id == 123456

    def test_registration_rest_auth_incorrect_confirm_password(self, client, db):
        response = client.post(
            "/api/v1/users/",
            data={
                "name": "jonatas Silva",
                "email": "jonatassilva@example.com",
                "password": "pass123",
                "password_confirm": "pass1234",
                "metadata": {"analytics_id": "GA.1.1234", "mautic_id": 123456},
            },
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_registration_rest_auth_missing_password(self, client, db):
        response = client.post(
            "/api/v1/users/",
            data={
                "name": "jonatas Silva",
                "email": "jonatasgomes@mail.com",
                "password_confirm": "pass123",
                "metadata": {"analytics_id": "GA.1.1234", "mautic_id": 123456},
            },
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_user_endpoint_post_with_already_created_user(self, client, db):
        User.objects.create_user("user@user.com", "password")
        response = client.post(
            "/api/v1/users/",
            data={
                "email": "user@user.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_get_token_after_user_registration(self, client, db):
        response = client.post(
            "/api/v1/users/",
            data={
                "name": "tester",
                "email": "tester@example.com",
                "password": "pass123",
                "password_confirm": "pass123",
            },
            content_type="application/json",
        )
        assert response.json()["token"]
        assert response.status_code == 200

    def test_missing_credentials_in_login_should_return_error(self, client, db):
        User.objects.create_user("user@user.com", "password")
        response = client.post(
            "/api/v1/login/",
            data={
                "email": "user@user.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 400

        response = client.post(
            "/api/v1/login/",
            data={"password": "password"},
            content_type="application/json",
        )
        assert response.status_code == 400

        response = client.post(
            "/api/v1/login/",
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

        assert response.json()["token"]
        assert response.status_code == 200
