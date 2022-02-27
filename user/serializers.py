from rest_framework import serializers
from user.models import User, Log
from .utils import password_validator

class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        """
            Override the `create` method of the ModelSerializer

            Args:
                validated_data: dict, data passed to the serializer

            Return:
                User: the user object
        """
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
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserUpdateSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        """
            Update the user object

            Args:
                instance: User, current user object
                validated_data: dict, the data passed to the serializer to 
                                update
            
            Return:
                User: current user object
        """
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
        """
            Delete current User object, password must be checked            
            
            Args:
                instance: User, current user object
                validated_data: dict, the data passed to the serializer to      
                                check the password

            Return:
                User: deleted user object
        """
        if not instance.check_password(validated_data.get('password', None)):
            raise serializers.ValidationError({'detail': 'Password does not match'})
        instance.delete()
        return instance

class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = ['id', 'user', 'action', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True},
            'action': {'read_only': True}
        }
