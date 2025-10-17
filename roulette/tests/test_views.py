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
        """Validate award data from response json

        Args:
            award_json (dict): Award data
        """
        award_obj = models.Award.objects.get(id=award_json["id"])
        self.assertEqual(award_json["name"], award_obj.name)
        self.assertEqual(award_json["description"], award_obj.description)
        self.assertIn(award_obj.image.url, award_json["image"])

    def test_get_roulette_list(self):
        """Test get all roulettes"""

        # valida response
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate results number
        json_data = response.json()["data"]
        self.assertEqual(json_data["count"], 1)
        self.assertEqual(json_data["results"][0]["id"], self.roulette.id)

    def test_get_roulette_detail(self):
        """Test get roulette detail"""

        # valida response
        response = self.client.get(f"{self.endpoint}{self.roulette.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate roulette data
        json_data = response.json()["data"]
        self.assertEqual(json_data["id"], self.roulette.id)
        self.assertEqual(json_data["name"], self.roulette.name)
        self.assertEqual(json_data["slug"], self.roulette.slug)
        self.assertIn(self.roulette.logo.url, json_data["logo"])
        self.assertEqual(json_data["subtitle"], self.roulette.subtitle)
        self.assertEqual(json_data["bottom_text"], self.roulette.bottom_text)
        self.assertIn(self.roulette.bg_image.url, json_data["bg_image"])
        self.assertEqual(
            json_data["spins_space_hours"], self.roulette.spins_space_hours
        )
        self.assertEqual(json_data["spins_ads_limit"], self.roulette.spins_ads_limit)
        self.assertIn(self.roulette.wrong_icon.url, json_data["wrong_icon"])
        self.assertEqual(json_data["message_no_spins"], self.roulette.message_no_spins)
        self.assertEqual(json_data["message_lose"], self.roulette.message_lose)
        self.assertEqual(json_data["message_win"], self.roulette.message_win)
        self.assertEqual(json_data["color_spin_1"], self.roulette.color_spin_1)
        self.assertEqual(json_data["color_spin_2"], self.roulette.color_spin_2)
        self.assertEqual(json_data["color_spin_3"], self.roulette.color_spin_3)
        self.assertEqual(json_data["color_spin_4"], self.roulette.color_spin_4)

        # Validate awards data
        self.assertEqual(len(json_data["awards"]), 3)
        for award in json_data["awards"]:
            self.__validate_award_data(award)

    def test_get_only_active_awards(self):
        """Test get roulette with only active awards"""

        # Set one award to inactive
        random_award = models.Award.objects.order_by("?").first()
        random_award.active = False
        random_award.save()

        # Validate response
        response = self.client.get(f"{self.endpoint}{self.roulette.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate awards in response
        json_data = response.json()["data"]
        self.assertEqual(len(json_data["awards"]), 2)
        for award in json_data["awards"]:
            self.__validate_award_data(award)

    def test_get_awards_no_sensitive_data(self):
        """Test get roulette with awards no sensitive data"""

        # Validate response
        response = self.client.get(f"{self.endpoint}{self.roulette.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate awards in response
        json_data = response.json()["data"]
        self.assertEqual(len(json_data["awards"]), 3)
        for award in json_data["awards"]:
            self.assertNotIn("min_spins", award)
            self.assertNotIn("active", award)


class ParticipantBaseTestCase(BaseTestApiViewsMethods):
    """Base class for testing participant views"""

    def load_dummy_data(self):
        """Create and load dummy data"""

        self.roulette = baker.make(
            models.Roulette,
            spins_space_hours=0.003,  # limit to aprox 10 seconds per spin
            spins_ads_limit=2,  # limit to 2 ads spins
            name="Test Roulette 1",
        )
        for award_index in range(3):
            award = baker.make(
                models.Award,
                roulette=self.roulette,
                active=True,
                min_spins=10 + award_index,
            )
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

    def validate_response_data(self, response, can_spin=True, can_spin_ads=True):
        """Validate response data from validate endpoint (can spin and can spin ads)

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

    def create_spin(self, is_extra_spin=False):
        """Create spin in database

        Args:
            is_extra_spin (bool): Is extra spin
        """
        models.ParticipantSpin.objects.create(
            participant=self.participant,
            roulette=self.roulette,
            is_extra_spin=is_extra_spin,
        )

    def wait_for_space_time(self):
        """Wait for space time: time required to wait until next spin"""
        sleep(self.roulette.spins_space_hours * 3600 + 1)


class ParticipantViewValidateTestCase(ParticipantBaseTestCase):

    def setUp(self):
        super().setUp("/api/participant/validate/", restricted_post=False)

        self.load_dummy_data()

        # Update api data
        self.api_data["is_extra_spin"] = False

    def test_missing_data(self):
        """Test missing data"""
        response = self.client.post(self.endpoint, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "Invalid data")

    def test_invalid_roulette(self):
        """Test invalid roulette"""
        self.api_data["roulette"] = "invalid-roulette"
        response = self.client.post(self.endpoint, data=self.api_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "Invalid data")

    def test_new_participant(self):
        """Test create new participant when validate"""

        # Delete participant
        self.participant.delete()

        # Validate no participant before api call
        self.assertEqual(models.Participant.objects.count(), 0)

        # Validate response
        response = self.client.post(self.endpoint, data=self.api_data)
        self.validate_response_data(response, can_spin=True, can_spin_ads=True)

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
        self.validate_response_data(response, can_spin=True, can_spin_ads=True)

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
            self.create_spin()

            # Check for next ads spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.validate_response_data(response, can_spin=False, can_spin_ads=True)

            # Wait until space time
            self.wait_for_space_time()

            # Check for next ads spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.validate_response_data(response, can_spin=True, can_spin_ads=True)

    def test_spin_limit(self):
        """Test regular spin limit:

        User already has a regular spin, so next spin is not allowed
        After space time, next spin is allowed
        """

        # Simullate two regular spins
        for _ in range(2):

            # Simullate first spin
            self.create_spin()

            # Check for second spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.validate_response_data(response, can_spin=False, can_spin_ads=True)

            # Wait until space time
            self.wait_for_space_time()

            # Check for third spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.validate_response_data(response, can_spin=True, can_spin_ads=True)

    def test_ads_spin_limit(self):
        """Test ads spin limit

        User already has a regular spin, so next ads spin is not allowed
        After space time, next ads spin is allowed
        """

        # Simullate two spins groups
        for _ in range(2):

            # Simullate first spin
            self.create_spin()

            # Simullate X ads spins
            for _ in range(self.roulette.spins_ads_limit):
                self.create_spin(is_extra_spin=True)

            # Check for next spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.validate_response_data(response, can_spin=False, can_spin_ads=False)

            # Wait until space time
            self.wait_for_space_time()

            # Check for next spin with api
            response = self.client.post(self.endpoint, data=self.api_data)
            self.validate_response_data(response, can_spin=True, can_spin_ads=True)


class ParticipantSpinTestCase(ParticipantBaseTestCase):

    def setUp(self):
        super().setUp("/api/participant/spin/", restricted_post=False)

        # Dummy data
        self.load_dummy_data()

    def test_missing_data(self):
        """validate error response when missing data"""
        response = self.client.post(self.endpoint, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "Invalid data")

    def test_invalid_roulette(self):
        """Validate error response when invalid roulette"""
        self.api_data["roulette"] = "invalid-roulette"
        response = self.client.post(self.endpoint, data=self.api_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "Invalid data")

    def test_spin_bypass_validation(self):
        """Validate success response when user bypass validation:
        - New user created
        - Spin created
        - No award
        """

        for is_extra_spin in [True, False]:

            self.api_data["is_extra_spin"] = is_extra_spin

            # Delete old data and reset roulette spins counter
            models.Participant.objects.all().delete()
            self.roulette.spins_counter = 0
            self.roulette.save()

            # Create spin with api call
            response = self.client.post(self.endpoint, data=self.api_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["message"], "Spin created")
            self.assertEqual(response.json()["data"]["award"], None)

            # Validate user created
            self.assertEqual(models.Participant.objects.count(), 1)
            participant = models.Participant.objects.first()
            self.assertEqual(participant.email, self.api_data["email"])
            self.assertEqual(participant.name, self.api_data["name"])

            # Validate roulette spins counter reset to 1 (only new spin created)
            self.roulette.refresh_from_db()
            self.assertEqual(self.roulette.spins_counter, 1)

            # Validate award not created
            self.assertEqual(models.ParticipantAward.objects.count(), 0)

    def test_spin_bypass_no_more_spins(self):
        """Validate error response when user try to spin bypassing validation
        and user has no more spins
            - No regular spin created
            - No spin created
            - No award
        """

        # Create 12 regular spin an any requires extra spins
        self.create_spin(is_extra_spin=False)
        for _ in range(self.roulette.spins_ads_limit):
            self.create_spin(is_extra_spin=True)
        initial_spins_counter = self.roulette.spins_counter

        for is_extra_spin in [True, False]:

            # Create 1 regular spin and update api data
            self.api_data["is_extra_spin"] = is_extra_spin

            # Create spin with api call
            response = self.client.post(self.endpoint, data=self.api_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json()["message"], "Invalid data")
            self.assertEqual(
                response.json()["data"]["non_field_errors"][0],
                (
                    "You can't regular spin"
                    if not is_extra_spin
                    else "You can't extra spin"
                ),
            )

            # Validate no spin created (only test spin created)
            self.assertEqual(
                models.ParticipantSpin.objects.count(), initial_spins_counter
            )

    def test_spins_without_award(self):
        """Validate success response when user spin without award:
        - Spin created
        - No award
        """

        for is_extra_spin in [True, False]:

            self.api_data["is_extra_spin"] = is_extra_spin

            # Delete old spins
            models.ParticipantSpin.objects.all().delete()

            # Create spin with api call
            response = self.client.post(self.endpoint, data=self.api_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Validate response data
            json_data = response.json()["data"]
            self.assertEqual(json_data["award"], None)

            # Validate spin created
            self.assertEqual(models.ParticipantSpin.objects.count(), 1)

            # Validate award not created
            self.assertEqual(models.ParticipantAward.objects.count(), 0)

    def test_spin_with_award(self):
        """Validate success response when user spin with award
        (exact min spins and overflow min spins)
        - Spin created
        - Award created
        - Award associated to participant
        """

        for is_extra_spin in [True, False]:

            for spins_counter in [10, 100]:

                # Delete old spins and awards
                models.ParticipantSpin.objects.all().delete()
                models.ParticipantAward.objects.all().delete()

                self.api_data["is_extra_spin"] = is_extra_spin

                # Set roulette spins counter
                self.roulette.spins_counter = spins_counter
                self.roulette.save()

                # Create spin with api call
                response = self.client.post(self.endpoint, data=self.api_data)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                # Validate response data
                json_data = response.json()["data"]
                awards = models.Award.objects.all()
                self.assertEqual(json_data["award"]["id"], awards.first().id)

                # Validate spin created
                self.assertEqual(models.ParticipantSpin.objects.count(), 1)

                # Validate award created
                self.assertEqual(models.ParticipantAward.objects.count(), 1)
                awardParticipant = models.ParticipantAward.objects.first()
                self.assertEqual(awardParticipant.participant, self.participant)
                self.assertEqual(awardParticipant.award, awards.first())

                # Validate roulette spins counter reset to 1 (only new spin created)
                old_spins_counter = self.roulette.spins_counter
                self.roulette.refresh_from_db()
                self.assertEqual(
                    self.roulette.spins_counter,
                    old_spins_counter - awards.first().min_spins + 1,
                )

    def test_spin_until_win_award(self):
        """Validate success response when user spin until win a award:
        - Spin created
        - Award created
        - Award associated to participant
        """

        # Set award min_spins to 3
        award = models.Award.objects.first()
        award.min_spins = 3
        award.save()

        json_data = {}
        for _ in range(4):
            # Create spin with api call
            response = self.client.post(self.endpoint, data=self.api_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Validate response data
            json_data = response.json()["data"]

            # wait for space time
            self.wait_for_space_time()

        # Validate award in last spin
        self.assertEqual(json_data["award"]["id"], award.id)

        # Validate 4 spins created
        self.assertEqual(models.ParticipantSpin.objects.count(), 4)

        # Validate 1 award created
        self.assertEqual(models.ParticipantAward.objects.count(), 1)
        awardParticipant = models.ParticipantAward.objects.first()
        self.assertEqual(awardParticipant.participant, self.participant)
        self.assertEqual(awardParticipant.award, award)

        # Validate roulette spins counter reset to 1 (only new spin created)
        self.roulette.refresh_from_db()
        self.assertEqual(self.roulette.spins_counter, 1)
