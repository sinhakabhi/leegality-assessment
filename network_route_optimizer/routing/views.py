from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import NoRouteFound
from .models import Edge, Node, RouteQuery
from .serializers import (
    EdgeSerializer,
    NodeSerializer,
    RouteHistoryFilterSerializer,
    RouteQuerySerializer,
    ShortestRouteRequestSerializer,
)
from .services.route_finder import find_shortest_path


class NodeListCreateView(generics.ListCreateAPIView):
    queryset = Node.objects.order_by("id")
    serializer_class = NodeSerializer


class NodeDestroyView(generics.DestroyAPIView):
    queryset = Node.objects.all()


class EdgeListCreateView(generics.ListCreateAPIView):
    queryset = Edge.objects.select_related("source", "destination").order_by("id")
    serializer_class = EdgeSerializer


class EdgeDestroyView(generics.DestroyAPIView):
    queryset = Edge.objects.all()


class ShortestRouteView(APIView):
    def post(self, request: Request) -> Response:
        serializer = ShortestRouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        source = serializer.validated_data["source"].name
        destination = serializer.validated_data["destination"].name

        edges = Edge.objects.values_list("source__name", "destination__name", "latency")
        route = find_shortest_path(edges, source, destination)
        if route is None:
            raise NoRouteFound(source, destination)

        RouteQuery.objects.create(
            source=source,
            destination=destination,
            total_latency=route.total_latency,
            path=route.path,
        )
        return Response({"total_latency": route.total_latency, "path": route.path})


class RouteHistoryView(generics.ListAPIView):
    serializer_class = RouteQuerySerializer

    def get_queryset(self):
        filters = RouteHistoryFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        params = filters.validated_data

        queryset = RouteQuery.objects.order_by("-created_at", "-id")
        if "source" in params:
            queryset = queryset.filter(source=params["source"])
        if "destination" in params:
            queryset = queryset.filter(destination=params["destination"])
        if "date_from" in params:
            queryset = queryset.filter(created_at__gte=params["date_from"])
        if "date_to" in params:
            queryset = queryset.filter(created_at__lte=params["date_to"])
        if "limit" in params:
            queryset = queryset[: params["limit"]]
        return queryset
