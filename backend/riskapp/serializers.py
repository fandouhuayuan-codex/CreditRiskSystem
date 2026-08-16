from rest_framework import serializers
from .models import CreditCustomer, TrainingLog, PredictHistory, FeatureWeight


class CreditCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCustomer
        fields = '__all__'


class TrainingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingLog
        fields = '__all__'


class PredictHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictHistory
        fields = '__all__'


class FeatureWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureWeight
        fields = '__all__'
