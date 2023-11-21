from typing import Any, Dict

from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView
from ej_conversations.models import Conversation
from ej_conversations.models.vote import normalize_choice
from ej_conversations.utils import conversation_admin_menu_links
from ej_dataviz.utils import export_data

from .models import SegmentFilter


class EngagementFrameView(DetailView):
    """
    View to save engagement level input value.
    Returns HTML results section with engagement level filter applied.
    """

    template_name = "ej_activation/includes/results-frame.jinja2"
    model = SegmentFilter

    def post(self, request, *args, **kwargs):
        segment_filter = self.get_object()
        engagement_level = self.request.POST.get("participation_level")
        try:
            segment_filter.engagement_level = int(engagement_level)
        except Exception:
            segment_filter.engagement_level = 0
        segment_filter.save()
        return render(
            request,
            self.template_name,
            {
                "segment_filter": segment_filter,
                "comments": segment_filter.comments,
                "participants": segment_filter.filter(),
            },
        )


class ClustersFrameView(DetailView):
    """
    View to save clusters select input.
    Returns HTML results section with selected clusters filter applied.
    """

    template_name = "ej_activation/includes/results-frame.jinja2"
    model = SegmentFilter

    def post(self, request, *args, **kwargs):
        segment_filter = self.get_object()
        clusters = segment_filter.get_clusters_by_id(self.request.POST.getlist("clusters"))
        segment_filter.clusters.set(clusters)
        segment_filter.save()
        return render(
            request,
            self.template_name,
            {
                "segment_filter": segment_filter,
                "comments": segment_filter.comments,
                "participants": segment_filter.filter(),
            },
        )


class CommentsFrameView(DetailView):
    """
    View to save comments options input.
    Returns HTML results section with comments filter applied.
    """

    model = SegmentFilter

    def get(self, request, *args, **kwargs):
        template_name = "ej_activation/includes/comments-frame.jinja2"
        segment_filter: SegmentFilter = self.get_object()
        comments_page = self.request.GET.get("page")
        conversation = segment_filter.conversation
        pagination = Paginator(conversation.comments.all(), 4)
        page = pagination.page(comments_page) if comments_page else pagination.page(1)
        return render(
            request,
            template_name,
            {
                "comments": segment_filter.comments,
                "page": page,
                "segment_filter": segment_filter,
                "comments_pagination_url": reverse(
                    "ej_activation:comments",
                    kwargs={
                        "board_slug": conversation.board.slug,
                        "slug": conversation.slug,
                        "conversation_id": conversation.id,
                        "pk": segment_filter.id,
                    },
                ),
            },
        )

    def post(self, request, *args, **kwargs):
        template_name = "ej_activation/includes/results-frame.jinja2"
        segment_filter = self.get_object()
        comment_and_choice: str = self.request.POST.get("comment")
        comment_id, choice = comment_and_choice.split(",")
        if not int(comment_id):
            return HttpResponse("invalid comment id", status=500)
        choice = normalize_choice(choice)
        segment_filter.remove_or_update_comment(comment_id, choice.value)
        segment_filter.save()
        return render(
            request,
            template_name,
            {
                "segment_filter": segment_filter,
                "comments": segment_filter.comments,
                "participants": segment_filter.filter(),
            },
        )


class ActivationExportView(DetailView):
    """
    View to export segments results.
    Returns an CSV file with segmented participants.
    """

    model = SegmentFilter

    def get(self, request, *args, **kwargs):
        from django_pandas.io import read_frame

        segment_filter = self.get_object()
        data = segment_filter.filter()
        df = read_frame(data)
        return export_data(df, "csv", f"{segment_filter.conversation.slug}_segmento")


class ActivationIndexView(DetailView):
    """
    View to list a conversation segments.
    """

    template_name = "ej_activation/index.jinja2"
    model = Conversation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation = self.get_object()
        context["conversation"] = conversation
        context["object_list"] = SegmentFilter.objects.filter(conversation=conversation).order_by("id")
        return context


class ActivationDetailView(DetailView):
    """
    View to edit a conversation segment.
    """

    template_name = "ej_activation/detail.jinja2"
    queryset = SegmentFilter.objects.all()

    def _get_data(
        self, user, conversation, segment_filter: SegmentFilter, form, segmentation_result=None
    ) -> Dict[str, Any]:
        comments_page = self.request.GET.get("page")
        pagination = Paginator(conversation.comments.all(), 4)
        page = pagination.page(comments_page) if comments_page else pagination.page(1)
        return {
            "conversation": conversation,
            "comment": conversation.next_comment_with_id(user, None),
            "menu_links": conversation_admin_menu_links(conversation, user),
            "form": form,
            "segment_filter": segment_filter,
            "participants": segmentation_result["participants"],
            "comments": segmentation_result["comments"],
            "conversation_clusters": self._get_conversation_clusters(conversation),
            "selected_clusters": segment_filter.clusters.all().values_list("id", flat=True),
            "comments_pagination_url": reverse(
                "ej_activation:comments",
                kwargs={
                    "board_slug": conversation.board.slug,
                    "slug": conversation.slug,
                    "conversation_id": conversation.id,
                    "pk": segment_filter.id,
                },
            ),
            "page": page,
        }

    def get_context_data(self, **kwargs):
        user = self.request.user
        segment_filter = self.get_object()
        segmentation_result = {"participants": segment_filter.filter(), "comments": segment_filter.comments}
        conversation = segment_filter.conversation
        return self._get_data(user, conversation, segment_filter, None, segmentation_result)

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def _get_conversation_clusters(self, conversation: Conversation):
        try:
            clusterization = conversation.clusterization
            return [(cluster.id, cluster.name) for cluster in clusterization.clusters.all()]
        except Exception as e:
            return []


class ActivationAddView(DetailView):
    """
    View to create an empty segment filter.
    """

    model = Conversation

    def get(self, request, *args, **kwargs):
        conversation = self.get_object()
        segment_filter = SegmentFilter.objects.create(
            conversation=conversation, engagement_level=0, comments={}
        )
        return HttpResponseRedirect(
            reverse(
                "activation:detail",
                kwargs={
                    "board_slug": conversation.board.slug,
                    "slug": conversation.slug,
                    "conversation_id": conversation.id,
                    "pk": segment_filter.id,
                },
            )
        )
