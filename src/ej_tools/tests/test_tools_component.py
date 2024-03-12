import pytest
from io import BytesIO
from PIL import Image
from django.test import Client
from django.core.files.base import File

from ej_conversations.mommy_recipes import ConversationRecipes
from ej_tools.models import OpinionComponent

ConversationRecipes.update_globals(globals())


class TestOpinionComponent(ConversationRecipes):
    @staticmethod
    def get_image_file(name, ext="png", size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    def test_custom_conversation_component_without_mandatory_fields(
        self, conversation_db
    ):
        client = Client()
        client.force_login(conversation_db.author)

        url = conversation_db.patch_url("conversation-tools:opinion-component")
        data = {
            "conversation": conversation_db.id,
            "final_voting_message": "finished voting!",
            "custom": "",
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert not OpinionComponent.objects.filter(conversation=conversation_db).exists()

    def test_custom_conversation_component_valid_form(self, conversation_db):
        client = Client()
        client.force_login(conversation_db.author)

        url = conversation_db.patch_url("conversation-tools:opinion-component")
        logo_image = TestOpinionComponent.get_image_file("image2.png")
        data = {
            "logo_image": logo_image,
            "conversation": conversation_db.id,
            "final_voting_message": "finished voting!",
            "custom": "",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert OpinionComponent.objects.filter(conversation=conversation_db).exists()

    def test_get_conversation_component(self, conversation_db):
        client = Client()
        client.force_login(conversation_db.author)

        url = conversation_db.patch_url("conversation-tools:opinion-component")
        response = client.get(url)
        assert response.status_code == 200
        assert b"logo_image" in response.content

    def test_custom_conversation_component_invalid_form(self, conversation_db):
        client = Client()
        client.force_login(conversation_db.author)

        url = conversation_db.patch_url("conversation-tools:opinion-component")
        logo_image = TestOpinionComponent.get_image_file("image2.png")
        data = {
            "logo_image": logo_image,
            "conversation": conversation_db.id,
            "final_voting_message": "",
            "custom": "",
        }
        response = client.post(url, data)

        error_message = "This field is required"
        assert response.status_code == 200
        assert not OpinionComponent.objects.filter(conversation=conversation_db).exists()
        assert error_message.encode() in response.content
