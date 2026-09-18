import unittest

from fastapi.testclient import TestClient

from itip_backend.api.main import app


class AppSmokeTests(unittest.TestCase):
    def test_health_endpoint(self):
        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_root_endpoint(self):
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("ITIP Backend", response.json()["service"])


if __name__ == "__main__":
    unittest.main()
