from django.urls import path

from . import views

urlpatterns = [
    path("nodes", views.NodeListCreateView.as_view(), name="node-list"),
    path("nodes/<int:pk>", views.NodeDestroyView.as_view(), name="node-detail"),
    path("edges", views.EdgeListCreateView.as_view(), name="edge-list"),
    path("edges/<int:pk>", views.EdgeDestroyView.as_view(), name="edge-detail"),
    path("routes/shortest", views.ShortestRouteView.as_view(), name="route-shortest"),
    path("routes/history", views.RouteHistoryView.as_view(), name="route-history"),
]
