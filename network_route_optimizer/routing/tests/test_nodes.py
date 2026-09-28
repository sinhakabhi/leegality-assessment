from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from routing.models import Node


class NodeTests(APITestCase):
    url = reverse("node-list")

    def test_create_node(self):
        response = self.client.post(self.url, {"name": "ServerA"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {"id": Node.objects.get().id, "name": "ServerA"})

    def test_missing_name_returns_400(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_duplicate_name_returns_400(self):
        Node.objects.create(name="ServerA")

        response = self.client.post(self.url, {"name": "ServerA"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_nodes(self):
        Node.objects.create(name="ServerA")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_delete_node(self):
        node = Node.objects.create(name="ServerA")

        response = self.client.delete(reverse("node-detail", args=[node.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Node.objects.exists())
