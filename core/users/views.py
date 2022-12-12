from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAdminUser, 
    IsAuthenticated, 
    AllowAny
    )
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer
from .models import User
from .permissions import UserIsAuthorized
from .utils.tokens import email_activation_token_generator

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
        'retrieve', 
        'update', 
        'partial_update', 
        'destroy', 
        'deactivate', 
        'reset_password'
        ]

    def get_permissions(self):
        if self.action in ('list', 'create', 'email_activate_user'):
            self.permission_classes = [AllowAny]
        if self.action in self.object_level_actions:
            self.permission_classes = [UserIsAuthorized]
        if self.action == 'test':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        if response.status_code == 201:
            email_address = request.data.get('email')
            token = email_activation_token_generator.make_token(user)
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            send_mail(
                'Subject here',
                f'''Here is the message. 
                To activate your account visit:  
                http://127.0.0.1:8000/api/users/email_activate_user?id={encoded_pk}&token={token}
                ''',
                'from@example.com',
                [f'{email_address}'],
                fail_silently=False,
            )
        
        return response
    
    @action(methods=['get'], detail=True)
    def admin_activate_user(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = True
        instance.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def email_activate_user(self, request):
        encoded_pk = request.query_params.get('id')
        token = request.query_params.get('token')
        if encoded_pk and token:
            decoded_pk = force_str(urlsafe_base64_decode(encoded_pk))
            instance = get_object_or_404(self.get_queryset(), pk=decoded_pk)
            if email_activation_token_generator.check_token(user=instance, token=token):
                instance.is_active = True
                instance.save()
                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def deactivate(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['get', 'post'], detail=True)
    def reset_password(self, request, pk=None):
        pass
        
    @action(methods=['get', 'post'], detail=False)
    def test(self, request):
        data = {
            "test": "hello"
        }
        return Response(status=status.HTTP_200_OK, data=data)


