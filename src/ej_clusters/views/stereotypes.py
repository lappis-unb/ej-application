from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from django.views.generic import ListView, CreateView

from ej_clusters.forms import StereotypeForm
from ej_clusters.utils import check_stereotype
from ..models import Stereotype


@method_decorator([login_required], name="dispatch")
class StereotypeListView(ListView):
    template_name = "ej_clusters/stereotypes/list.jinja2"

    def get_queryset(self):
        return self.request.user.stereotypes.prefetch_related("clusters__clusterization__conversation")

    def get_context_data(self, **kwargs):
        qs = self.get_queryset()
        stereotypes = []
        for stereotype in qs:
            stereotype.conversations = conversations = []
            for cluster in stereotype.clusters.all():
                conversations.append(cluster.clusterization.conversation)
            stereotypes.append(stereotype)
        return {"stereotypes": stereotypes}


@method_decorator([login_required], name="dispatch")
class StereotypeCreateView(CreateView):
    template_name = "ej_clusters/stereotypes/create.jinja2"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = StereotypeForm(request=request, owner=request.user)
        if form.is_valid_post():
            form.save()
            return redirect("stereotypes:list")
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        form = StereotypeForm(request=self.request, owner=self.request.user)
        return {"form": form}


@method_decorator([login_required], name="dispatch")
class StereotypeEditView(UpdateView):
    model = Stereotype
    template_name = "ej_clusters/stereotypes/edit.jinja2"
    form_class = StereotypeForm

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        stereotype = self.get_object()
        form = self.form_class(request=self.request, instance=stereotype)

        if request.POST.get("action") == "delete":
            stereotype.delete()
        elif form.is_valid_post():
            form.save()
        else:
            return render(request, self.template_name, self.get_context_data())

        return redirect("stereotypes:list")

    def get_object(self) -> Stereotype:
        return check_stereotype(super().get_object(), self.request.user)

    def get_context_data(self, **kwargs):
        stereotype = self.get_object()
        form = self.kwargs.get("form", self.form_class(request=self.request, instance=stereotype))
        return {"form": form, "stereotype": stereotype}
