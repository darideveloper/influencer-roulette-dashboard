import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from model_bakery import baker

from core.tests_base.test_views import BaseTestApiViewsMethods
from roulette import models


class TestRouletteViewsBase(BaseTestApiViewsMethods):
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
        self.assertEqual(response.data["current_spins"], self.roulette.current_spins)
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
        for award in models.Award.objects.all():
            print(award.active)

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