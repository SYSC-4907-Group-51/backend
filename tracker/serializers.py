from tracker.models import *
from rest_framework import serializers

class UserStepTimeSeriesSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='date_time')
    class Meta:
        model = UserStepTimeSeries
        fields = ['date', 'steps']

class UserHeartrateTimeSeriesSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='date_time')
    class Meta:
        model = UserHeartrateTimeSeries
        fields = ['date', 'resting_heartrate', 'heartrate_zones']

class UserSleepTimeSeriesSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='date_time')
    class Meta:
        model = UserSleepTimeSeries
        fields = ['date', 'duration', 'efficiency', 'start_time', 'end_time', 'minutes_after_wakeup', 'minutes_asleep', 'minutes_awake', 'minutes_to_fall_asleep', 'time_in_bed', 'levels', 'summary']

class UserStepIntradayDataSerializer(serializers.ModelSerializer):
    time_series = UserStepTimeSeriesSerializer()
    class Meta:
        model = UserStepIntradayData
        fields = ['time_series', 'dataset', 'dataset_interval', 'dataset_type']

class UserHeartrateIntradayDataSerializer(serializers.ModelSerializer):
    time_series = UserHeartrateTimeSeriesSerializer()
    class Meta:
        model = UserHeartrateIntradayData
        fields = ['time_series', 'dataset', 'dataset_interval', 'dataset_type']

class UserSyncStatusSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='date_time')
    status = serializers.JSONField(source='get_sync_status')
    class Meta:
        model = UserSyncStatus
        fields = ['date', 'status']