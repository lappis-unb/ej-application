import pytest
from django.conf import settings
from django.core.files import File

from ej_conversations.tests.conftest import *
from ej_tools.models import OpinionComponent

SOME_FILE = settings.BASE_DIR / "src/ej/static/ej/assets/img/tools/opinion-component-default-background.jpg"


@pytest.fixture
def opinion_component(db, conversation):
    instance = OpinionComponent()
    instance.conversation = conversation
    instance.final_voting_message = "texto final de votação"
    with open(str(SOME_FILE), "rb") as _file:
        instance.logo_image.save("logo.jpg", File(_file))
        instance.background_image.save("bg.jpg", File(_file))
    instance.save()
    return instance
