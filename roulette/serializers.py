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


class ParticipantValidateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField()
    roulette = serializers.SlugRelatedField(
        queryset=models.Roulette.objects.all(), slug_field="slug"
    )

    def validate(self, data):
        """Validate if participant can spin and return response data"""

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

            if not last_regular_spin.exists():
                print("no last regular spin")
                return data
            
            # Get last regular spin
            last_regular_spin = last_regular_spin.first()

            # Calculate time to spin regular and check if if user can spin
            time_to_spin_next = last_regular_spin.created_at + timedelta(
                hours=roulette.spins_space_hours
            )
            if time_to_spin_next > timezone.now():
                data["can_spin"] = False
                
                # Calculate number of extra spins in space time
                num_extra_spins_in_space_time = participant_spins.filter(
                    is_extra_spin=True,
                    created_at__gte=last_regular_spin.created_at,
                ).count()
                
                if num_extra_spins_in_space_time >= roulette.spins_ads_limit:
                    data["can_spin_ads"] = False

        return data

    def create(self, validated_data):
        """Create participant or update name"""

        participant = validated_data.get("participant")
        if participant:
            # Update participant name
            participant.name = validated_data["name"]
            participant.save()
        else:
            # Create new participant
            participant = models.Participant.objects.create(
                email=validated_data["email"], name=validated_data["name"]
            )

        # Add participant to validated data
        validated_data["participant"] = participant

        # Return validated data
        return validated_data


class ParticipantSpinSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField()
    roulette = serializers.SlugRelatedField(
        queryset=models.Roulette.objects.all(), slug_field="slug"
    )
    is_extra_spin = serializers.BooleanField()

    def validate(self, data):

        # Add data to validated_data
        data["award"] = None
        data["participant"] = None

        # Validate participant
        validate_serializer = ParticipantValidateSerializer(
            data={
                "email": data["email"],
                "name": data["name"],
                "roulette": data["roulette"].slug,
            }
        )
        if not validate_serializer.is_valid():
            raise serializers.ValidationError(validate_serializer.errors)
        validated_data = validate_serializer.save()
        data["participant"] = validated_data["participant"]

        # Detect spins bypass validation
        if data["is_extra_spin"] and not validated_data["can_spin_ads"]:
            raise serializers.ValidationError("You can't extra spin")

        if not data["is_extra_spin"] and not validated_data["can_spin"]:
            raise serializers.ValidationError("You can't regular spin")

        # Calculate if user win a award based in roulette data
        roulette_total_spins = data["roulette"].spins_counter
        roulette_awards = models.Award.objects.filter(
            roulette=data["roulette"],
            active=True,
        )
        for award in roulette_awards:
            if roulette_total_spins >= award.min_spins:
                data["award"] = award
                break

        return data

    def create(self, validated_data):

        # Register spin in database
        models.ParticipantSpin.objects.create(
            participant=validated_data["participant"],
            roulette=validated_data["roulette"],
            is_extra_spin=validated_data["is_extra_spin"],
        )

        award = validated_data.get("award")
        if award:
            # Register award if user win
            models.ParticipantAward.objects.create(
                participant=validated_data["participant"],
                award=award,
            )

            # Reduce roulette spins counter
            validated_data["roulette"].spins_counter -= award.min_spins
            validated_data["roulette"].save()

        # Return validated data
        return validated_data
