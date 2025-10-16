from django.test import TestCase
from model_bakery import baker

from roulette import models


class RouletteTestCase(TestCase):

    def setUp(self):
        pass

    def test_save_create_slug(self):
        roulette = baker.make(models.Roulette, name="Test Roulette")
        self.assertEqual(roulette.slug, "test-roulette")

    def test_save_update_slug(self):
        roulette = baker.make(models.Roulette, name="Test Roulette")
        roulette.name = "Test Roulette 2"
        roulette.save()
        self.assertEqual(roulette.slug, "test-roulette-2")


class ParticipantSpinTestCase(TestCase):

    def setUp(self):
        pass

    def test_save_increase_spins_counter(self):
        """Validate if spins counter is increased when a spin is created"""

        roulette = baker.make(models.Roulette, spins_counter=0)
        participant = baker.make(models.Participant)
        
        self.assertEqual(roulette.spins_counter, 0)

        # Create spin
        models.ParticipantSpin.objects.create(
            participant=participant,
            roulette=roulette,
            is_extra_spin=False,
        )
        self.assertEqual(roulette.spins_counter, 1)
