import logging

from boogie.apps.users.models import (
    UserManager as BaseUserManager,
    UserQuerySet as BaseUserQuerySet,
)

log = logging.getLogger("ej")


class UserQuerySet(BaseUserQuerySet):
    """
    User queryset.
    """


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    def get_by_email(self, value):
        """
        Return a user with the given e-mail.
        """
        return self.get(email=value)

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def create_user_from_session(self, session_key, email, password, **extra_fields):
        """
        creates a regular user and converts votes and comments from anonymous participant, if it exists.
        This method implements part of the behavior of anonymous participation conversation option.
        """
        user = self.create_user(email, password, **extra_fields)
        anonymous_user_query = self.filter(email=f"anonymoususer-{session_key}@mail.com")
        if anonymous_user_query.exists():
            try:
                anonymous_user = anonymous_user_query.first()
                self.merge_users(anonymous_user, user)
                log.info(f"anonymous user participation converted to {email} user")
            except Exception as e:
                log.error(f"Could not find anonymous user. Error: {e}")
        return user

    def merge_users(self, temporary_user, unique_user):
        """
        migrates temporary_user boards, conversations, votes and comments to unique_user.
        """
        temporary_user.boards.all().update(owner=unique_user)
        temporary_user.conversations.all().update(author=unique_user)
        unique_comments_ids = unique_user.votes.select_related("comment").values_list(
            "comment__id"
        )
        # removes votes from temporary_user that also exists in unique_user.
        temporary_user.votes.filter(comment__id__in=unique_comments_ids).delete()
        temporary_user.votes.all().update(author=unique_user)
        temporary_user.comments.all().update(author=unique_user)
        temporary_user.profile.delete()
        temporary_user.delete()
        return unique_user
