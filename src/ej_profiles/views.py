from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView
from django.http import HttpResponse
from ej_boards.models import Board
from ej_conversations.models import Conversation, ConversationTag
from ej_tools.utils import get_host_with_schema

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
        return profile.get_contributions_data()


@method_decorator([login_required], name="dispatch")
class HomeView(ListView):
    template_name = "ej_profiles/home.jinja2"
    queryset = Conversation.objects.filter(is_promoted=True)

    def get(self, request, *args, **kwargs):
        user = request.user
        tour_url = reverse("profile:tour")
        print(user.get_profile().completed_tour)
        if user.get_profile().completed_tour:
            return super().get(request, *args, **kwargs)
        return redirect(tour_url)

    def get_context_data(self, **kwargs):
        public_conversations = self.get_queryset()
        user_participated_tags = self.request.user.profile.participated_tags()
        public_tags = ConversationTag.objects.filter(content_object__is_promoted=True).distinct("tag")
        my_tags = ConversationTag.objects.filter(content_object__author=self.request.user).distinct("tag")
        contributions_data = self.request.user.profile.get_contributions_data()

        public_tags_str = [str(tag.tag) for tag in public_tags]
        my_tags_str = [str(tag.tag) for tag in my_tags]
        participated_tag_str = [str(tag.tag) for tag in user_participated_tags]

        return {
            "user_boards": Board.objects.filter(owner=self.request.user),
            "public_conversations": public_conversations,
            "participated_tags": participated_tag_str,
            "all_tags": public_tags_str,
            "host": get_host_with_schema(self.request),
            "has_filtered_tag": self.request.user.profile.filtered_home_tag,
            "my_tags": my_tags_str,
            **contributions_data,
        }


@method_decorator([login_required], name="dispatch")
class TourView(HomeView):
    def _get_tour_step_template(self, step: str):
        if not step:
            return "ej_profiles/tour.jinja2"
        return f"ej_profiles/includes/tour-page{step}.jinja2"

    def get(self, *args, **kwargs):
        user = self.request.user
        if user.get_profile().completed_tour:
            return redirect(reverse("profile:home"))
        tour_step = self.request.GET.get("step")
        template_name = self._get_tour_step_template(tour_step)
        return render(self.request, template_name, self.get_context_data())

    def post(self, *args, **kwargs):
        user = self.request.user
        response = HttpResponse()
        if self.request.GET.get("step") in ["skip", "end"]:
            profile = user.get_profile()
            profile.completed_tour = True
            profile.save()
            """
            Tour page utilizes HTMX library to make backend AJAX requests.
            In order to make a redirect with HTMX,
            we need to include HX-Redirect header in the response.
            For more information, access https://htmx.org/reference/.
            """
            response.status_code = 302
            response["HX-Redirect"] = reverse("profile:home")
        return response
