import os
from time import sleep

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from model_bakery import baker

from core.tests_base.test_views import BaseTestApiViewsMethods
from roulette import models


class TestRouletteViewsBaseTestCase(BaseTestApiViewsMethods):
    """Base class for testing roulette views"""

    def setUp(self):
        super().setUp("/api/roulette/")

        test_folder = os.path.join(settings.BASE_DIR, "media", "test")

        # Create dummy data
        self.roulette = baker.make(models.Roulette)
        for _ in range(3):
            award_image_name = "test.webp"
            award_image_path = os.path.join(test_folder, award_image_name)
            award = baker.make(models.Award, roulette=self.roulette)
            award.image = SimpleUploadedFile(
                name=award_image_name,
                content=open(award_image_path, "rb").read(),
                content_type="image/webp",
            )
            award.save()
        self.awards = models.Award.objects.all()

        # Add test images to roulette
        test_logo_name = "test-logo.webp"
        test_bg_image_name = "test-bg-image.webp"
        test_wrong_icon_name = "test-wrong-icon.webp"
        test_logo_path = os.path.join(test_folder, test_logo_name)
        test_bg_image_path = os.path.join(test_folder, test_bg_image_name)
        test_wrong_icon_path = os.path.join(test_folder, test_wrong_icon_name)
        self.roulette.logo = SimpleUploadedFile(
            name=test_logo_name,
            content=open(test_logo_path, "rb").read(),
            content_type="image/webp",
        )
        self.roulette.bg_image = SimpleUploadedFile(
            name=test_bg_image_name,
            content=open(test_bg_image_path, "rb").read(),
            content_type="image/webp",
        )
        self.roulette.wrong_icon = SimpleUploadedFile(
            name=test_wrong_icon_name,
            content=open(test_wrong_icon_path, "rb").read(),
            content_type="image/webp",
        )
        self.roulette.save()

    def __validate_award_data(self, award_json):
        """Validate award data

        Args:
            award_json (dict): Award data
        """
        award_obj = models.Award.objects.get(id=award_json["id"])
        self.assertEqual(award_json["name"], award_obj.name)
        self.assertEqual(award_json["description"], award_obj.description)
        self.assertIn(award_obj.image.url, award_json["image"])

    def test_get_roulette_list(self):
        """Test get roulette"""

        # valida response
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate results number
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.roulette.id)

    def test_get_roulette_detail(self):
        """Test get roulette detail"""

        # valida response
        response = self.client.get(f"{self.endpoint}{self.roulette.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate roulette data
        self.assertEqual(response.data["id"], self.roulette.id)
        self.assertEqual(response.data["name"], self.roulette.name)
        self.assertEqual(response.data["slug"], self.roulette.slug)
        self.assertIn(self.roulette.logo.url, response.data["logo"])
        self.assertEqual(response.data["subtitle"], self.roulette.subtitle)
        self.assertEqual(response.data["bottom_text"], self.roulette.bottom_text)
        self.assertIn(self.roulette.bg_image.url, response.data["bg_image"])
        self.assertEqual(
            response.data["spins_space_hours"], self.roulette.spins_space_hours
        )
        self.assertEqual(
            response.data["spins_ads_limit"], self.roulette.spins_ads_limit
        )
        self.assertIn(self.roulette.wrong_icon.url, response.data["wrong_icon"])
        self.assertEqual(
            response.data["message_no_spins"], self.roulette.message_no_spins
        )
        self.assertEqual(response.data["message_lose"], self.roulette.message_lose)
        self.assertEqual(response.data["message_win"], self.roulette.message_win)
        self.assertEqual(response.data["color_spin_1"], self.roulette.color_spin_1)
        self.assertEqual(response.data["color_spin_2"], self.roulette.color_spin_2)
        self.assertEqual(response.data["color_spin_3"], self.roulette.color_spin_3)
        self.assertEqual(response.data["color_spin_4"], self.roulette.color_spin_4)

        # Validate awards data
        self.assertEqual(len(response.data["awards"]), 3)
        for award in response.data["awards"]:
            self.__validate_award_data(award)

    def test_get_only_active_awards(self):
        """Test get only active awards"""

        # Set one award to inactive
        random_award = models.Award.objects.order_by("?").first()
        random_award.active = False
        random_award.save()

        # Validate response
        response = self.client.get(f"{self.endpoint}{self.roulette.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate awards in response
        self.assertEqual(len(response.data["awards"]), 2)
        for award in response.data["awards"]:
            self.__validate_award_data(award)

    def test_get_awards_no_sensitive_data(self):
        """Test get awards no sensitive data"""

        # Validate response
        response = self.client.get(f"{self.endpoint}{self.roulette.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate awards in response
        self.assertEqual(len(response.data["awards"]), 3)
        for award in response.data["awards"]:
            self.assertNotIn("min_spins", award)
            self.assertNotIn("active", award)


class ParticipantViewValidateTestCase(BaseTestApiViewsMethods):

    def setUp(self):
        super().setUp(
            "/api/participant/validate/", restricted_post=False
        )

        self.roulette = baker.make(
            models.Roulette,
            spins_space_hours=0.003,  # limit to aprox 10 seconds per spin
            spins_ads_limit=2,  # limit to 2 ads spins
        )
        for _ in range(3):
            award = baker.make(models.Award, roulette=self.roulette)
            award.save()

        # Api data
        self.api_data = {
            "email": "test@test.com",
            "name": "Test Participant",
            "roulette": self.roulette.slug,
        }

        # Create participant with dummy data
        self.participant = baker.make(
            models.Participant, email=self.api_data["email"], name=self.api_data["name"]
        )

    def __validate_response_data(self, response, can_spin=True, can_spin_ads=True):
        """Validate response data

        Args:
            response (Response): Response object
            can_spin (bool): Can spin
            can_spin_ads (bool): Can spin ads
        """

        # Validate response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response data
        json_data = response.json()["data"]
        self.assertEqual(json_data["can_spin"], can_spin)
        self.assertEqual(json_data["can_spin_ads"], can_spin_ads)
        
    def __create_spin(self, is_extra_spin=False):
        """Create spin
        
        Args:
            is_extra_spin (bool): Is extra spin
        """
        models.ParticipantSpin.objects.create(
            participant=self.participant,
            roulette=self.roulette,
            is_extra_spin=is_extra_spin,
        )
        
    def __wait_for_space_time(self):
        """Wait for space time"""
        sleep(self.roulette.spins_space_hours * 3600 + 1)

    def test_new_participant(self):
        """Test create new participant when validate"""

        # Delete participant
        self.participant.delete()

        # Validate no participant before api call
        self.assertEqual(models.Participant.objects.count(), 0)

        # Validate response
        response = self.client.post(self.endpoint, data=self.api_data)
        self.__validate_response_data(response, can_spin=True, can_spin_ads=True)

        # Validate participant created
        self.assertEqual(models.Participant.objects.count(), 1)
        participant = models.Participant.objects.first()

        # Validate participant data
        self.assertEqual(participant.email, self.api_data["email"])
        self.assertEqual(participant.name, self.api_data["name"])

    def test_update_participant_name(self):
        """Test update participant name when validate (if exists)"""

        # Update participant name
        self.api_data["name"] = "Test Participant 2"

        # Validate response
        response = self.client.post(self.endpoint, data=self.api_data)
        self.__validate_response_data(response, can_spin=True, can_spin_ads=True)

        # Validate participant updated
        self.participant.refresh_from_db()
        self.assertEqual(self.participant.name, self.api_data["name"])

    def test_ads_spin(self):
        """Test ads spin after regular spin

        User already has a regular spin, so next ads spin is allowed
        """
        
        # Simullate two regular spins
        for _ in range(2):

            # Simullate first spin
            self.__create_spin()

            # Check for next ads spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.__validate_response_data(response, can_spin=False, can_spin_ads=True)

            # Wait until space time
            self.__wait_for_space_time()

            # Check for next ads spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.__validate_response_data(response, can_spin=True, can_spin_ads=True)

    def test_spin_limit(self):
        """Test regular spin limit:

        User already has a regular spin, so next spin is not allowed
        After space time, next spin is allowed
        """
        
        # Simullate two regular spins
        for _ in range(2):

            # Simullate first spin
            self.__create_spin()

            # Check for second spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.__validate_response_data(response, can_spin=False, can_spin_ads=True)

            # Wait until space time
            self.__wait_for_space_time()

            # Check for third spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.__validate_response_data(response, can_spin=True, can_spin_ads=True)

    def test_ads_spin_limit(self):
        """Test ads spin limit

        User already has a regular spin, so next ads spin is not allowed
        After space time, next ads spin is allowed
        """

        # Simullate two regular spins
        for _ in range(2):

            # Simullate first spin
            self.__create_spin()

            # Simullate X ads spins
            for _ in range(self.roulette.spins_ads_limit):
                self.__create_spin(is_extra_spin=True)

            # Check for next spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.__validate_response_data(response, can_spin=False, can_spin_ads=False)

            # Wait until space time
            self.__wait_for_space_time()

            # Check for next spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.__validate_response_data(response, can_spin=True, can_spin_ads=True)