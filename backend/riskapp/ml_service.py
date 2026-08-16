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
