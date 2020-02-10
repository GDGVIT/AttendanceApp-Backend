import os
import tempfile
import unittest
import pytest

from .. import *

class TestMyApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    # DB connectivity
    @pytest.fixture
    def client():
        db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True

        with app.app.test_client() as client:
            with app.app.app_context():
                app.init_db()
            yield client

        os.close(db_fd)
        os.unlink(app.app.config['DATABASE'])
