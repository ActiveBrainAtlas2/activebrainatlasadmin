from abakit.lib.python_util import read_file
import os
from django.test import TestCase
from django.utils import timezone

from neuroglancer.models import UrlModel
import neuroglancer

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        print(neuroglancer.__file__)
        test_folder = os.path.dirname(__file__)
        ng_state_file = test_folder + '/test_neuroglancer_state_volume'
        test_neuroglancer_state = read_file(ng_state_file)
        url = UrlModel(url = test_neuroglancer_state,comments='test',owner = 1)
        breakpoint()
        # url.save()
        # self.assertEqual(lion.speak(), 'The lion says "roar"')