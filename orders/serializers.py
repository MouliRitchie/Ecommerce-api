from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_identifier', 'total_amount', 'order_status', 'items', 'created_at']
        read_only_fields = ['total_amount', 'order_status', 'created_at']


class PlaceOrderSerializer(serializers.Serializer):
    user_identifier = serializers.CharField(max_length=255)


class UpdateOrderStatusSerializer(serializers.Serializer):
    order_status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
