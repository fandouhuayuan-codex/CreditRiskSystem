from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class AdminUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('auditor', '风控审核'),
        ('viewer', '只读'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    # 必须加这两个，否则和原生User冲突
    groups = models.ManyToManyField(
        Group,
        verbose_name='用户组',
        blank=True,
        related_name="risk_admin_users",
        related_query_name="risk_admin_user"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='权限',
        blank=True,
        related_name="risk_admin_users",
        related_query_name="risk_admin_user"
    )


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


class RiskAlert(models.Model):
    """风险告警表：高风险客户预测时自动生成，支持人工复核"""
    STATUS_CHOICES = (
        ('pending', '待复核'),
        ('reviewed', '已复核'),
        ('ignored', '已忽略'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    input_features = models.JSONField()
    predicted_proba = models.FloatField()
    model_name = models.CharField(max_length=64, default='XGBoost')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'告警-{self.customer_id or "匿名"}-{self.predicted_proba:.2f}-{self.get_status_display()}'
