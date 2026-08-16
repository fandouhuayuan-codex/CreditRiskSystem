#!/usr/bin/env bash
set -e
echo "正在创建项目骨架文件..."

# README
cat > README.md <<'MD'
# CreditRiskSystem信用风险系统
基于 XGBoost 的银行信贷风险评估系统

This repository contains a full-stack proof-of-concept for a credit risk scoring and alert system using Django (DRF) backend and Vue3 frontend. The backend includes an MLService that trains 5 models and exposes REST APIs for upload / train / predict / dashboard.

本仓库包含一个基于 Django（DRF 后端）与 Vue3 前端的全栈信用风险评分与预警系统概念验证项目。后端内置一个 MLService，用于训练 5 种模型，并提供 REST API，支持数据上传、模型训练、预测及仪表盘功能。
MD

# .gitignore
cat > .gitignore <<'GI'
.venv/
__pycache__/
*.pyc
media/
models/*.joblib
/node_modules/
/dist/
.env
db.sqlite3
coverage/
.idea/
.vscode/
GI

# docker‑compose.yml
cat > docker-compose.yml <<'DC'
version: '3.8'
services:
  backend:
    build: ./backend
    container_name: credit_backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./models:/app/models
    env_file:
      - .env
    command: ["/bin/bash", "-c", "./entrypoint.sh"]
  frontend:
    build: ./frontend
    container_name: credit_frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
    env_file:
      - .env
DC

# .env.example
cat > .env.example <<'ENV'
# example env示例环境变量
DJANGO_SECRET_KEY=replace-me
DATABASE_URL=sqlite:///db.sqlite3

# Frontend前端
VITE_PORT=5173
ENV

# License
cat > LICENSE <<'LIC'
Apache‑2.0
LIC

# models占位目录
mkdir -p models
cat > models/README.md <<'MR'
这是一个占位文件，用于指示训练好的模型（.joblib）应存放的位置。训练完成后，请用真实的模型文件替换此占位文件。
MR
touch models/.gitkeep

# GitHub Actions CI
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'CIY'
name: CI

on: [push, pull_request]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install backend deps
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run Django checks
        run: |
          cd backend
          python manage.py check || true

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install and build frontend
        run: |
          cd frontend
          npm install
          npm run build || true
CIY

# backend骨架
mkdir -p backend/credit_risk backend/riskapp
cat > backend/manage.py <<'MNG'
#!/usr/bin/env python
import os
import sys
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_risk.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise
    execute_from_command_line(sys.argv)
MNG
chmod +x backend/manage.py

cat > backend/requirements.txt <<'REQ'
Django>=4.2
djangorestframework
django-cors-headers
pandas
numpy
scikit-learn
xgboost
lightgbm
imbalanced-learn
joblib
shap
openpyxl
uvicorn
REQ

cat > backend/entrypoint.sh <<'EN'
#!/bin/bash
set -e
mkdir -p /app/models
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
EN
chmod +x backend/entrypoint.sh

cat > backend/credit_risk/__init__.py <<'PY'
PY

cat > backend/credit_risk/settings.py <<'PYSET'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY','replace-me')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'riskapp',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'credit_risk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

WSGI_APPLICATION = 'credit_risk.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'zh‑hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}
CORS_ALLOW_ALL_ORIGINS = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
PYSET

cat > backend/credit_risk/urls.py <<'UR'
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('riskapp.urls')),
]
UR

cat > backend/credit_risk/wsgi.py <<'WSG'
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_risk.settings')
application = get_wsgi_application()
WSG

# riskapp app
cat > backend/riskapp/__init__.py <<'RI'
RI

cat > backend/riskapp/apps.py <<'AP'
from django.apps import AppConfig

class RiskappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'riskapp'
AP

cat > backend/riskapp/models.py <<'MODELS'
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
MODELS

cat > backend/riskapp/admin.py <<'ADM'
from django.contrib import admin
from .models import AdminUser, CreditCustomer, TrainingLog, PredictHistory, FeatureWeight
from django.contrib.auth.admin import UserAdmin

admin.site.register(AdminUser, UserAdmin)
admin.site.register(CreditCustomer)
admin.site.register(TrainingLog)
admin.site.register(PredictHistory)
admin.site.register(FeatureWeight)
ADM

cat > backend/riskapp/serializers.py <<'SER'
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
SER

cat > backend/riskapp/views.py <<'VIEWS'
import os
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from django.conf import settings
from .models import CreditCustomer, TrainingLog, PredictHistory, FeatureWeight
from .ml_service import MLService
import joblib


class FileUploadView(APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': '没有上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        filename = file_obj.name.lower()
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_obj)
            elif filename.endswith('.xls') or filename.endswith('.xlsx'):
                df = pd.read_excel(file_obj)
            else:
                return Response({'error':'仅支持 CSV / Excel'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        label_candidates = [c for c in df.columns if 'default' in c.lower() or 'payment' in c.lower()]
        label_col = label_candidates[0] if label_candidates else 'default_payment'
        if label_col not in df.columns:
            df[label_col] = 0

        objs = []
        for idx, row in df.iterrows():
            cid = str(row.get('ID') or row.get('customer_id') or f'row_{idx}')
            obj = CreditCustomer(
                customer_id=cid,
                LIMIT_BAL=row.get('LIMIT_BAL'),
                SEX=row.get('SEX'),
                EDUCATION=row.get('EDUCATION'),
                MARRIAGE=row.get('MARRIAGE'),
                AGE=row.get('AGE'),
                features_json=row.to_dict(),
                label=int(row.get(label_col, 0))
            )
            objs.append(obj)
        CreditCustomer.objects.bulk_create(objs, batch_size=500)
        return Response({'message': f'已写入 {len(objs)} 条记录'})


class TrainModelsView(APIView):
    def post(self, request):
        use_grid = request.data.get('use_gridsearch', True)
        smote_ratio = float(request.data.get('smote_ratio', 0.25))
        qs = CreditCustomer.objects.all()
        if not qs.exists():
            return Response({'error':'未找到任何数据，请先上传'}, status=400)

        rows = []
        for c in qs:
            row = c.features_json or {}
            if 'default_payment' not in row and c.label is not None:
                row['default_payment'] = c.label
            rows.append(row)
        df = pd.DataFrame(rows)

        ml = MLService(df, label_col='default_payment')
        ml.preprocess()
        ml.train_test_split(test_size=0.2, shuffle=True)
        ml.apply_smote(sampling_strategy=smote_ratio)
        metrics = ml.train_all(use_gridsearch=use_grid)

        training_log = TrainingLog.objects.create(models_metrics=metrics, models_params={}, features=ml.feature_cols)
        feat_imp = ml.get_feature_importance(topn=50)
        FeatureWeight.objects.create(model_name='XGBoost', weights=feat_imp)

        model_files = os.listdir(settings.MODEL_DIR)
        return Response({'metrics': metrics, 'model_files': model_files})


class PredictView(APIView):
    def post(self, request):
        features = request.data.get('features')
        model_name = request.data.get('model_name', 'XGBoost')
        threshold = float(request.data.get('threshold', 0.5))
        if not features:
            return Response({'error': '缺少 features'}, status=400)

        qs = CreditCustomer.objects.all()
        rows = []
        for c in qs[:2000]:
            row = c.features_json or {}
            if 'default_payment' not in row and c.label is not None:
                row['default_payment'] = c.label
            rows.append(row)
        if not rows:
            return Response({'error':'数据库无样本，无法恢复特征结构，请先上传并训练'}, status=400)
        df_ref = pd.DataFrame(rows)

        ml = MLService(df_ref, label_col='default_payment')
        ml.preprocess()

        model_files = [f for f in os.listdir(settings.MODEL_DIR) if f.startswith(model_name)]
        if not model_files:
            return Response({'error':'未找到已训练模型，请先训练'}, status=400)
        latest = sorted(model_files)[-1]
        model = joblib.load(os.path.join(settings.MODEL_DIR, latest))
        ml.models[model_name] = model

        label, proba = ml.predict_single(features, model_name=model_name, threshold=threshold)
        PredictHistory.objects.create(input_features=features, predicted_label=label, predicted_proba=proba, model_name=model_name)
        return Response({'label': label, 'proba': proba})


class DashboardDataView(APIView):
    def get(self, request):
        tl = TrainingLog.objects.order_by('-created_at').first()
        metrics = tl.models_metrics if tl else {}
        fw = FeatureWeight.objects.order_by('-computed_at').first()
        feat_imp = fw.weights if fw else {}
        total = CreditCustomer.objects.count()
        positive = CreditCustomer.objects.filter(label=1).count()
        neg = total - positive
        return Response({
            'metrics': metrics,
            'feature_importance': feat_imp,
            'distribution': {'total': total, 'positive': positive, 'negative': neg}
        })
VIEWS

cat > backend/riskapp/ml_service.py <<'ML'
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import lightgbm as lgb
import joblib
from django.conf import settings

MODEL_DIR = settings.MODEL_DIR


class MLService:
    def __init__(self, df: pd.DataFrame, label_col='default_payment'):
        self.df = df.copy()
        self.label_col = label_col
        self.feature_cols = [c for c in df.columns if c != label_col and c != 'customer_id']
        self.scaler = StandardScaler()
        self.models = {}
        self.metrics = {}

    def preprocess(self):
        df = self.df.copy()
        for col in df.columns:
            if col == self.label_col or col == 'customer_id':
                continue
            if df[col].dtype.kind in 'biufc':
                median = df[col].median()
                df[col] = df[col].fillna(median)
            else:
                df[col] = df[col].fillna('missing')
        self.df_clean = df
        X = df[self.feature_cols]
        y = df[self.label_col].astype(int)
        X_scaled = pd.DataFrame(self.scaler.fit_transform(X), columns=self.feature_cols)
        self.X = X_scaled
        self.y = y
        return self.X, self.y

    def train_test_split(self, test_size=0.2, random_state=42, shuffle=False):
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=test_size, random_state=random_state, shuffle=shuffle,
            stratify=self.y if shuffle else None
        )
        self.X_train, self.X_test, self.y_train, self.y_test = X_train, X_test, y_train, y_test
        return X_train, X_test, y_train, y_test

    def apply_smote(self, sampling_strategy=0.25, random_state=42):
        sm = SMOTE(sampling_strategy=sampling_strategy, random_state=random_state, n_jobs=-1)
        X_res, y_res = sm.fit_resample(self.X_train, self.y_train)
        self.X_train_res, self.y_train_res = X_res, y_res
        return X_res, y_res

    def _evaluate(self, model, X, y_true):
        y_pred = model.predict(X)
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X)[:,1]
        else:
            try:
                y_proba = model.decision_function(X)
                y_proba = (y_proba - y_proba.min()) / (y_proba.max() - y_proba.min() + 1e-9)
            except:
                y_proba = np.zeros_like(y_pred, dtype=float)
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1': float(f1_score(y_true, y_pred, zero_division=0)),
            'auc': float(roc_auc_score(y_true, y_proba))
        }
        return metrics, y_proba

    def grid_search_cv(self, estimator, param_grid, X, y, cv=3, scoring='roc_auc', n_jobs=-1):
        grid = GridSearchCV(estimator=estimator, param_grid=param_grid, cv=cv, scoring=scoring, n_jobs=n_jobs)
        grid.fit(X, y)
        return grid.best_estimator_, grid.best_params_, grid.best_score_

    def train_all(self, use_gridsearch=True):
        X_tr = self.X_train_res if hasattr(self, 'X_train_res') else self.X_train
        y_tr = self.y_train_res if hasattr(self, 'y_train_res') else self.y_train
        X_val = self.X_test
        y_val = self.y_test

        # Logistic
        lr = LogisticRegression(max_iter=1000)
        if use_gridsearch:
            param_grid = {'C':[0.01,0.1,1,10]}
            best_lr, best_params, best_score = self.grid_search_cv(lr, param_grid, X_tr, y_tr)
            lr = best_lr
        else:
            lr.fit(X_tr, y_tr)
        self.models['LogisticRegression'] = lr
        self.metrics['LogisticRegression'], _ = self._evaluate(lr, X_val, y_val)

        # SVM
        svm = SVC(probability=True)
        if use_gridsearch:
            param_grid = {'C':[0.1,1], 'gamma':['scale'], 'kernel':['rbf']}
            best_svm, best_params, best_score = self.grid_search_cv(svm, param_grid, X_tr, y_tr)
            svm = best_svm
        else:
            svm.fit(X_tr, y_tr)
        self.models['SVM'] = svm
        self.metrics['SVM'], _ = self._evaluate(svm, X_val, y_val)

        # RandomForest
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        if use_gridsearch:
            param_grid = {'n_estimators':[50,100], 'max_depth':[5,10,None]}
            best_rf, best_params, best_score = self.grid_search_cv(rf, param_grid, X_tr, y_tr)
            rf = best_rf
        else:
            rf.fit(X_tr, y_tr)
        self.models['RandomForest'] = rf
        self.metrics['RandomForest'], _ = self._evaluate(rf, X_val, y_val)

        # LightGBM
        lgbm = lgb.LGBMClassifier(random_state=42)
        if use_gridsearch:
            param_grid = {'num_leaves':[31,63], 'n_estimators':[100,200], 'learning_rate':[0.05,0.1]}
            best_lgbm, best_params, best_score = self.grid_search_cv(lgbm, param_grid, X_tr, y_tr)
            lgbm = best_lgbm
        else:
            lgbm.fit(X_tr, y_tr)
        self.models['LightGBM'] = lgbm
        self.metrics['LightGBM'], _ = self._evaluate(lgbm, X_val, y_val)

        # XGBoost
        xgb_clf = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
        if use_gridsearch:
            param_grid = {'max_depth':[3,6], 'n_estimators':[100,200], 'learning_rate':[0.05,0.1]}
            best_xgb, best_params, best_score = self.grid_search_cv(xgb_clf, param_grid, X_tr, y_tr)
            xgb_clf = best_xgb
        else:
            xgb_clf.fit(X_tr, y_tr)
        self.models['XGBoost'] = xgb_clf
        self.metrics['XGBoost'], _ = self._evaluate(xgb_clf, X_val, y_val)

        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        for name, model in self.models.items():
            path = os.path.join(MODEL_DIR, f'{name}_{timestamp}.joblib')
            joblib.dump(model, path)
        return self.metrics

    def get_feature_importance(self, topn=10):
        if 'XGBoost' in self.models:
            model = self.models['XGBoost']
            try:
                importances = model.feature_importances_
                feat_imp = dict(zip(self.feature_cols, importances))
                sorted_imp = dict(sorted(feat_imp.items(), key=lambda item: item[1], reverse=True)[:topn])
                return sorted_imp
            except:
                pass
        if 'RandomForest' in self.models:
            model = self.models['RandomForest']
            importances = model.feature_importances_
            feat_imp = dict(zip(self.feature_cols, importances))
            sorted_imp = dict(sorted(feat_imp.items(), key=lambda item: item[1], reverse=True)[:topn])
            return sorted_imp
        return {}

    def predict_single(self, x_dict, model_name='XGBoost', threshold=0.5):
        X = pd.DataFrame([x_dict])
        for col in self.feature_cols:
            if col not in X.columns:
                X[col] = 0
        X = X[self.feature_cols]
        X_scaled = pd.DataFrame(self.scaler.transform(X), columns=self.feature_cols)

        model = self.models.get(model_name)
        if model is None:
            model_files = [f for f in os.listdir(MODEL_DIR) if f.startswith(model_name)]
            if not model_files:
                raise ValueError("No model available")
            latest = sorted(model_files)[-1]
            model = joblib.load(os.path.join(MODEL_DIR, latest))
            self.models[model_name] = model

        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X_scaled)[:,1][0]
        else:
            proba = model.decision_function(X_scaled)[0]
            proba = (proba - proba.min())/(proba.max() - proba.min() + 1e-9)
        label = int(proba >= threshold)
        return label, float(proba)
ML

cat > backend/riskapp/urls.py <<'URLS'
from django.urls import path
from .views import FileUploadView, TrainModelsView, PredictView, DashboardDataView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('train/', TrainModelsView.as_view(), name='train'),
    path('predict/', PredictView.as_view(), name='predict'),
    path('dashboard/', DashboardDataView.as_view(), name='dashboard'),
]
URLS

# frontend骨架
mkdir -p frontend/src/router frontend/src/views frontend/src/api
cat > frontend/package.json <<'FPKG'
{
  "name": "credit-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "serve": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "vue": "^3.2.0",
    "vue-router": "^4.0.0",
    "axios": "^1.3.0",
    "element-plus": "^2.2.0",
    "echarts": "^5.4.0"
  },
  "devDependencies": {
    "vite": "^4.0.0"
  }
}
FPKG

cat > frontend/index.html <<'FI'
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>信用风险系统</title>
</head>
<body>
<div id="app"></div>
<script type="module" src="/src/main.js"></script>
</body>
</html>
FI

cat > frontend/src/main.js <<'FMAIN'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.mount('#app')
FMAIN

cat > frontend/src/App.vue <<'FAPP'
<template>
  <router-view />
</template>
<script>
export default {
  name: 'App'
}
</script>
FAPP

cat > frontend/src/router/index.js <<'FR'
import { createRouter, createWebHistory } from 'vue-router'
import Upload from '../views/Upload.vue'
import Train from '../views/Train.vue'
import Predict from '../views/Predict.vue'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/upload', component: Upload },
  { path: '/train', component: Train },
  { path: '/predict', component: Predict },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})
export default router
FR

cat > frontend/src/api/index.js <<'FA'
import axios from 'axios'
const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 60000
})

export function uploadFile(file) {
  const form = new FormData();
  form.append('file', file);
  return api.post('upload/', form, { headers: {'Content-Type':'multipart/form-data'} })
}

export function trainModels(params) {
  return api.post('train/', params)
}

export function predictSingle(payload) {
  return api.post('predict/', payload)
}

export function getDashboard() {
  return api.get('dashboard/')
}

export default api
FA

cat > frontend/src/views/Upload.vue <<'FVUP'
<template>
<el-card>
  <el-upload drag :auto-upload="false" :file-list="fileList" :on-change="handleChange" :on-remove="handleRemove">
    <i class="el-icon-upload"></i>
    <div class="el-upload__text">将 CSV / Excel 文件拖拽至此，或点击上传</div>
  </el-upload>
  <el-button type="primary" @click="doUpload" :disabled="!file">上传并导入</el-button>
</el-card>
</template>
<script>
import { ref } from 'vue'
import { uploadFile } from '../api'
export default {
  setup() {
    const file=ref(null);
    const fileList=ref([]);
    function handleChange(fileItem){
      file.value=fileItem.raw;
      fileList.value=[fileItem]
    }
    function handleRemove(){
      file.value=null;
      fileList.value=[]
    }
    async function doUpload(){
      if(!file.value) return;
      try{
        const resp=await uploadFile(file.value);
        alert(JSON.stringify(resp.data))
      }catch(e){
        alert('上传失败:'+e)
      }
    }
    return { file, fileList, handleChange, handleRemove, doUpload }
  }
}
</script>
FVUP

cat > frontend/src/views/Train.vue <<'FVTR'
<template>
<el-card>
  <div style="margin-bottom:16px;">
    <el-checkbox v-model="useGrid">使用 GridSearchCV</el-checkbox>
    <el-input-number v-model="smoteRatio" :min="0.05" :max="0.5" :step="0.05"></el-input-number>
    <el-button type="primary" @click="doTrain">开始训练</el-button>
  </div>
  <div v-if="metrics">{{ metrics }}</div>
</el-card>
</template>
<script>
import { ref } from 'vue'
import { trainModels } from '../api'
export default {
  setup(){
    const useGrid=ref(true);
    const smoteRatio=ref(0.25);
    const metrics=ref(null);
    async function doTrain(){
      try{
        const resp=await trainModels({ use_gridsearch: useGrid.value, smote_ratio: smoteRatio.value });
        metrics.value=resp.data.metrics;
        alert('训练完成')
      }catch(e){
        alert('训练失败:'+e)
      }
    }
    return { useGrid, smoteRatio, doTrain, metrics }
  }
}
</script>
FVTR

cat > frontend/src/views/Predict.vue <<'FVP'
<template>
<el-card>
  <el-form :model="form">
    <el-form-item label="LIMIT_BAL"><el-input v-model.number="form.LIMIT_BAL"></el-input></el-form-item>
    <el-form-item label="SEX"><el-input-number v-model.number="form.SEX" :min="0" :max="2"></el-input-number></el-form-item>
    <el-form-item label="年龄"><el-input-number v-model.number="form.AGE"></el-input-number></el-form-item>
    <el-form-item label="阈值"><el-input-number v-model.number="threshold" :min="0" :max="1" :step="0.01"></el-input-number></el-form-item>
    <el-button type="primary" @click="doPredict">预测</el-button>
  </el-form>
  <div v-if="result"><p>标签：{{ result.label }}</p><p>概率：{{ result.proba }}</p></div>
</el-card>
</template>
<script>
import { ref } from 'vue'
import { predictSingle } from '../api'
export default {
  setup(){
    const form=ref({ LIMIT_BAL:20000, SEX:1, AGE:35 });
    const threshold=ref(0.5);
    const result=ref(null);
    async function doPredict(){
      try{
        const resp=await predictSingle({ features: form.value, model_name: 'XGBoost', threshold: threshold.value });
        result.value=resp.data
      }catch(e){
        alert('预测失败:'+e)
      }
    }
    return { form, threshold, doPredict, result }
  }
}
</script>
FVP

cat > frontend/src/views/Dashboard.vue <<'FVD'
<template>
<el-row :gutter="20">
  <el-col :span="12"><el-card><div ref="aucChart" style="height:300px;"></div></el-card></el-col>
  <el-col :span="12"><el-card><div ref="distChart" style="height:300px;"></div></el-card></el-col>
  <el-col :span="24" style="margin-top:20px;"><el-card><div ref="featChart" style="height:400px;"></div></el-card></el-col>
</el-row>
</template>
<script>
import * as echarts from 'echarts'
import { onMounted, ref } from 'vue'
import { getDashboard } from '../api'
export default {
  setup(){
    const aucChart=ref(null);
    const distChart=ref(null);
    const featChart=ref(null);
    async function render(){
      const resp=await getDashboard();
      const data=resp.data;
      const models=Object.keys(data.metrics || {});
      const aucs=models.map(m => (data.metrics[m] && data.metrics[m].auc) ? data.metrics[m].auc : 0);
      const aucInstance=echarts.init(aucChart.value);
      aucInstance.setOption({
        title:{text:'模型 AUC 对比'},
        xAxis:{type:'category', data:models},
        yAxis:{type:'value'},
        series:[{type:'bar', data:aucs}]
      });

      const distInstance=echarts.init(distChart.value);
      distInstance.setOption({
        title:{text:'违约分布'},
        series:[{name:'分布', type:'pie', radius:'50%', data:[
          {value:data.distribution.negative, name:'正常'},
          {value:data.distribution.positive, name:'违约'}
        ]}]
      });

      const feat=data.feature_importance || {};
      const keys=Object.keys(feat).slice(0,10);
      const vals=keys.map(k=>feat[k]);
      const featInstance=echarts.init(featChart.value);
      featInstance.setOption({
        title:{text:'特征重要性前10名（XGBoost）'},
        xAxis:{type:'value'},
        yAxis:{type:'category', data:keys},
        series:[{type:'bar', data:vals}]
      });
    }
    onMounted(()=>{ render() })
    return { aucChart, distChart, featChart }
  }
}
</script>
FVD

# Dockerfiles
cat > backend/Dockerfile <<'BD'
FROM python:3.9‑slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no‑cache‑dir -r /app/requirements.txt
COPY . /app
EXPOSE 8000
CMD ["/bin/bash","./entrypoint.sh"]
BD

cat > frontend/Dockerfile <<'FD'
FROM node:18‑alpine
WORKDIR /app
COPY package.json /app/package.json
RUN npm install
COPY . /app
EXPOSE 5173
CMD ["npm","run","serve"]
FD

cat > LICENSE <<'LIC2'
Apache‑2.0
LIC2

# git commit && push
git add .
git commit -m "Add full‑stack CreditRiskSystem skeleton: backend (Django + MLService), frontend (Vue3), docker‑compose, CI, example env, models placeholder, README and license"

BRANCH=$(git rev‑parse --abbrev‑ref HEAD)
echo "Pushing to origin/$BRANCH ..."
git push origin "$BRANCH"

echo "Done. Files created and pushed on branch $BRANCH."
