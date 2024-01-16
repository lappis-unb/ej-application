import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model


User = get_user_model()
log = logging.getLogger("ej")


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):

        user = sociallogin.user
        if user.id:
            return
        if not user.email:
            return

        try:
            user = User.objects.get(email=user.email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
        except Exception as e:
            log.exception("Social adapter failure - {}".format(e))
