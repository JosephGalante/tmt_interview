from django.urls import path
from interview.order.views import (
    DeactivateOrderView,
    OrderListCreateView,
    OrderTagListCreateView,
)


urlpatterns = [
    path(
        "<int:id>/deactivate/", DeactivateOrderView.as_view(), name="order-deactivate"
    ),
    path("tags/", OrderTagListCreateView.as_view(), name="order-detail"),
    path("", OrderListCreateView.as_view(), name="order-list"),
]
