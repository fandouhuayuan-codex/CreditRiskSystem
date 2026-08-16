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
