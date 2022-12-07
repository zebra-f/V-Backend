from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAdminUser, 
    IsAuthenticated, 
    AllowAny
    )

from .serializers import UserSerializer
from .models import User
from .permissions import UserIsAuthorized

# class UserViewSet(viewsets.ViewSet):
#     """
#     A simple ViewSet for listing or retrieving users.
#     """
#     def list(self, request):
#         queryset = User.objects.all()
#         serializer = UserSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = User.objects.all()
#         user = get_object_or_404(queryset, pk=pk)
#         serializer = UserSerializer(user)
#         return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):  
    queryset = User.objects.all() 
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    object_level_actions = [
        'retrieve', 'update', 'partial_update', 'destroy', 'activate', 'deactivate'
        ]

    def get_permissions(self):
        if self.action in ('list', 'create'):
            self.permission_classes = [AllowAny]
        if self.action in self.object_level_actions:
            self.permission_classes = [UserIsAuthorized]
        return super().get_permissions()

    @action(methods=['post'], detail=True)
    def activate(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = True
        instance.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def deactivate(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_200_OK)


