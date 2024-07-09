from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q


from ej_profiles.models import Profile
from ej_users.serializers import UserAuthSerializer, UsersSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from dataclasses import dataclass
from typing import Any


@dataclass
class EJTokens:
    """
    Manage EJ API authentication tokens.
    """

    user: Any
    access_token: str = ""
    refresh_token: str = ""
    data = {}

    def __post_init__(self):
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)
        self.data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }


class TokenViewSet(viewsets.ViewSet):
    serializer_class = UserAuthSerializer

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        # TODO: migrates all EJ API clients to token/token_refresh endpoints.
        return self.token(request)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="refresh-token",
    )
    def refresh_token(self, request):
        view = TokenRefreshView()
        view.request = request
        view.format_kwarg = "json"
        return view.post(request)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def token(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            if request.data.get("secret_id"):
                user = User.objects.get(
                    Q(email=request.data["email"])
                    | Q(secret_id=request.data.get("secret_id"))
                )
            else:
                user = User.objects.get(email=request.data["email"])
        except User.DoesNotExist:
            return Response({"error": _("User was not found.")}, status=500)

        checked_password = user.check_password(
            request.data["password"]
        ) or user.check_password(user.get_dummy_password())

        if not checked_password:
            return Response({"error": _("The password is incorrect")}, status=400)

        try:
            tokens = EJTokens(user)
            return Response(tokens.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    permission_classes_by_action = {
        "create": [AllowAny],
        "update": [AllowAny],
        "list": [IsAdminUser],
    }

    def update(self, request, pk=None):
        try:
            if pk.isdigit():
                user = User.objects.get(id=pk)
            else:
                user = User.objects.get(secret_id=pk)
        except User.DoesNotExist as e:
            return Response({"error": str(e)}, status=404)

        email = request.data.get("email")
        main_user_exists = User.objects.filter(email=email).exists()
        if user and main_user_exists:
            main_user = User.objects.get(email=email)
            if user.secret_id:
                main_user.secret_id = user.secret_id
                main_user.set_password(user.get_dummy_password())
                main_user = User.objects._convert_anonymous_participation_to_regular_user(
                    user, main_user
                )
                main_user.save()
            else:
                user.email = email
                user.save()

        return Response({"status": "ok"}, status=200)

    def create(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.save()
        self.check_profile(user, request)
        tokens = EJTokens(user)
        response = {"id": user.id, "name": user.name, "email": user.email, **tokens.data}
        return Response(response, status=201)

    def check_profile(self, user, request):
        phone_number = request.data.get("phone_number", None)
        profile, _ = Profile.objects.get_or_create(user=user)

        if phone_number:
            profile.phone_number = phone_number
            profile.save()

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]
