from ej_profiles.models import Profile
from rest_framework import serializers
from .enums import Race, Gender, Region


class ProfileSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=False)
    race = serializers.ChoiceField(
        choices=[(tag.value, tag) for tag in Race], required=False
    )
    gender = serializers.ChoiceField(
        choices=[(tag.value, tag) for tag in Gender], required=False
    )
    birth_date = serializers.DateField(required=False)
    region = serializers.ChoiceField(
        choices=[(tag.value, tag) for tag in Region], required=False
    )

    class Meta:
        model = Profile
        fields = [
            "phone_number",
            "race",
            "gender",
            "birth_date",
            "region",
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
