from django.db.models import Prefetch
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from interview.order.models import Order, OrderTag
from interview.order.serializers import OrderSerializer, OrderTagSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrdersOnTagView(APIView):
    def get(self, request, id):
        order_queryset = (
            Order.objects.select_related(
                "inventory",
                "inventory__type",
                "inventory__language",
            )
            .prefetch_related("inventory__tags", "tags")
            .order_by("id")
        )
        tag = generics.get_object_or_404(
            OrderTag.objects.prefetch_related(
                Prefetch("orders", queryset=order_queryset)
            ),
            id=id,
        )
        serializer = OrderSerializer(tag.orders.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderTagListCreateView(generics.ListCreateAPIView):
    queryset = OrderTag.objects.all()
    serializer_class = OrderTagSerializer
