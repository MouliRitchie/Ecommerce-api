from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderHistoryView.as_view(), name='order-history'),
    path('place/', views.PlaceOrderView.as_view(), name='place-order'),
    path('<int:order_id>/', views.OrderHistoryView.as_view(), name='order-detail'),
    path('<int:order_id>/status/', views.UpdateOrderStatusView.as_view(), name='order-status-update'),
]
