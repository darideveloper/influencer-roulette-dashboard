from rest_framework import viewsets

from roulette import models, serializers


class RouletteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Roulette.objects.all()
    serializer_class = serializers.RouletteSerializer
    lookup_field = "slug"
