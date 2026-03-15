from django.db.models import Prefetch
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from interview.order.models import Order, OrderTag
from interview.order.serializers import OrderSerializer, OrderTagSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderTagListView(APIView):
    def get(self, request, id):
        order = generics.get_object_or_404(
            Order.objects.prefetch_related(
                Prefetch("tags", queryset=OrderTag.objects.order_by("id"))
            ),
            id=id,
        )
        serializer = OrderTagSerializer(order.tags.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderTagListCreateView(generics.ListCreateAPIView):
    queryset = OrderTag.objects.all()
    serializer_class = OrderTagSerializer
