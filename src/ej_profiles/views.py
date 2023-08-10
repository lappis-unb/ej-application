from typing import Any
from django.db.models.query import QuerySet
import toolz
from django.db.models import Q, Count
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView


from ej_conversations.models import Conversation, Comment
from . import forms
from .models import Profile


@method_decorator([login_required], name="dispatch")
class DetailView(DetailView):
    template_name = "ej_profiles/detail.jinja2"

    def get_object(self) -> Profile:
        return self.request.user.get_profile()

    def get_context_data(self, **kwargs):
        profile = self.get_object()

        return {
            "profile": self.get_object(),
            "n_conversations": profile.conversations.count(),
            "n_boards": profile.boards.count(),
            "n_favorites": profile.favorite_conversations.count(),
            "n_comments": profile.user.comments.count(),
            "n_votes": profile.votes.count(),
            "achievements_href": None,
        }


@method_decorator([login_required], name="dispatch")
class EditView(UpdateView):
    template_name = "ej_profiles/edit.jinja2"
    form_class = forms.ProfileForm

    def post(self, request):
        form = self.form_class(instance=self.get_object(), request=self.request)

        if form.is_valid_post():
            form.files = request.FILES
            form.save()

            return redirect("/profile/")

        return render(request, self.template_name, self.get_context_data())

    def get_object(self) -> Profile:
        return self.request.user.get_profile()

    def get_context_data(self, **kwargs):
        profile = self.get_object()

        return {"form": self.form_class(instance=profile, request=self.request), "profile": profile}


@method_decorator([login_required], name="dispatch")
class ContributionsView(DetailView):
    template_name = "ej_profiles/contributions.jinja2"

    def get_context_data(self, **kwargs):
        profile = self.request.user.get_profile()
        created = profile.conversations.cache_annotations(
            "first_tag", "n_user_votes", "n_comments", user=profile.user
        )

        # Fetch voted conversations
        # This code merges in python 2 querysets. The first is annotated with
        # tag and the number of user votes. The second is annotated with the total
        # number of comments in each conversation
        voted = profile.conversations_with_votes.exclude(id__in=[x.id for x in created])
        voted = voted.cache_annotations("first_tag", "n_user_votes", user=profile.user)
        voted_extra = (
            Conversation.objects.filter(id__in=[x.id for x in voted])
            .cache_annotations("n_comments")
            .values("id", "n_comments")
        )
        total_votes = {}
        for item in voted_extra:
            total_votes[item["id"]] = item["n_comments"]
        for conversation in voted:
            conversation.annotation_total_votes = total_votes[conversation.id]

        # Now we get the favorite conversations from user
        favorites = Conversation.objects.filter(favorites__user=profile.user).cache_annotations(
            "first_tag", "n_user_votes", "n_comments", user=profile.user
        )

        # Comments
        comments = profile.user.comments.select_related("conversation").annotate(
            skip_count=Count("votes", filter=Q(votes__choice=0)),
            agree_count=Count("votes", filter=Q(votes__choice__gt=0)),
            disagree_count=Count("votes", filter=Q(votes__choice__lt=0)),
        )
        groups = toolz.groupby(lambda x: x.status, comments)
        approved = groups.get(Comment.STATUS.approved, ())
        rejected = groups.get(Comment.STATUS.rejected, ())
        pending = groups.get(Comment.STATUS.pending, ())

        return {
            "profile": profile,
            "user": profile.user,
            "created_conversations": created,
            "favorite_conversations": favorites,
            "voted_conversations": voted,
            "approved_comments": approved,
            "rejected_comments": rejected,
            "pending_comments": pending,
        }
