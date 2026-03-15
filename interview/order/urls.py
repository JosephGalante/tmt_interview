from django.urls import path
from interview.order.views import (
    OrderListCreateView,
    OrdersOnTagView,
    OrderTagListCreateView,
)


urlpatterns = [
    path("tags/<int:id>/orders/", OrdersOnTagView.as_view(), name="tag-orders"),
    path("tags/", OrderTagListCreateView.as_view(), name="order-detail"),
    path("", OrderListCreateView.as_view(), name="order-list"),
]
