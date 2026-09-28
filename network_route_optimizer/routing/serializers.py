from rest_framework import serializers

from .models import Edge, Node, RouteQuery


class NodeNameField(serializers.SlugRelatedField):
    default_error_messages = {"does_not_exist": 'Node "{value}" does not exist.'}

    def __init__(self, **kwargs):
        super().__init__(slug_field="name", queryset=Node.objects.all(), **kwargs)


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ["id", "name"]


class EdgeSerializer(serializers.ModelSerializer):
    source = NodeNameField()
    destination = NodeNameField()

    class Meta:
        model = Edge
        fields = ["id", "source", "destination", "latency"]

    def validate_latency(self, value):
        if value <= 0:
            raise serializers.ValidationError("Latency must be greater than 0.")
        return value


class ShortestRouteRequestSerializer(serializers.Serializer):
    source = NodeNameField()
    destination = NodeNameField()


class RouteQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteQuery
        fields = ["id", "source", "destination", "total_latency", "path", "created_at"]


class RouteHistoryFilterSerializer(serializers.Serializer):
    source = serializers.CharField(required=False)
    destination = serializers.CharField(required=False)
    limit = serializers.IntegerField(required=False, min_value=1)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
