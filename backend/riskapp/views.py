import os
import io
import pandas as pd
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import AdminUser, CreditCustomer, TrainingLog, PredictHistory, FeatureWeight, RiskAlert
from .ml_service import MLService
import joblib


def local_time_str(dt):
    """将UTC时间转换为本地时间并格式化，解决时区差8小时问题"""
    if dt is None:
        return None
    return timezone.localtime(dt).strftime('%Y-%m-%d %H:%M:%S')


class LoginView(APIView):
    permission_classes = []
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = AdminUser.objects.get(username=username)
            if user.check_password(password):
                return Response({'username': user.username, 'role': getattr(user, 'role', 'admin'), 'token': 'local-dev-token'})
        except AdminUser.DoesNotExist:
            pass
        return Response({'error': '用户名或密码错误'}, status=400)


class LogoutView(APIView):
    def post(self, request):
        return Response({'message': '已退出登录'})


class UserInfoView(APIView):
    permission_classes = []
    def get(self, request):
        return Response({'is_authenticated': False})


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
                return Response({'error': '仅支持 CSV / Excel'}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({'message': f'已写入 {len(objs)} 条记录', 'columns': list(df.columns), 'rows': len(df)})


class DataPreviewView(APIView):
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        qs = CreditCustomer.objects.all()[:limit]
        data = []
        for c in qs:
            row = c.features_json or {}
            row['customer_id'] = c.customer_id
            row['label'] = c.label
            data.append(row)
        columns = list(data[0].keys()) if data else []
        return Response({'columns': columns, 'data': data, 'total': CreditCustomer.objects.count()})


class DeleteAllDataView(APIView):
    def delete(self, request):
        count = CreditCustomer.objects.count()
        CreditCustomer.objects.all().delete()
        TrainingLog.objects.all().delete()
        PredictHistory.objects.all().delete()
        FeatureWeight.objects.all().delete()
        return Response({'message': f'已删除 {count} 条客户数据及相关记录'})


class DataStatsView(APIView):
    def get(self, request):
        total = CreditCustomer.objects.count()
        positive = CreditCustomer.objects.filter(label=1).count()
        negative = total - positive
        latest = CreditCustomer.objects.order_by('-created_at').first()
        return Response({
            'total': total, 'positive': positive, 'negative': negative,
            'latest_upload': local_time_str(latest.created_at) if latest else None
        })


class TrainModelsView(APIView):
    def post(self, request):
        use_grid = request.data.get('use_gridsearch', False)
        smote_ratio = float(request.data.get('smote_ratio', 0.5))
        qs = CreditCustomer.objects.all()
        if not qs.exists():
            return Response({'error': '未找到数据，请先上传'}, status=400)
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
        # SMOTE 采样前后训练集类别分布（用于前端对比图）
        class_distribution = {
            'before': {
                'negative': int((ml.y_train == 0).sum()),
                'positive': int((ml.y_train == 1).sum())
            },
            'after': {
                'negative': int((ml.y_train_res == 0).sum()),
                'positive': int((ml.y_train_res == 1).sum())
            }
        }
        metrics = ml.train_all(use_gridsearch=use_grid)
        feat_imp = ml.get_feature_importance(topn=50)
        TrainingLog.objects.create(models_metrics=metrics, models_params={'use_gridsearch': use_grid, 'smote_ratio': smote_ratio}, features=ml.feature_cols)
        FeatureWeight.objects.create(model_name='XGBoost', weights=feat_imp)
        return Response({'metrics': metrics, 'feature_importance': feat_imp, 'features': ml.feature_cols, 'class_distribution': class_distribution})


class TrainingHistoryView(APIView):
    def get(self, request):
        logs = TrainingLog.objects.order_by('-created_at')[:20]
        result = []
        for log in logs:
            best_model = max(log.models_metrics.items(), key=lambda x: x[1].get('auc', 0)) if log.models_metrics else (None, {})
            result.append({
                'id': log.id,
                'created_at': local_time_str(log.created_at),
                'dataset_name': log.dataset_name,
                'best_model': best_model[0],
                'best_auc': best_model[1].get('auc', 0),
                'models_metrics': log.models_metrics,
                'params': log.models_params
            })
        return Response(result)


def _get_ref_df():
    qs = CreditCustomer.objects.all()[:2000]
    rows = []
    for c in qs:
        row = c.features_json or {}
        if 'default_payment' not in row and c.label is not None:
            row['default_payment'] = c.label
        rows.append(row)
    return pd.DataFrame(rows) if rows else None


def _load_model(model_name):
    model_files = [f for f in os.listdir(settings.MODEL_DIR) if f.startswith(model_name)]
    if not model_files:
        return None
    latest = sorted(model_files)[-1]
    return joblib.load(os.path.join(settings.MODEL_DIR, latest))


class PredictView(APIView):
    def post(self, request):
        features = request.data.get('features')
        model_name = request.data.get('model_name', 'XGBoost')
        threshold = float(request.data.get('threshold', 0.5))
        if not features:
            return Response({'error': '缺少 features'}, status=400)
        df_ref = _get_ref_df()
        if df_ref is None:
            return Response({'error': '数据库无样本，请先上传并训练'}, status=400)
        ml = MLService(df_ref, label_col='default_payment')
        ml.preprocess()
        model = _load_model(model_name)
        if model is None:
            return Response({'error': '未找到已训练模型，请先训练'}, status=400)
        ml.models[model_name] = model
        label, proba = ml.predict_single(features, model_name=model_name, threshold=threshold)
        # 三档风险分级
        if proba >= 0.7:
            risk_level = '高风险'
            risk_color = '#ff4757'
        elif proba >= 0.3:
            risk_level = '中风险'
            risk_color = '#ffa502'
        else:
            risk_level = '低风险'
            risk_color = '#00ff88'
        PredictHistory.objects.create(input_features=features, predicted_label=label, predicted_proba=proba, model_name=model_name)
        # 高风险自动生成告警
        alert_id = None
        if proba >= 0.7:
            cid = features.get('ID') or features.get('customer_id') or features.get('customer_id')
            alert = RiskAlert.objects.create(
                customer_id=str(cid) if cid else None,
                input_features=features,
                predicted_proba=proba,
                model_name=model_name,
                status='pending'
            )
            alert_id = alert.id
        return Response({'label': label, 'proba': proba, 'risk_level': risk_level, 'risk_color': risk_color, 'alert_id': alert_id})


class BatchPredictView(APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    def post(self, request):
        file_obj = request.FILES.get('file')
        model_name = request.data.get('model_name', 'XGBoost')
        threshold = float(request.data.get('threshold', 0.5))
        if not file_obj:
            return Response({'error': '请上传文件'}, status=400)
        try:
            if file_obj.name.lower().endswith('.csv'):
                df = pd.read_csv(file_obj)
            else:
                df = pd.read_excel(file_obj)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        df_ref = _get_ref_df()
        if df_ref is None:
            return Response({'error': '数据库无样本'}, status=400)
        ml = MLService(df_ref, label_col='default_payment')
        ml.preprocess()
        model = _load_model(model_name)
        if model is None:
            return Response({'error': '未找到模型'}, status=400)
        ml.models[model_name] = model
        results = []
        high_count = 0
        mid_count = 0
        low_count = 0
        alert_objs = []
        for idx, row in df.iterrows():
            features = row.to_dict()
            label, proba = ml.predict_single(features, model_name=model_name, threshold=threshold)
            if proba >= 0.7:
                risk = '高风险'
                high_count += 1
                cid = features.get('ID') or features.get('customer_id')
                alert_objs.append(RiskAlert(
                    customer_id=str(cid) if cid else None,
                    input_features=features,
                    predicted_proba=proba,
                    model_name=model_name,
                    status='pending'
                ))
            elif proba >= 0.3:
                risk = '中风险'
                mid_count += 1
            else:
                risk = '低风险'
                low_count += 1
            results.append({'index': idx, 'label': label, 'proba': round(proba, 4), 'risk': risk})
        # 批量创建高风险告警（最多保留前500条，避免数据过大）
        if alert_objs:
            RiskAlert.objects.bulk_create(alert_objs[:500])
        return Response({
            'total': len(results),
            'high_risk': high_count,
            'mid_risk': mid_count,
            'low_risk': low_count,
            'alert_created': min(len(alert_objs), 500),
            'results': results
        })


class ModelDetailView(APIView):
    def get(self, request, model_name):
        tl = TrainingLog.objects.order_by('-created_at').first()
        if not tl or model_name not in tl.models_metrics:
            return Response({'error': '未找到该模型数据'}, status=404)
        metrics = tl.models_metrics[model_name]
        df_ref = _get_ref_df()
        if df_ref is None:
            return Response({'metrics': metrics, 'confusion_matrix': None, 'roc': None})
        ml = MLService(df_ref, label_col='default_payment')
        ml.preprocess()
        ml.train_test_split(test_size=0.2, shuffle=True)
        model = _load_model(model_name)
        if model is None:
            return Response({'metrics': metrics, 'confusion_matrix': None, 'roc': None})
        y_pred = model.predict(ml.X_test)
        y_true = ml.y_test.values
        tn = int(((y_pred == 0) & (y_true == 0)).sum())
        fp = int(((y_pred == 1) & (y_true == 0)).sum())
        fn = int(((y_pred == 0) & (y_true == 1)).sum())
        tp = int(((y_pred == 1) & (y_true == 1)).sum())
        roc_data = ml.get_roc_data(model, ml.X_test, y_true)
        return Response({
            'metrics': metrics,
            'confusion_matrix': {'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp},
            'roc': roc_data,
            'features': ml.feature_cols
        })


class SHAPView(APIView):
    def post(self, request):
        features = request.data.get('features')
        model_name = request.data.get('model_name', 'XGBoost')
        if not features:
            return Response({'error': '缺少 features'}, status=400)
        try:
            import shap
        except ImportError:
            return Response({'error': '请先安装 shap 库: pip install shap'}, status=400)
        df_ref = _get_ref_df()
        if df_ref is None:
            return Response({'error': '无样本数据'}, status=400)
        ml = MLService(df_ref, label_col='default_payment')
        ml.preprocess()
        model = _load_model(model_name)
        if model is None:
            return Response({'error': '未找到模型'}, status=400)
        X = pd.DataFrame([features])
        for col in ml.feature_cols:
            if col not in X.columns:
                X[col] = 0
        X = X[ml.feature_cols]
        X_scaled = pd.DataFrame(ml.scaler.transform(X), columns=ml.feature_cols)
        try:
            if hasattr(model, 'get_booster') or hasattr(model, 'feature_importances_'):
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X_scaled)
            else:
                explainer = shap.KernelExplainer(model.predict_proba, ml.X[:100])
                shap_values = explainer.shap_values(X_scaled)
            if isinstance(shap_values, list):
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            sv = shap_values[0] if len(shap_values.shape) > 1 else shap_values
            contributions = {ml.feature_cols[i]: float(sv[i]) for i in range(min(len(ml.feature_cols), len(sv)))}
            sorted_contrib = dict(sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)[:15])
            return Response({'shap_values': sorted_contrib})
        except Exception as e:
            return Response({'error': 'SHAP计算失败: ' + str(e), 'shap_values': {}})


class DashboardDataView(APIView):
    def get(self, request):
        tl = TrainingLog.objects.order_by('-created_at').first()
        metrics = tl.models_metrics if tl else {}
        fw = FeatureWeight.objects.order_by('-computed_at').first()
        feat_imp = fw.weights if fw else {}
        total = CreditCustomer.objects.count()
        positive = CreditCustomer.objects.filter(label=1).count()
        neg = total - positive
        return Response({'metrics': metrics, 'feature_importance': feat_imp, 'distribution': {'total': total, 'positive': positive, 'negative': neg}})


class ExportReportView(APIView):
    permission_classes = []
    def get(self, request):
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
        wb = Workbook()
        ws = wb.active
        ws.title = '模型评估报告'
        header_fill = PatternFill(start_color='00D4FF', end_color='00D4FF', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        ws.append(['银行信贷风险评估系统 - 模型评估报告'])
        ws.merge_cells('A1:F1')
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = Alignment(horizontal='center')
        ws.append([])
        tl = TrainingLog.objects.order_by('-created_at').first()
        if tl:
            ws.append(['训练时间', local_time_str(tl.created_at)])
            ws.append(['数据集', tl.dataset_name])
            ws.append([])
            headers = ['模型', '准确率', '精确率', '召回率', 'F1分数', 'AUC']
            ws.append(headers)
            header_row = ws.max_row
            for col_idx in range(1, len(headers)+1):
                cell = ws.cell(row=header_row, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
            for name, m in tl.models_metrics.items():
                ws.append([name, f"{m['accuracy']*100:.2f}%", f"{m['precision']*100:.2f}%", f"{m['recall']*100:.2f}%", f"{m['f1']*100:.2f}%", f"{m['auc']:.4f}"])
        total = CreditCustomer.objects.count()
        positive = CreditCustomer.objects.filter(label=1).count()
        ws.append([])
        ws.append(['数据统计'])
        ws.append(['总样本数', total])
        ws.append(['违约样本', positive])
        ws.append(['正常样本', total - positive])
        ws.append(['违约率', f"{positive/total*100:.2f}%" if total else '0%'])
        for col_idx in range(1, 8):
            max_length = 0
            for row in ws.iter_rows(min_col=col_idx, max_col=col_idx):
                for cell in row:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
            ws.column_dimensions[get_column_letter(col_idx)].width = max_length + 4
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        from django.http import HttpResponse
        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="credit_risk_report.xlsx"'
        return response


class AlertListView(APIView):
    """风险告警列表，支持按状态筛选和分页"""
    def get(self, request):
        status_filter = request.query_params.get('status', '')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        qs = RiskAlert.objects.all().order_by('-created_at')
        if status_filter and status_filter != 'all':
            qs = qs.filter(status=status_filter)
        total = qs.count()
        pending_count = RiskAlert.objects.filter(status='pending').count()
        start = (page - 1) * page_size
        end = start + page_size
        alerts = qs[start:end]
        data = []
        for a in alerts:
            data.append({
                'id': a.id,
                'customer_id': a.customer_id,
                'predicted_proba': round(a.predicted_proba, 4),
                'model_name': a.model_name,
                'status': a.status,
                'status_display': a.get_status_display(),
                'created_at': local_time_str(a.created_at),
                'reviewed_at': local_time_str(a.reviewed_at),
                'review_note': a.review_note,
            })
        return Response({
            'total': total,
            'pending_count': pending_count,
            'page': page,
            'page_size': page_size,
            'results': data
        })


class AlertReviewView(APIView):
    """标记告警为已复核或已忽略"""
    def post(self, request, alert_id):
        try:
            alert = RiskAlert.objects.get(id=alert_id)
        except RiskAlert.DoesNotExist:
            return Response({'error': '告警不存在'}, status=404)
        action = request.data.get('action', 'reviewed')
        note = request.data.get('note', '')
        from django.utils import timezone
        if action == 'reviewed':
            alert.status = 'reviewed'
        elif action == 'ignored':
            alert.status = 'ignored'
        else:
            return Response({'error': '无效操作'}, status=400)
        alert.reviewed_at = timezone.now()
        alert.review_note = note
        alert.save()
        return Response({'message': '操作成功', 'status': alert.status, 'status_display': alert.get_status_display()})
