from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from hyperpython import html
from hyperpython.components import fa_icon
from sidekick import import_later

from ej.roles import with_template
from ej_conversations import models

np = import_later("numpy")
User = get_user_model()

#
# Conversation roles
#
DEFAULT_FORMATS = {"csv": "CSV", "json": "JSON"}


@with_template(models.Conversation, role="download-data")
def conversation_download_data(
    conversation, *, which, formats=None, cluster=None, **url_kwargs
):
    if ":" not in which:
        which = f"boards:dataviz-{which}"
        if cluster is not None:
            which += "-cluster"

    # Prepare urls
    url_kwargs = {}
    if cluster is not None:
        url_kwargs["cluster_id"] = cluster.id

    format_lst = []
    for format, name in (formats or DEFAULT_FORMATS).items():
        request_kwargs = conversation.get_url_kwargs().copy()
        request_kwargs.update({"fmt": format})
        request_kwargs.update(url_kwargs)
        format_lst.append((name, which, request_kwargs))

    return {"conversation": conversation, "formats": format_lst}


html.register(type(fa_icon("check")), lambda x, *args: x)
