from rest_framework import serializers
from user.models import User, Log
from visualize.models import Key

class KeySerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField(method_name='get_permissions')

    def get_permissions(self, obj):
        return [
            obj.allow_step_time_series,
            obj.allow_heartrate_time_series,
            obj.allow_sleep_time_series,
            obj.allow_step_intraday_data,
            obj.allow_heartrate_intraday_data
        ]

    class Meta:
        model = Key
        fields = ['user', 'key', 'notes', 'permissions', 'created_at', 'allow_step_time_series', 'allow_heartrate_time_series', 'allow_sleep_time_series', 'allow_step_intraday_data', 'allow_heartrate_intraday_data']
        extra_kwargs = {
            'user': {'write_only': True},
            'allow_step_time_series': {'write_only': True},
            'allow_heartrate_time_series': {'write_only': True},
            'allow_sleep_time_series': {'write_only': True},
            'allow_step_intraday_data': {'write_only': True},
            'allow_heartrate_intraday_data': {'write_only': True}
        }

class KeyDeleteSerializer(serializers.Serializer):

    def delete(self, instance, validated_data):
        key = Key.objects.filter(user=instance, **validated_data)
        if not key:
            raise serializers.ValidationError({'detail': 'Invalid key'})
        key.delete()
        return key
