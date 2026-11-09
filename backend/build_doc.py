# -*- coding: utf-8 -*-
"""生成《毕设从0到1全流程拆解与答辩指南》Word 文档"""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOC = Document()
# 全局正文样式
NORMAL = DOC.styles['Normal']
NORMAL.font.name = 'Microsoft YaHei'
NORMAL.font.size = Pt(10.5)
NORMAL._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

BLUE = RGBColor(0x00, 0x6E, 0xC8)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
CODE_BG = 'F2F4F7'


def _set_east(run, font='Microsoft YaHei'):
    run.font.name = font
    r = run._element
    r.rPr.rFonts.set(qn('w:eastAsia'), font)


def h1(text):
    p = DOC.add_heading(level=1)
    run = p.add_run(text)
    run.font.color.rgb = BLUE
    run.font.size = Pt(17)
    _set_east(run)
    return p


def h2(text):
    p = DOC.add_heading(level=2)
    run = p.add_run(text)
    run.font.color.rgb = RGBColor(0x0B, 0x4F, 0x8C)
    run.font.size = Pt(13.5)
    _set_east(run)
    return p


def h3(text):
    p = DOC.add_heading(level=3)
    run = p.add_run(text)
    run.font.color.rgb = DARK
    run.font.size = Pt(11.5)
    _set_east(run)
    return p


def para(text, bold=False):
    p = DOC.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.25
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(10.5)
    _set_east(run)
    return p


def bullet(text):
    p = DOC.add_paragraph(style='List Bullet')
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    _set_east(run)
    return p


def _shade(p, color):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), color)
    pPr.append(shd)


def code(text):
    p = DOC.add_paragraph()
    p.paragraph_format.left_indent = Pt(6)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.05
    _shade(p, CODE_BG)
    for i, line in enumerate(text.split('\n')):
        run = p.add_run(('' if i == 0 else '\n') + line)
        run.font.name = 'Consolas'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas')
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x1F, 0x2D, 0x3D)
    return p


def table(headers, rows, widths=None):
    t = DOC.add_table(rows=1, cols=len(headers))
    t.style = 'Light Grid Accent 1'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, htext in enumerate(headers):
        hdr[i].text = ''
        run = hdr[i].paragraphs[0].add_run(htext)
        run.bold = True
        run.font.size = Pt(9.5)
        _set_east(run)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ''
            run = cells[i].paragraphs[0].add_run(str(val))
            run.font.size = Pt(9)
            _set_east(run)
    if widths:
        for i, w in enumerate(widths):
            for r in t.rows:
                r.cells[i].width = Inches(w)
    DOC.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ============================ 封面 ============================
title = DOC.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.paragraph_format.space_before = Pt(90)
r = title.add_run('基于 XGBoost 的银行信贷风险评估\n与可视化预警系统')
r.font.size = Pt(26); r.bold = True; r.font.color.rgb = BLUE; _set_east(r)

sub = DOC.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.paragraph_format.space_before = Pt(20)
r = sub.add_run('从 0 到 1 全流程拆解与答辩指南')
r.font.size = Pt(16); r.font.color.rgb = RGBColor(0x55, 0x55, 0x55); _set_east(r)

info = DOC.add_paragraph(); info.alignment = WD_ALIGN_PARAGRAPH.CENTER
info.paragraph_format.space_before = Pt(120)
for line in ['学生：杨航　　学号：2023102282', '班级：大数据 231　　指导教师：尹兰兰',
             '河池学院 · 大数据与计算机学院 · 数据科学与大数据技术专业']:
    rr = info.add_run(line + '\n'); rr.font.size = Pt(12); _set_east(rr)
DOC.add_page_break()

# ============================ 导读 ============================
h1('导读：本系统是什么')
para('本系统是一个前后端分离的信用风险评估 Web 系统。它以 UCI 公开的“信用卡客户违约数据集”（30000 条样本、23 个特征、违约率约 22.12%）为数据基础，'
     '在统一数据口径下训练并横向对比逻辑回归、支持向量机、随机森林、LightGBM、XGBoost 五种模型，用 SMOTE 处理类别不平衡，用 SHAP 做模型可解释性，'
     '并把“数据管理—模型训练—风险预测—分级告警—人工复核—可视化大屏”做成完整的业务闭环。')
para('全文按真实开发顺序组织：先讲后端工程与数据建模，再讲机器学习核心，再讲 API 接口，最后讲前端页面与联调；每个步骤都给出关键代码、用途、功能与存在意义。')

# ============================ 阶段零 ============================
h1('阶段零　技术选型与总体架构')
h2('0.1 为什么这样选型')
table(['层次', '技术', '选择理由'],
      [['后端框架', 'Django + DRF', '自带 ORM、认证、后台管理；DRF 快速构建 REST API，生态成熟'],
       ['机器学习', 'scikit-learn / XGBoost / LightGBM / imbalanced-learn / SHAP', '覆盖传统模型、梯度提升、不平衡采样与可解释性'],
       ['前端框架', 'Vue3 + Vite + Element Plus + ECharts', '组件化、构建快、UI 组件丰富、图表能力强'],
       ['数据库', 'SQLite', '零配置单文件，适合原型与答辩；经 ORM 可平滑迁移 MySQL'],
       ['架构模式', '前后端分离', '前后端通过 JSON 接口解耦，分工清晰、可独立部署']],
      widths=[1.2, 2.4, 3.0])
h2('0.2 总体架构与数据流')
code('''浏览器(Vue3页面)
   │  HTTP/JSON (axios)
   ▼
Django REST Framework (views.py 17个接口)
   │ 调用            │ ORM
   ▼                  ▼
MLService(模型/训练/预测)   SQLite 六张表
   │ joblib
   ▼
models/ 目录下的 .joblib 模型文件''')
para('意义：分层清晰——页面只负责展示与交互，视图负责业务编排，MLService 负责算法，数据库负责持久化，模型文件负责复用，任何一层都可独立替换而不影响其他层。')

# ============================ 阶段一 ============================
h1('阶段一　后端工程搭建（Django）')

h2('1.1 创建虚拟环境与安装依赖')
para('用途：隔离项目依赖，避免污染系统 Python。先建虚拟环境，再用 requirements.txt 安装全部依赖。')
code('''python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt''')

h2('1.2 创建 Django 工程与应用')
code('''django-admin startproject credit_risk
python manage.py startapp riskapp''')
para('credit_risk 是工程配置目录，riskapp 是承载全部业务的应用。')

h2('1.3 配置 settings.py（逐项说明）')
para('（1）注册应用：把 rest_framework、corsheaders、riskapp 加入 INSTALLED_APPS，Django 才能识别这些模块。')
code('''INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'rest_framework','corsheaders','riskapp',
]''')
para('（2）中间件：corsheaders 放在最前，用于处理跨域；其余负责会话、认证、CSRF 等。')
para('（3）数据库：使用 SQLite，Django 自动生成 db.sqlite3 文件，无需安装数据库服务。')
code('''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}''')
para('（4）跨域与权限：开发期允许全部来源，关闭默认认证（登录由自定义接口实现），保证前端 5173 端口能访问后端 8000。')
code('''CORS_ALLOW_ALL_ORIGINS = True
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_AUTHENTICATION_CLASSES': []
}''')
para('（5）时区与自定义用户、模型目录：统一上海时区，指定自定义用户表和模型文件目录。')
code('''TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True
AUTH_USER_MODEL = "riskapp.AdminUser"
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)''')

h2('1.4 数据库模型设计 models.py（六张表）')
para('意义：把业务中的“人、客户、训练、预测、权重、告警”抽象为六张关系表，是系统持久化的基础。')
table(['表名', '作用', '关键字段'],
      [['AdminUser', '系统用户（继承 AbstractUser）', 'role 角色、phone，含管理员/审核/只读'],
       ['CreditCustomer', '信贷客户数据', 'customer_id、LIMIT_BAL、SEX、EDUCATION、features_json、label、predicted_proba'],
       ['TrainingLog', '每次训练记录', 'models_metrics、models_params、features'],
       ['PredictHistory', '每次预测留痕', 'input_features、predicted_label、predicted_proba、model_name'],
       ['FeatureWeight', '特征权重', 'model_name、weights(JSON)'],
       ['RiskAlert', '高风险告警', 'customer_id、predicted_proba、status、reviewed_at、review_note']],
      widths=[1.4, 2.2, 3.0])
para('以自定义用户和告警表为例的关键代码：')
code('''class AdminUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20,
        choices=(('admin','管理员'),('auditor','风控审核'),('viewer','只读')),
        default='viewer')

class RiskAlert(models.Model):
    customer_id = models.CharField(max_length=64, null=True, db_index=True)
    input_features = models.JSONField()
    predicted_proba = models.FloatField()
    model_name = models.CharField(max_length=64, default='XGBoost')
    status = models.CharField(max_length=20,
        choices=(('pending','待复核'),('reviewed','已复核'),('ignored','已忽略')),
        default='pending')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True, null=True)''')

h2('1.5 数据库迁移与后台注册')
para('迁移把模型定义同步成真实数据表；admin 注册后可在 /admin 后台直接增删改查。')
code('''python manage.py makemigrations
python manage.py migrate''')
code('''# admin.py
admin.site.register(AdminUser, UserAdmin)
admin.site.register(CreditCustomer)
admin.site.register(TrainingLog)
admin.site.register(PredictHistory)
admin.site.register(FeatureWeight)
admin.site.register(RiskAlert)''')

h2('1.6 序列化器 serializers.py')
para('用途：在模型对象与 JSON 之间转换，是 DRF 数据进出的标准方式。ModelSerializer 自动按字段生成。')
code('''class RiskAlertSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = RiskAlert
        fields = '__all__' ''')

# ============================ 阶段二 ============================
h1('阶段二　机器学习核心 MLService（ml_service.py）')
para('MLService 把“数据预处理 → 划分 → 采样 → 训练 → 评估 → 保存 → 预测”封装成一个类，是整个系统的算法大脑。')

h2('2.1 初始化：标签识别与特征列筛选')
para('用途：自动找到标签列，并把标签列、ID 列从特征中排除，从源头防止标签泄漏（标签泄漏会导致 AUC 异常等于 1）。')
code('''def __init__(self, df, label_col='default_payment'):
    self.df = df.copy()
    if label_col not in df.columns:
        cands = [c for c in df.columns if 'default' in c.lower() or 'payment' in c.lower()]
        if cands: label_col = cands[0]
    self.feature_cols = [c for c in df.columns
        if c != label_col and c != 'customer_id' and c.upper() != 'ID'
        and 'default' not in c.lower() and 'payment' not in c.lower()]
    self.scaler = StandardScaler()
    self.models, self.metrics = {}, {}''')

h2('2.2 数据预处理 preprocess')
para('功能：数值列用中位数填充缺失值、非数值列填 0，再用 StandardScaler 做标准化（均值0、方差1），消除量纲差异，对 LR、SVM 尤其重要。')
code('''def preprocess(self):
    df = self.df.copy()
    for col in df.columns:
        if col == self.label_col or col == 'customer_id' or col.upper()=='ID': continue
        if 'default' in col.lower() or 'payment' in col.lower(): continue
        if df[col].dtype.kind in 'biufc':
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(0)
    X = df[self.feature_cols]; y = df[self.label_col].astype(int)
    self.X = pd.DataFrame(self.scaler.fit_transform(X), columns=self.feature_cols)
    self.y = y
    return self.X, self.y''')

h2('2.3 数据集划分 train_test_split')
para('功能：按比例切分训练集/测试集，stratify 分层抽样保证两边类别比例一致，random_state 固定保证结果可复现。')
code('''def train_test_split(self, test_size=0.2, random_state=42, shuffle=True):
    X_tr, X_te, y_tr, y_te = train_test_split(
        self.X, self.y, test_size=test_size, random_state=random_state,
        shuffle=shuffle, stratify=self.y if shuffle else None)
    self.X_train, self.X_test = X_tr, X_te
    self.y_train, self.y_test = y_tr, y_te''')

h2('2.4 SMOTE 过采样 apply_smote')
para('意义：违约样本仅占 22%，模型容易偏向多数类。SMOTE 通过对少数类样本做线性插值合成新样本，缓解不平衡。'
     '关键：只对训练集采样，测试集保持真实分布，评估才客观。')
code('''def apply_smote(self, sampling_strategy=0.5, random_state=42):
    sm = SMOTE(sampling_strategy=sampling_strategy, random_state=random_state)
    self.X_train_res, self.y_train_res = sm.fit_resample(self.X_train, self.y_train)''')

h2('2.5 模型评估 _evaluate（七项指标）')
para('功能：输出准确率、精确率、召回率、F1、AUC、PR-AUC、KS 七项指标。对没有 predict_proba 的 SVM，'
     '用 sigmoid（Platt scaling）把 decision_function 映射到 [0,1]，解决概率为 0 的问题。')
code('''def _evaluate(self, model, X, y_true):
    y_pred = model.predict(X)
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X)[:, 1]
    else:
        y_proba = model.decision_function(X)
        y_proba = 1.0 / (1.0 + np.exp(-y_proba))   # sigmoid
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    ks = float(np.max(tpr - fpr))
    pr_auc = float(average_precision_score(y_true, y_proba))
    return {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1': float(f1_score(y_true, y_pred, zero_division=0)),
        'auc': float(roc_auc_score(y_true, y_proba)),
        'pr_auc': pr_auc, 'ks': ks}, y_proba''')

h2('2.6 ROC 数据与网格搜索')
para('get_roc_data 返回 ROC 曲线坐标并降采样到 200 点，避免前端数据过大；grid_search_cv 用交叉验证自动挑选最优超参数。')
code('''def grid_search_cv(self, estimator, param_grid, X, y, cv=3, scoring='roc_auc'):
    grid = GridSearchCV(estimator, param_grid, cv=cv, scoring=scoring, n_jobs=-1)
    grid.fit(X, y)
    return grid.best_estimator_, grid.best_params_, grid.best_score_''')

h2('2.7 训练全部模型 train_all')
para('功能：在重采样后的训练集上依次训练五个模型，在未采样的测试集上评估，最后用 joblib 把每个模型加时间戳保存，便于加载复用。')
code('''def train_all(self, use_gridsearch=False):
    X_tr = self.X_train_res if hasattr(self,'X_train_res') else self.X_train
    y_tr = self.y_train_res if hasattr(self,'y_train_res') else self.y_train
    X_val, y_val = self.X_test, self.y_test
    lr = LogisticRegression(max_iter=1000)
    svm = SVC(kernel='rbf', C=1.0, gamma='scale', probability=False)
    rf  = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    lgbm = lgb.LGBMClassifier(random_state=42, verbose=-1)
    xgbc = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
    for name, m in [('LogisticRegression',lr),('SVM',svm),('RandomForest',rf),
                    ('LightGBM',lgbm),('XGBoost',xgbc)]:
        m.fit(X_tr, y_tr)
        self.models[name] = m
        self.metrics[name], _ = self._evaluate(m, X_val, y_val)
    ts = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    for name, m in self.models.items():
        joblib.dump(m, os.path.join(MODEL_DIR, f'{name}_{ts}.joblib'))
    return self.metrics''')

h2('2.8 特征重要性与单条预测')
para('get_feature_importance 优先取 XGBoost 的特征重要性并排序；predict_single 对齐特征、补齐缺失列、用同一 scaler 转换，'
     '再输出违约标签与概率，保证训练与预测的预处理口径完全一致。')
code('''def predict_single(self, x_dict, model_name='XGBoost', threshold=0.5):
    X = pd.DataFrame([x_dict])
    for col in self.feature_cols:
        if col not in X.columns: X[col] = 0
    X = X[self.feature_cols]
    X_scaled = pd.DataFrame(self.scaler.transform(X), columns=self.feature_cols)
    model = self.models.get(model_name)
    proba = model.predict_proba(X_scaled)[:,1][0]
    label = int(proba >= threshold)
    return label, float(proba)''')

# ============================ 阶段三 ============================
h1('阶段三　后端 REST API 视图（views.py）')
para('视图是前端与算法/数据库之间的桥梁，共 17 个接口，按业务分组如下。')
table(['接口', '方法/路径', '功能与意义'],
      [['登录/登出', 'POST auth/login、auth/logout', '校验用户名密码，返回角色与 token'],
       ['文件上传', 'POST upload/', '解析 CSV/Excel，识别标签列，批量入库'],
       ['数据预览', 'GET preview/', '分页返回客户数据，支持表格展示'],
       ['清空数据', 'DELETE delete-all/', '删除客户及关联训练/预测/权重记录'],
       ['数据统计', 'GET stats/', '返回总数、正负样本数、最近上传时间'],
       ['模型训练', 'POST train/', '编排预处理→划分→采样→训练，返回指标与类别分布'],
       ['训练历史', 'GET training-history/', '列出历次训练及最佳模型'],
       ['单条预测', 'POST predict/', '输出概率、三档风险，高风险自动生成告警'],
       ['批量预测', 'POST batch-predict/', '逐行预测并统计高/中/低数量，批量建告警'],
       ['模型详情', 'GET model-detail/<name>', '返回混淆矩阵、ROC 数据'],
       ['SHAP', 'POST shap/', 'TreeExplainer 计算特征贡献度'],
       ['大屏数据', 'GET dashboard/', '聚合指标、特征重要性、分布'],
       ['导出报告', 'GET export-report/', 'openpyxl 生成 Excel 评估报告'],
       ['告警列表/复核', 'GET alerts、POST alerts/<id>/review', '分页筛选、复核/忽略闭环']],
      widths=[1.3, 2.3, 3.0])
h2('3.1 单条预测中的三档分级与告警（核心业务逻辑）')
code('''if proba >= 0.7:
    risk_level = '高风险'
elif proba >= 0.3:
    risk_level = '中风险'
else:
    risk_level = '低风险'
PredictHistory.objects.create(input_features=features,
    predicted_label=label, predicted_proba=proba, model_name=model_name)
if proba >= 0.7:
    alert = RiskAlert.objects.create(customer_id=str(features.get('ID')),
        input_features=features, predicted_proba=proba,
        model_name=model_name, status='pending')''')
h2('3.2 本地时间处理')
para('USE_TZ=True 时数据库存 UTC，用 timezone.localtime 转成本地时间，解决显示时间差 8 小时的问题。')
code('''def local_time_str(dt):
    return timezone.localtime(dt).strftime('%Y-%m-%d %H:%M:%S')''')

# ============================ 阶段四 ============================
h1('阶段四　前端工程（Vue3）')
h2('4.1 创建项目与入口 main.js')
code('''npm create vite@latest frontend -- --template vue
cd frontend && npm install''')
para('main.js 创建应用实例，注册路由与 Element Plus 并挂载到 #app。')
code('''const app = createApp(App)
app.use(router); app.use(ElementPlus)
app.mount('#app')''')

h2('4.2 路由与登录守卫 router/index.js')
para('意义：定义 URL 与页面的映射；beforeEach 守卫检查 token，未登录一律跳转登录页，实现访问控制。')
code('''router.beforeEach((to, from, next) => {
  if (to.meta.public) return next()
  if (localStorage.getItem('auth_token')) next()
  else next('/login')
})''')

h2('4.3 接口封装 api/index.js')
para('用 axios 创建统一实例，baseURL 指向后端，超时设 10 分钟以容纳 SVM 训练；各接口封装成函数，页面直接调用。')
code('''const api = axios.create({ baseURL: 'http://localhost:8000/api/', timeout: 600000 })
export function trainModels(params){ return api.post('train/', params) }
export function predictSingle(payload){ return api.post('predict/', payload) }
export function getAlerts(params){ return api.get('alerts/', { params }) }''')

h2('4.4 主布局 App.vue')
para('功能：侧边栏导航 + 顶部告警角标，每 30 秒轮询待复核数量；登录页单独全屏布局，其余页面统一框架。')

h2('4.5 八个页面职责')
table(['页面', '功能', '关键技术'],
      [['Login 登录', '账号密码登录、写入 token', 'el-form、el-input'],
       ['Dashboard 大屏', '数据卡片、AUC/饼图/雷达/特征重要性', 'ECharts 五张图'],
       ['Upload 数据管理', '上传、统计、预览、清空', 'el-upload、el-table'],
       ['Train 模型训练', '参数配置、指标表、采样对比图', 'el-slider、ECharts'],
       ['Predict 风险预测', '单条/批量预测、SHAP 分析', 'el-tabs、el-progress'],
       ['ModelDetail 详情', '指标、混淆矩阵、ROC 曲线', 'ECharts'],
       ['TrainingHistory 历史', '历次训练记录对比', 'el-table'],
       ['Alert 告警中心', '筛选、分页、复核/忽略闭环', 'el-dialog、el-pagination']],
      widths=[1.5, 2.8, 2.3])

# ============================ 阶段五 ============================
h1('阶段五　系统联调与运行')
para('后端与前端分别启动，前端通过代理/跨域访问后端接口，完成端到端联调。')
h2('5.1 启动后端')
code('''cd backend
.venv\\Scripts\\activate
python manage.py runserver 0.0.0.0:8000''')
h2('5.2 启动前端')
code('''cd frontend
npm install
npm run serve''')
h2('5.3 完整使用流程')
para('登录 → 数据管理上传数据集 → 模型训练（等待 SVM 完成）→ 查看大屏与模型详情 → 风险预测 → 高风险自动告警 → 告警中心复核 → 导出报告。')

DOC.add_page_break()
# ============================ 答辩十题 ============================
h1('附：答辩高频十题及参考答案')
qa = [
 ('1. 为什么最终选择 XGBoost？表格里 LightGBM 的 AUC 不是更高吗？',
  'AUC 只是单一指标，模型选型综合了召回率、精确率、F1、KS、PR-AUC、稳定性和工程成熟度。XGBoost 在信贷风控领域落地案例最多，'
  '与 SHAP 的工具链最成熟，且系统预测默认使用 XGBoost。LightGBM 在默认参数下 AUC 略高，二者非常接近，调参后 XGBoost 同样具备竞争力。'),
 ('2. 类别不平衡是怎么处理的？',
  '违约样本仅占约 22%。我采用 SMOTE 在训练集上对少数类做插值合成，并严格遵循“先划分、后采样”，只对训练集采样，测试集保持真实分布，'
  '同时用召回率、KS、PR-AUC 等对不平衡更敏感的指标评估，避免只看准确率带来的误导。'),
 ('3. 你遇到过 AUC 等于 1 的情况吗？是什么原因？',
  '遇到过，本质是标签泄漏——标签列被当成特征送入模型。我在初始化时自动识别并排除含 default、payment 的列和 ID 列，从源头避免泄漏，修复后 AUC 回到合理的 0.8 左右。'),
 ('4. AUC、KS、PR-AUC 分别是什么？',
  'AUC 是 ROC 曲线下面积，衡量整体区分好坏客户的能力，0.5 为随机、1 为完美；KS 是 TPR 与 FPR 最大差值，衡量模型的最大区分度；'
  'PR-AUC 是精确率-召回率曲线下面积，在类别不平衡时比 ROC-AUC 更敏感。'),
 ('5. 为什么用 SQLite 而不是 MySQL？',
  '系统定位是原型验证，数据量约 3 万、单机演示，SQLite 零配置、易部署。系统基于 Django ORM 实现数据库无关，迁移 MySQL 只需改配置并重新 migrate，业务代码无需改动。'),
 ('6. 一条客户数据从输入到出结果，完整流程是怎样的？',
  '前端录入特征 → POST 到 predict 接口 → 加载最新模型 → 对齐特征列并用同一 scaler 标准化 → 模型输出违约概率 → 按 0.3/0.7 阈值分档 →'
  '写预测历史，若概率≥0.7 自动生成告警 → 结果返回前端展示。'),
 ('7. 高/中/低三档阈值是怎么定的？',
  '结合业务经验设定：概率≥0.7 判为高风险并自动告警，0.3–0.7 为中风险转人工复核，低于 0.3 为低风险走正常审批。阈值在前端可调整，便于按风险偏好灵活配置。'),
 ('8. SHAP 是什么？为什么要用它？',
  'SHAP 基于博弈论 Shapley 值，把预测结果分解到每个特征，量化各特征对单次预测的正负向贡献。它解决了复杂模型“黑箱”问题，让风控决策可解释、可审计。'),
 ('9. 前后端分离是怎么交互的？跨域怎么解决？',
  '前端用 axios 以 JSON 调用后端 REST 接口，后端用 django-cors-headers 配置 CORS 允许前端来源，实现跨域访问；前后端通过约定的接口契约解耦，可独立开发部署。'),
 ('10. 系统有哪些不足？如何改进？',
  '一是 SQLite 不支持高并发，生产应换 MySQL/PostgreSQL；二是特征工程较基础，可增加分箱与交叉特征；三是缺少模型在线更新机制；'
  '四是可引入深度学习模型对比，并结合 LIME 等更多可解释性工具。'),
]
for q, a in qa:
    h3(q)
    para(a)

OUT = os.path.join(os.path.dirname(__file__), '毕设从0到1全流程拆解与答辩指南.docx')
DOC.save(OUT)
print('saved:', OUT, 'paragraphs:', len(DOC.paragraphs))
