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
    roulette = serializers.SlugRelatedField(
        queryset=models.Roulette.objects.all(), slug_field="slug"
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

            # Allow to spin if not have any spin
            if not participant_spins.exists():
                return data

            roulette = data["roulette"]

            # Regular spin limit
            last_regular_spin = participant_spins.filter(is_extra_spin=False).order_by(
                "-created_at"
            )

            if last_regular_spin.exists():
                last_regular_spin = last_regular_spin.first()

                # Calculate time to spin regular
                time_to_spin_regular = last_regular_spin.created_at + timedelta(
                    hours=roulette.spins_space_hours
                )

                if time_to_spin_regular > timezone.now():
                    data["can_spin"] = False

            # Extra spin limit
            last_extra_spin = participant_spins.filter(is_extra_spin=True).order_by(
                "-created_at"
            )

            if last_extra_spin.exists():
                last_extra_spin = last_extra_spin.first()

                # Calculate time to spin extra
                time_to_spin_extra = last_extra_spin.created_at + timedelta(
                    hours=roulette.spins_space_hours
                )

                # Calculate number of extra spins in current space time
                space_time_start = timezone.now() - timedelta(
                    hours=roulette.spins_space_hours
                )
                num_extra_spins_in_space_time = participant_spins.filter(
                    is_extra_spin=True,
                    created_at__gte=space_time_start,
                ).count()

                if (
                    time_to_spin_extra > timezone.now()
                    or num_extra_spins_in_space_time >= roulette.spins_ads_limit
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
