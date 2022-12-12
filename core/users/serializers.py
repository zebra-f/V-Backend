from rest_framework import serializers

from core.users.models import User, UserPersonalProfile


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        
        user_personal_profile = UserPersonalProfile(
            user=user
        )
        user_personal_profile.save()
        
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        
        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance

