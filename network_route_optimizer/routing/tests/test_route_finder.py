from decimal import Decimal as D

from django.test import SimpleTestCase

from routing.services.route_finder import Route, find_shortest_path


class FindShortestPathTests(SimpleTestCase):
    def test_returns_lowest_latency_path(self):
        edges = [("A", "D", D("30")), ("A", "B", D("12.5")), ("B", "D", D("10.9"))]

        self.assertEqual(find_shortest_path(edges, "A", "D"), Route(D("23.4"), ["A", "B", "D"]))

    def test_returns_none_when_unreachable(self):
        edges = [("A", "B", D("1"))]

        self.assertIsNone(find_shortest_path(edges, "B", "A"))
