from django.urls import path

from app import views

urlpatterns = [
    # auth
    path("auth/signup", views.SignupView.as_view(), name="signup"),
    path("auth/login", views.LoginView.as_view(), name="login"),
    path("auth/logout", views.LogoutView.as_view(), name="logout"),
    path("auth/me", views.MeView.as_view(), name="me"),
    # parcels
    path("parcels/me", views.ListMyParcelsView.as_view(), name="list-my-parcels"),
    path("parcels", views.CreateParcelView.as_view(), name="create-parcel"),
    path("parcels/<int:parcel_id>", views.ParcelDetailView.as_view(), name="parcel-detail"),
    path("parcels/<int:parcel_id>/destination", views.UpdateDestinationView.as_view(), name="parcel-destination"),
    path("parcels/<int:parcel_id>/cancel", views.CancelParcelView.as_view(), name="parcel-cancel"),
    path("parcels/<int:parcel_id>/status-history", views.StatusHistoryView.as_view(), name="parcel-status-history"),
    path("parcels/<int:parcel_id>/tracking", views.TrackingView.as_view(), name="parcel-tracking"),
    # admin
    path("admin/parcels", views.AdminListParcelsView.as_view(), name="admin-list-parcels"),
    path("admin/parcels/<int:parcel_id>/status", views.AdminUpdateStatusView.as_view(), name="admin-parcel-status"),
    path("admin/parcels/<int:parcel_id>/location", views.AdminUpdateLocationView.as_view(), name="admin-parcel-location"),
]
