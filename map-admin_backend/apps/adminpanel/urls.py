from django.urls import path
from .views import AdminParcelListView, AdminParcelUpdateView

urlpatterns = [
    path('admin/parcels/', AdminParcelListView.as_view(), name='admin-parcel-list'),
    path('admin/parcels/<int:pk>/', AdminParcelUpdateView.as_view(), name='admin-parcel-update'),
]
