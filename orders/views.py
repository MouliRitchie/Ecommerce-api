from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer, PlaceOrderSerializer, UpdateOrderStatusSerializer
from cart.models import Cart


class PlaceOrderView(APIView):
    """
    POST /api/orders/place/
    Places an order from the user's current cart.
    - Validates stock for every item
    - Decreases stock on success
    - Clears the cart on success
    """

    @transaction.atomic
    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_identifier = serializer.validated_data['user_identifier']

        # Get the user's cart
        try:
            cart = Cart.objects.prefetch_related('items__product').get(
                user_identifier=user_identifier
            )
        except Cart.DoesNotExist:
            return Response(
                {"error": "No cart found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response(
                {"error": "Cart is empty. Add products before placing an order."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Stock validation pass (before any writes) ---
        stock_errors = []
        for item in cart_items:
            product = item.product
            if product.stock_quantity < item.quantity:
                stock_errors.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "requested": item.quantity,
                    "available": product.stock_quantity
                })

        if stock_errors:
            return Response(
                {
                    "error": "Some products do not have sufficient stock.",
                    "stock_issues": stock_errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Create order ---
        total_amount = cart.total_price
        order = Order.objects.create(
            user_identifier=user_identifier,
            total_amount=total_amount,
            order_status=Order.STATUS_PENDING
        )

        # --- Create order items & decrement stock ---
        for item in cart_items:
            product = item.product
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_price=product.price,
                quantity=item.quantity
            )
            # Decrease stock
            product.stock_quantity -= item.quantity
            product.save()

        # --- Clear cart ---
        cart_items.delete()

        order_serializer = OrderSerializer(order)
        return Response(
            {
                "message": "Order placed successfully.",
                "order": order_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class OrderHistoryView(APIView):
    """
    GET /api/orders/?user_identifier=<id>  - View all orders for a user
    GET /api/orders/<order_id>/            - View a specific order
    """

    def get(self, request, order_id=None):
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            serializer = OrderSerializer(order)
            return Response(serializer.data)

        user_identifier = request.query_params.get('user_identifier')
        if not user_identifier:
            return Response(
                {"error": "user_identifier query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        orders = Order.objects.filter(
            user_identifier=user_identifier
        ).prefetch_related('items').order_by('-created_at')

        serializer = OrderSerializer(orders, many=True)
        return Response({
            "user": user_identifier,
            "total_orders": orders.count(),
            "orders": serializer.data
        })


class UpdateOrderStatusView(APIView):
    """
    PATCH /api/orders/<order_id>/status/  - Update order status
    """

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['order_status']

        # Restore stock if cancelling a pending order
        if new_status == Order.STATUS_CANCELLED and order.order_status == Order.STATUS_PENDING:
            for item in order.items.all():
                if item.product:
                    item.product.stock_quantity += item.quantity
                    item.product.save()

        order.order_status = new_status
        order.save()

        order_serializer = OrderSerializer(order)
        return Response(
            {"message": f"Order status updated to '{new_status}'.", "order": order_serializer.data}
        )
