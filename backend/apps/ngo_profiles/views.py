from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsNGO
from .models import NGOProfile
from .serializers import NGOProfileSerializer, NGOProfileWriteSerializer


class NGOProfilePublicView(RetrieveAPIView):
    """GET /ngo-profile/:userId/ — public, no auth required."""

    queryset = NGOProfile.objects.select_related("user")
    serializer_class = NGOProfileSerializer
    permission_classes = [AllowAny]
    lookup_url_kwarg = "user_id"
    lookup_field = "user_id"


class MyNGOProfileView(APIView):
    """GET/PUT /ngo-profile/ — the logged-in NGO's own profile.
    get_or_create semantics: an NGO account might not have created its
    profile yet, so GET/PUT both work from a blank slate."""

    permission_classes = [IsAuthenticated, IsNGO]

    def get(self, request):
        profile, _ = NGOProfile.objects.get_or_create(
            user=request.user, defaults={"organization_name": request.user.full_name}
        )
        return Response(NGOProfileSerializer(profile).data)

    def put(self, request):
        profile, _ = NGOProfile.objects.get_or_create(
            user=request.user, defaults={"organization_name": request.user.full_name}
        )
        serializer = NGOProfileWriteSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(NGOProfileSerializer(profile).data, status=status.HTTP_200_OK)
