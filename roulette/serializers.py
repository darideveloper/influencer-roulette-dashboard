from datetime import timedelta
from django.utils import timezone

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from roulette import models


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Award
        fields = ["id", "name", "description", "image"]


class RouletteSerializer(serializers.ModelSerializer):

    awards = SerializerMethodField()

    class Meta:
        model = models.Roulette
        fields = "__all__"

    def get_awards(self, obj):
        # return only active awards
        active_awards = obj.awards.filter(active=True)
        return AwardSerializer(active_awards, many=True).data


class ParticipantSpinSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField()
    roulette = serializers.PrimaryKeyRelatedField(
        queryset=models.Roulette.objects.all()
    )

    def validate(self, data):
        # Default response
        data["can_spin"] = True
        data["can_spin_ads"] = True

        # Participant logic
        participants = models.Participant.objects.filter(email=data["email"])
        if participants.exists():
            participant = participants.first()
            data["participant"] = participant  # pass to create()
            participant_spins = models.ParticipantSpin.objects.filter(
                participant=participant, roulette=data["roulette"]
            ).order_by("-created_at")

            # Regular spin limit
            last_regular_spin = participant_spins.filter(is_extra_spin=False).first()
            roulette = data["roulette"]
            if (
                last_regular_spin.created_at
                + timedelta(hours=roulette.spins_space_hours)
                > timezone.now()
            ):
                data["can_spin"] = False

            # Extra spin limit
            num_extra_spins = participant_spins.filter(is_extra_spin=True).count()
            last_extra_spin = participant_spins.filter(is_extra_spin=True).first()
            
            if (num_extra_spins >= roulette.spins_ads_limit):
                data["can_spin_ads"] = False
                
            if (
                last_extra_spin.created_at
                + timedelta(hours=roulette.spins_space_hours)
                > timezone.now()
            ):
                data["can_spin_ads"] = False

        return data

    def create(self, validated_data):
        participant = validated_data.get("participant")
        if participant:
            participant.name = validated_data["name"]
            participant.save()
        else:
            participant = models.Participant.objects.create(
                email=validated_data["email"], name=validated_data["name"]
            )

        return validated_data
