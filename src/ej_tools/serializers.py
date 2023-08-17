from rest_framework import serializers
from .models import RasaConversation, OpinionComponent


class RasaConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RasaConversation
        fields = ["conversation", "domain"]


class OpinionComponentSerializer(serializers.BaseSerializer):
    def to_representation(self, instance: OpinionComponent):
        """
        to_representation customizes how Serializers returns data
        """
        request = self.context["request"]
        return {
            "background_image_url": instance.get_upload_url(request, "background_image"),
            "logo_image_url": instance.get_upload_url(request, "logo_image"),
            "final_voting_message": instance.final_voting_message,
        }

    def get_empty_data(request):
        return {
            "background_image_url": OpinionComponent.default_bg_img_url(request),
            "logo_image_url": "",
            "final_voting_message": "",
        }
