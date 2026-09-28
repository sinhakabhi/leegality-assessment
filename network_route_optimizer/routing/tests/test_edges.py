from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from routing.models import Edge, Node


class EdgeTests(APITestCase):
    url = reverse("edge-list")

    @classmethod
    def setUpTestData(cls):
        cls.a = Node.objects.create(name="ServerA")
        cls.b = Node.objects.create(name="ServerB")

    def post(self, **overrides):
        payload = {"source": "ServerA", "destination": "ServerB", "latency": 12.5, **overrides}
        return self.client.post(self.url, payload, format="json")

    def test_create_edge(self):
        response = self.post()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {
                "id": Edge.objects.get().id,
                "source": "ServerA",
                "destination": "ServerB",
                "latency": 12.5,
            },
        )

    def test_missing_source_or_destination_returns_400(self):
        for field in ("source", "destination"):
            with self.subTest(field=field):
                response = self.post(**{field: None})

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_positive_latency_returns_400(self):
        for latency in (0, -5):
            with self.subTest(latency=latency):
                response = self.post(latency=latency)

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_edge_returns_400(self):
        self.post()

        response = self.post()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "error": {
                    "non_field_errors": [
                        "An edge from this source to this destination already exists."
                    ]
                }
            },
        )
        self.assertEqual(Edge.objects.count(), 1)

    def test_unknown_node_returns_400(self):
        response = self.post(destination="ServerZ")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"error": {"destination": ['Node "ServerZ" does not exist.']}}
        )

    def test_list_edges(self):
        self.post()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_delete_edge(self):
        edge = Edge.objects.create(source=self.a, destination=self.b, latency=1)

        response = self.client.delete(reverse("edge-detail", args=[edge.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Edge.objects.exists())
