from rest_framework import serializers
from user.models import User, Log
from visualize.models import Key

class KeyShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Key
        fields = ['key', 'notes', 'created_at']

class KeyDeleteSerializer(serializers.Serializer):

    def delete(self, instance, validated_data):
        key = Key.objects.filter(user=instance, **validated_data)
        if not key:
            raise serializers.ValidationError({'detail': 'Invalid key'})
        key.delete()
        return key
