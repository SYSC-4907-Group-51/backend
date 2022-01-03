from rest_framework import serializers
from user.models import User
from .utils import password_validator

class UserRegisterSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        errors = password_validator(User(**validated_data), validated_data.get('password'))
        if errors:
            raise serializers.ValidationError(errors)
        else:
            user = super().create(validated_data)
            user.set_password(validated_data['password'])
            user.save()
            return user

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserUpdateSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        errors = dict()
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        if validated_data.get('password', None):
            errors = password_validator(instance, validated_data.get('password'))
        if errors:
            raise serializers.ValidationError(errors)
        else:
            instance.save()
            return instance

class UserDeleteSerializer(serializers.Serializer):

    def delete(self, instance, validated_data):
        if not instance.check_password(validated_data.get('password', None)):
            raise serializers.ValidationError({'detail': 'Password does not match'})
        instance.delete()
        return instance