import unittest

from config.settings import APP_FILE
from utilities.driver_factory import create_driver
from utilities.server import start_static_server


class CarePointUnittestExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_static_server(APP_FILE.parent)
        cls.driver = create_driver()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server.shutdown()
        cls.server.server_close()

    def test_mock_page_title(self):
        self.driver.get(self.url)
        self.assertIn("Jeevadhara", self.driver.title)


if __name__ == "__main__":
    unittest.main()
