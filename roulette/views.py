from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from roulette import models, serializers


class RouletteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Roulette.objects.all()
    serializer_class = serializers.RouletteSerializer
    lookup_field = "slug"


class ParticipantViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def validate(self, request):
        """Create new participant, update and check if can spin"""
        serializer = serializers.ParticipantValidateSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.save()

            # get response data
            response_data = {
                "can_spin": validated_data["can_spin"],
                "can_spin_ads": validated_data["can_spin_ads"],
            }

            # Return success response
            return Response(
                {
                    "status": "success",
                    "message": "Participant validated",
                    "data": response_data,
                },
                status=status.HTTP_200_OK,
            )

        # Error response
        return Response(
            {
                "status": "error",
                "message": "Invalid data",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"])
    def spin(self, request):
        """Create spin and return if user win a award"""
        serializer = serializers.ParticipantSpinSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.save()

            # get response data
            response_data = {
                "award": None,
            }
            if validated_data["award"]:
                response_data["award"] = serializers.AwardSerializer(
                    validated_data["award"]
                ).data

            return Response(
                {
                    "status": "success",
                    "message": "Spin created",
                    "data": response_data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "error",
                "message": "Invalid data",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
