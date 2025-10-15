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