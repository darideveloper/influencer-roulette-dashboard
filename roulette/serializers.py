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
