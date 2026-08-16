from django.db import models
from django.contrib.auth.models import AbstractUser


class AdminUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    ROLE_CHOICES = (
        ('admin','管理员'),
        ('auditor','风控审核'),
        ('viewer','只读'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')


class CreditCustomer(models.Model):
    customer_id = models.CharField(max_length=64, unique=True, db_index=True)
    LIMIT_BAL = models.FloatField(null=True)
    SEX = models.IntegerField(null=True)
    EDUCATION = models.IntegerField(null=True)
    MARRIAGE = models.IntegerField(null=True)
    AGE = models.IntegerField(null=True)
    features_json = models.JSONField(null=True, blank=True)
    label = models.IntegerField(null=True)
    predicted_label = models.IntegerField(null=True, blank=True)
    predicted_proba = models.FloatField(null=True, blank=True)
    predicted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_id


class TrainingLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    dataset_name = models.CharField(max_length=128, default='UCI_default_credit')
    models_metrics = models.JSONField()
    models_params = models.JSONField()
    features = models.JSONField()
    notes = models.TextField(blank=True, null=True)


class PredictHistory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    input_features = models.JSONField()
    predicted_label = models.IntegerField()
    predicted_proba = models.FloatField()
    model_name = models.CharField(max_length=64)


class FeatureWeight(models.Model):
    model_name = models.CharField(max_length=64)
    computed_at = models.DateTimeField(auto_now_add=True)
    weights = models.JSONField()
