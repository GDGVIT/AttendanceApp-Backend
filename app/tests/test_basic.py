import unittest
from .. import *
import unittest

# pytest -v
# python -m unitest


class TestMyApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_404(self):
        result = self.app.get('/other')
        self.assertEqual(result.status, '404 NOT FOUND')

    def setUp(self):
        app.testing = True
        self.app = app.test_client()