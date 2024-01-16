from boogie.configurations import InstalledAppsConf as Base, env

from .options import EjOptions


class InstalledAppsConf(Base, EjOptions):
    USE_DJANGO_ADMIN = env(True, name="{attr}")
    DISABLE_DJANGO_DEBUG_TOOLBAR = env(True, name="{attr}")

    project_apps = [
        "ej_boards",
        "ej_clusters",
        "ej_dataviz",
        "ej_profiles",
        "ej_conversations",
        "ej_tools",
        "ej_admin",
        "ej_activation",
    ]

    third_party_apps = [
        "boogie.apps.fragments",
        "taggit",
        "rules",
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
        "allauth.socialaccount.providers.google",
        "ej_users",
        "rest_framework",
        "rest_framework.authtoken",
        "dj_rest_auth",
        "corsheaders",
        "django.contrib.auth",
        "django.contrib.messages",
        "django.contrib.sites",
        "constance",
        "constance.backends.database",
        "anymail",
        "ckeditor",
    ]

    def get_django_contrib_apps(self):
        return [*super().get_django_contrib_apps(), "django.contrib.flatpages"]

    def get_project_apps(self):
        return [*super().get_project_apps(), *self.project_apps]

    def get_third_party_apps(self):
        apps = [*super().get_third_party_apps(), *self.third_party_apps]
        if self.ENVIRONMENT == "local":
            if not self.DISABLE_DJANGO_DEBUG_TOOLBAR:
                apps = ["debug_toolbar", *apps]

        elif self.DEBUG and not self.DISABLE_DJANGO_DEBUG_TOOLBAR:
            apps = ["debug_toolbar", *apps]
        if self.ENVIRONMENT == "production":
            apps = ["gunicorn", *apps]
        return apps
