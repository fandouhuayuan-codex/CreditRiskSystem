"""验证 SMOTE 采样前后类别分布数据"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_risk.settings')
django.setup()

import pandas as pd
from riskapp.models import CreditCustomer
from riskapp.ml_service import MLService

qs = CreditCustomer.objects.all()[:3000]
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
ml.apply_smote(sampling_strategy=0.5)

dist = {
    'before': {
        'negative': int((ml.y_train == 0).sum()),
        'positive': int((ml.y_train == 1).sum())
    },
    'after': {
        'negative': int((ml.y_train_res == 0).sum()),
        'positive': int((ml.y_train_res == 1).sum())
    }
}
print("采样前训练集:", dist['before'])
print("采样后训练集:", dist['after'])
ratio = dist['after']['positive'] / dist['after']['negative']
print(f"采样后 违约/正常 比例: {ratio:.3f}（预期≈0.5）")
assert abs(ratio - 0.5) < 0.01, "采样比例异常"
print("[通过] 类别分布数据正确。")
