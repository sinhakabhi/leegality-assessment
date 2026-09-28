from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from routing.models import Edge, Node, RouteQuery


class ShortestRouteTests(APITestCase):
    url = reverse("route-shortest")

    @classmethod
    def setUpTestData(cls):
        a, b, d = (Node.objects.create(name=name) for name in ("ServerA", "ServerB", "ServerD"))
        Edge.objects.create(source=a, destination=b, latency=Decimal("12.5"))
        Edge.objects.create(source=b, destination=d, latency=Decimal("10.9"))

    def post(self, source, destination):
        return self.client.post(
            self.url, {"source": source, "destination": destination}, format="json"
        )

    def test_path_exists(self):
        response = self.post("ServerA", "ServerD")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(), {"total_latency": 23.4, "path": ["ServerA", "ServerB", "ServerD"]}
        )
        self.assertEqual(RouteQuery.objects.count(), 1)

    def test_no_path_returns_404(self):
        response = self.post("ServerD", "ServerA")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {"error": "No path exists between ServerD and ServerA"})

    def test_non_existent_node_returns_400(self):
        response = self.post("ServerA", "ServerZ")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
