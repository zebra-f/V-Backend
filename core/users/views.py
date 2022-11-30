from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action


from .serializers import UserSerializer
from .models import User

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
    # permission_classes = [IsAccountAdminOrReadOnly]

    @action(methods=['post'], detail=True)
    def activate(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = True
        instance.save()

        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def deactivate(self, request, pk=None):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        instance = self.get_object()
        if instance == request.user or request.user.is_admin:
            instance.is_active = False
            instance.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


