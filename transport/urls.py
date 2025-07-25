from django.urls import path
from . import views

urlpatterns = [
    path("", views.request_transport, name="home"),
    path("select/<int:vendor_id>/", views.select_vendor, name="select_vendor"),  # <- add this line
]
