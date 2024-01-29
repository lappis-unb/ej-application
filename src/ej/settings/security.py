from sidekick import unique as _unique

from boogie.configurations import SecurityConf as Base, env


class SecurityConf(Base):
    INTERNAL_IPS = env([])
    AUTHENTICATION_BACKENDS = [
        "rules.permissions.ObjectPermissionBackend",
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    ]
    X_FRAME_OPTIONS = env("SAMEORIGIN")
    CONTENT_SECURITY_POLICY_FRAME_ANCESTORS = env([])  # TODO: deprecated
    CORS_ORIGIN_ALLOW_ALL = env(False)
    CORS_ALLOW_CREDENTIALS = env(False)

    # Configure HTTP headers
    HTTP_CONTENT_SECURITY_POLICY = env("", name="{attr}")
    HTTP_ACCESS_CONTROL_ALLOW_ORIGIN = env("", name="{attr}")
    HTTP_ACCESS_CONTROL_ALLOW_CREDENTIALS = env("", name="{attr}")
    HTTP_X_FRAME_OPTIONS = env("", name="{attr}")

    def finalize(self, settings):
        settings = super().finalize(settings)

        if self.ENVIRONMENT == "local":
            settings["INTERNAL_IPS"].append("127.0.0.1")
            settings["CORS_ORIGIN_ALLOW_ALL"] = True
        return settings


def remove_schema(url):
    _, _, hostname = url.partition("://")
    return hostname


def unique(data):
    return list(_unique(data))
