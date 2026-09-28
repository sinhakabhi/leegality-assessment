from datetime import UTC, datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from routing.models import RouteQuery


def make_query(source, destination, created_at):
    record = RouteQuery.objects.create(
        source=source, destination=destination, total_latency=10, path=[source, destination]
    )
    RouteQuery.objects.filter(pk=record.pk).update(created_at=created_at)
    return record


class RouteHistoryTests(APITestCase):
    url = reverse("route-history")

    @classmethod
    def setUpTestData(cls):
        cls.first = make_query("ServerA", "ServerD", datetime(2026, 2, 20, 14, 32, tzinfo=UTC))
        cls.second = make_query("ServerB", "ServerC", datetime(2026, 2, 20, 15, 10, tzinfo=UTC))

    def get_ids(self, **params):
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [item["id"] for item in response.json()]

    def test_list_history(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()[-1],
            {
                "id": self.first.id,
                "source": "ServerA",
                "destination": "ServerD",
                "total_latency": 10.0,
                "path": ["ServerA", "ServerD"],
                "created_at": "2026-02-20T14:32:00Z",
            },
        )

    def test_filter_by_source_and_destination(self):
        self.assertEqual(self.get_ids(source="ServerA"), [self.first.id])
        self.assertEqual(self.get_ids(destination="ServerC"), [self.second.id])

    def test_filter_by_date(self):
        ids = self.get_ids(date_from="2026-02-20T15:00:00Z", date_to="2026-02-20T16:00:00Z")

        self.assertEqual(ids, [self.second.id])

    def test_limit(self):
        self.assertEqual(len(self.get_ids(limit=1)), 1)
