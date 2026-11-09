from django.contrib import admin
from .models import AdminUser, CreditCustomer, TrainingLog, PredictHistory, FeatureWeight, RiskAlert
from django.contrib.auth.admin import UserAdmin

admin.site.register(AdminUser, UserAdmin)
admin.site.register(CreditCustomer)
admin.site.register(TrainingLog)
admin.site.register(PredictHistory)
admin.site.register(FeatureWeight)
admin.site.register(RiskAlert)
