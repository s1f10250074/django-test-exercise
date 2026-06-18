from django.test import TestCase

# Create your tests here.
class SampleTestCase(TestCase):
    def test_Sample(self):
        self.assertEqual(1 + 2, 3)
