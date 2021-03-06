from unittest import TestCase
from django.test import TestCase as DjangoTestCase

from mock import patch

from artists.models import Artist
from .. import models


class GeneralArtistModelTest(TestCase):

    """Tests for GeneralArtist model."""

    def test_save(self):
        name = "Brad Sucks"
        artist = models.GeneralArtist(name=name)
        with patch('similarities.models.GeneralArtist.save_base') as save_base:
            self.assertEqual(artist.normalized_name, "")
            artist.save()
            save_base.assert_called_once_with(
                update_fields=None,
                using='default',
                force_update=False,
                force_insert=False,
            )
            self.assertEqual(artist.normalized_name, name.upper())


class CreateGeneralArtistTest(DjangoTestCase):

    """Tests for create_general_artist post_save handler."""

    name = "Brad Sucks"
    normalized_name = name.upper()

    def test_insert(self):
        artist = Artist.objects.create(name=self.name)
        general_artist = models.GeneralArtist.objects.get()
        similarity = models.Similarity.objects.get()
        self.assertEqual(general_artist.name, self.name)
        self.assertEqual(general_artist.normalized_name, self.normalized_name)
        self.assertEqual(similarity.cc_artist, artist)
        self.assertEqual(similarity.other_artist, general_artist)
        self.assertEqual(similarity.weight, 5)

    def test_update(self):
        artist = Artist.objects.create(name=self.name)
        models.GeneralArtist.objects.all().delete()
        models.Similarity.objects.all().delete()
        artist.save()
        self.assertFalse(models.GeneralArtist.objects.exists())
        self.assertFalse(models.Similarity.objects.exists())


class BaseSimilarityModelTest(TestCase):

    """Tests for BaseSimilarity model."""

    def test_weights(self):
        self.assertEqual(list(models.BaseSimilarity.WEIGHTS), [
            (0, 'dissimilar (these artists are not similar at all)'),
            (1, "slightly similar (they're not completely different)"),
            (2, 'fairly similar (some elements of the music sound similar)'),
            (3, 'very similar (fans of one probably like the other)'),
            (4, 'extremely similar (easily mistakable)'),
            (5, 'identical (different name for the same artist)'),
        ])

    def test_default_weight(self):
        self.assertEqual(models.BaseSimilarity().weight, 0)
