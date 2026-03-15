from datetime import datetime

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from interview.order.models import Order, OrderTag
from interview.order.serializers import OrderSerializer, OrderTagSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        embargo_date = self.request.query_params.get("embargo_date")

        queryset = self.queryset.order_by("start_date", "id")

        # Ensure that if no date filters are provided, all orders are returned
        if not start_date and not embargo_date:
            return queryset

        # Ensure that both start_date and embargo_date are provided
        if not start_date or not embargo_date:
            raise ValueError("start_date and embargo_date are both required.")

        try:
            start_date_value = datetime.strptime(start_date, "%Y-%m-%d").date()
            embargo_date_value = datetime.strptime(embargo_date, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(
                "start_date and embargo_date must be valid dates in YYYY-MM-DD format."
            ) from exc

        if start_date_value > embargo_date_value:
            raise ValueError("start_date must be on or before embargo_date.")

        return queryset.filter(
            start_date__gte=start_date_value,
            embargo_date__lte=embargo_date_value,
        )

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class DeactivateOrderView(APIView):
    def patch(self, request, id):
        order = generics.get_object_or_404(Order, id=id)
        order.is_active = False
        order.save(update_fields=["is_active"])

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderTagListCreateView(generics.ListCreateAPIView):
    queryset = OrderTag.objects.all()
    serializer_class = OrderTagSerializer
