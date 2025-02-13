from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', views.list_order, name='list_order'),
    path('new/', views.create_order, name='create_order'),
    path('edit/<int:pk>/', views.edit_order, name='update_order'),
    path('delete/<int:pk>/', views.delete_order, name='order_delete'),
    path('search/', views.search_order, name='order_search'),
    path('revenue/', views.calculate_revenue, name='calculate_revenue'),
    path('api/', include(router.urls)),
]
