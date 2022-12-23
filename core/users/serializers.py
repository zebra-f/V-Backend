import smtplib

from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError, APIException

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from core.users.models import User, UserPersonalProfile
from core.users.utils.emails import ActivationEmailMessage, PasswordResetEmailMessage
from .utils.tokens import activate_user_token_generator, custom_password_reset_token_generator


class PasswordValidatorMixin:
    def custom_validate_password(self, instance, validated_data):
        password = validated_data['password']
        try:
            validate_password(password, instance)
        except ValidationError as e:
            raise DRFValidationError({'password': e.messages})
        return password


class EmailMessageMixin:
    def email_token(self, instance, token_generator, EmailMessage):
        encoded_pk = urlsafe_base64_encode(force_bytes(instance.pk))
        token = token_generator.make_token(instance)
        email_message = EmailMessage(
            encoded_pk=encoded_pk, 
            token=token, 
            to=[instance.email]
            )
        try:
            email_message.send(fail_silently=False)
        except smtplib.SMTPException: 
            exc = APIException()
            exc.status_code = 503
            exc.default_detail = 'Service temporarily unavailable, try again later.'
            exc.default_code = 'service_unavailable'
            raise exc 


class UserSerializer(serializers.ModelSerializer, PasswordValidatorMixin, EmailMessageMixin):
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}}

    def create(self, validated_data):
        instance = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        password = self.custom_validate_password(instance, validated_data)
        instance.set_password(password)

        self.email_token(instance, activate_user_token_generator, ActivationEmailMessage)

        instance.save()
        user_personal_profile = UserPersonalProfile(
            user=instance
        )
        user_personal_profile.save()
        return instance

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        if validated_data.get('password'):
            password = self.custom_validate_password(instance, validated_data)
            instance.set_password(password)
        instance.save()
        return instance


class UserPasswordResetSerializer(serializers.Serializer, PasswordValidatorMixin, EmailMessageMixin):
    password = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
            
    def email_is_valid(self, validated_data, queryset):
        if not validated_data.get('email'):
            raise DRFValidationError({'email': ['This field is required.']})
        user = get_object_or_404(queryset, email=validated_data['email'])
        return user

    def send_reset_password_email(self, instance):
        self.email_token(instance, custom_password_reset_token_generator, PasswordResetEmailMessage)

    def update(self, instance, validated_data):
        if not validated_data.get('password'):
            raise DRFValidationError({'password': ['This field is required.']})
        password = self.custom_validate_password(instance, validated_data)
        instance.set_password(password)
        instance.save()
        return instance