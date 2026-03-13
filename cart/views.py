from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, AddToCartSerializer, UpdateCartItemSerializer
)
from products.models import Product


class CartView(APIView):
    """
    GET /api/cart/?user_identifier=<id>  - View cart items for a user
    POST /api/cart/                       - Add a product to cart
    """

    def get(self, request):
        user_identifier = request.query_params.get('user_identifier')
        if not user_identifier:
            return Response(
                {"error": "user_identifier query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart = get_object_or_404(Cart, user_identifier=user_identifier)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        """Add a product to the cart. Creates cart if it doesn't exist."""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_identifier = serializer.validated_data['user_identifier']
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        # Validate product exists
        product = get_object_or_404(Product, id=product_id)

        # Check if product has enough stock
        if product.stock_quantity < quantity:
            return Response(
                {
                    "error": f"Insufficient stock. Only {product.stock_quantity} unit(s) available.",
                    "available_stock": product.stock_quantity
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create cart
        cart, _ = Cart.objects.get_or_create(user_identifier=user_identifier)

        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # Item already in cart — increase quantity
            new_quantity = cart_item.quantity + quantity
            if product.stock_quantity < new_quantity:
                return Response(
                    {
                        "error": f"Cannot add {quantity} more. Only {product.stock_quantity - cart_item.quantity} additional unit(s) available.",
                        "available_stock": product.stock_quantity,
                        "already_in_cart": cart_item.quantity
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()

        cart_serializer = CartSerializer(cart)
        return Response(
            {
                "message": "Product added to cart." if created else "Cart item quantity updated.",
                "cart": cart_serializer.data
            },
            status=status.HTTP_200_OK
        )


class CartItemDetailView(APIView):
    """
    PATCH  /api/cart/items/<item_id>/  - Update item quantity
    DELETE /api/cart/items/<item_id>/  - Remove item from cart
    """

    def patch(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_quantity = serializer.validated_data['quantity']
        product = cart_item.product

        # Check stock
        if product.stock_quantity < new_quantity:
            return Response(
                {
                    "error": f"Insufficient stock. Only {product.stock_quantity} unit(s) available.",
                    "available_stock": product.stock_quantity
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = new_quantity
        cart_item.save()

        cart_serializer = CartSerializer(cart_item.cart)
        return Response(
            {"message": "Cart item updated.", "cart": cart_serializer.data}
        )

    def delete(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        product_name = cart_item.product.name
        cart = cart_item.cart
        cart_item.delete()

        cart_serializer = CartSerializer(cart)
        return Response(
            {
                "message": f"'{product_name}' removed from cart.",
                "cart": cart_serializer.data
            },
            status=status.HTTP_200_OK
        )


class ClearCartView(APIView):
    """
    DELETE /api/cart/clear/?user_identifier=<id>  - Clear entire cart
    """

    def delete(self, request):
        user_identifier = request.query_params.get('user_identifier')
        if not user_identifier:
            return Response(
                {"error": "user_identifier query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart = get_object_or_404(Cart, user_identifier=user_identifier)
        cart.items.all().delete()
        return Response({"message": "Cart cleared successfully."}, status=status.HTTP_200_OK)
