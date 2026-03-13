from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/products/       - List all products
    POST /api/products/       - Create a new product
    """
    queryset = Product.objects.select_related('category').all().order_by('-created_at')
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Product created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/products/<id>/  - Retrieve a product
    PUT    /api/products/<id>/  - Full update
    PATCH  /api/products/<id>/  - Partial update
    DELETE /api/products/<id>/  - Delete a product
    """
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"message": "Product updated successfully.", "data": serializer.data}
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product_name = instance.name
        self.perform_destroy(instance)
        return Response(
            {"message": f"Product '{product_name}' deleted successfully."},
            status=status.HTTP_200_OK
        )


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/products/categories/  - List all categories
    POST /api/products/categories/  - Create a category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
