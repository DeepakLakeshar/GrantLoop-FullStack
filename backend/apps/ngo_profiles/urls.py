from django.urls import path

from .views import MyNGOProfileView, NGOProfilePublicView

urlpatterns = [
    path("", MyNGOProfileView.as_view(), name="ngo-profile-mine"),
    path("<uuid:user_id>/", NGOProfilePublicView.as_view(), name="ngo-profile-public"),
]
