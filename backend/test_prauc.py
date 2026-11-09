"""验证 PR-AUC 指标：取前 2000 条数据，只评估逻辑回归，确认 pr_auc 字段正常"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_risk.settings')
django.setup()

import pandas as pd
from riskapp.models import CreditCustomer
from riskapp.ml_service import MLService

qs = CreditCustomer.objects.all()[:2000]
rows = []
for c in qs:
    row = c.features_json or {}
    if 'default_payment' not in row and c.label is not None:
        row['default_payment'] = c.label
    rows.append(row)
df = pd.DataFrame(rows)
print(f"样本数: {len(df)}, 违约率: {df['default_payment'].mean():.4f}")

ml = MLService(df, label_col='default_payment')
ml.preprocess()
ml.train_test_split(test_size=0.2, shuffle=True)
ml.apply_smote(sampling_strategy=0.5)

from sklearn.linear_model import LogisticRegression
lr = LogisticRegression(max_iter=1000)
lr.fit(ml.X_train, ml.y_train)
metrics, proba = ml._evaluate(lr, ml.X_test, ml.y_test)
print("=== LR 评估指标（含 PR-AUC）===")
for k, v in metrics.items():
    print(f"  {k}: {v:.4f}")
assert 'pr_auc' in metrics, "缺少 pr_auc 字段!"
assert 0 <= metrics['pr_auc'] <= 1, "pr_auc 取值异常!"
print("\n[通过] PR-AUC 计算正常，字段齐全。")
