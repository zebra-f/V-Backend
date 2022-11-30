from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from ..users.models import User


class CustomTokenBlacklistView(TokenBlacklistView):

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs) 


class LogoutView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        user = request.user
        user.last_logout = timezone.now()
        user.save()

        return super().post(request, *args, **kwargs) 


class LoginView(TokenObtainPairView):
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.get(email=request.data['email'])
            user.last_login = timezone.now()
            user.save()
        
        return response