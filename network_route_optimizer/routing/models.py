from django.db import models


class Node(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "nodes"


class Edge(models.Model):
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="outgoing_edges")
    destination = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="incoming_edges")
    latency = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        db_table = "edges"
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"],
                name="unique_edge",
                violation_error_message=(
                    "An edge from the source to this destination already exists."
                ),
            ),
        ]


class RouteQuery(models.Model):
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    total_latency = models.DecimalField(max_digits=12, decimal_places=3)
    path = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "route_queries"
