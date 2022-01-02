from rest_framework import serializers
from user.models import User

class UserRegisterSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
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
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        if validated_data.get('password', None):
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

class UserDeleteSerializer(serializers.Serializer):

    def delete(self):
        request = self.context['request']
        user = request.user
        password = request.data.get('password', None)
        if not user.check_password(password):
            raise serializers.ValidationError({'detail': 'Password does not match'})
        user.delete()
        return user