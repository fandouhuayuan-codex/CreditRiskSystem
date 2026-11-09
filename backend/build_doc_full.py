# -*- coding: utf-8 -*-
"""生成《完整代码版》Word：逐文件读取真实源码 + 详细解释，供答辩深挖准备。"""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r'C:\Users\22121\Desktop\CreditRiskSystem'
BACKEND = os.path.join(ROOT, 'backend')
FRONTEND = os.path.join(ROOT, 'frontend')

DOC = Document()
NORMAL = DOC.styles['Normal']
NORMAL.font.name = 'Microsoft YaHei'; NORMAL.font.size = Pt(10.5)
NORMAL._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
BLUE = RGBColor(0x00, 0x6E, 0xC8); DARK = RGBColor(0x1A, 0x1A, 0x1A); CODE_BG = 'F2F4F7'


def _east(run, font='Microsoft YaHei'):
    run.font.name = font
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font)


def h1(t):
    p = DOC.add_heading(level=1); r = p.add_run(t); r.font.color.rgb = BLUE; r.font.size = Pt(17); _east(r)


def h2(t):
    p = DOC.add_heading(level=2); r = p.add_run(t); r.font.color.rgb = RGBColor(0x0B, 0x4F, 0x8C); r.font.size = Pt(13); _east(r)


def h3(t):
    p = DOC.add_heading(level=3); r = p.add_run(t); r.font.color.rgb = DARK; r.font.size = Pt(11); _east(r)


def para(t, bold=False):
    p = DOC.add_paragraph(); p.paragraph_format.space_after = Pt(4); p.paragraph_format.line_spacing = 1.25
    r = p.add_run(t); r.bold = bold; r.font.size = Pt(10.5); _east(r)


def _shade(p, color):
    pPr = p._p.get_or_add_pPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:fill'), color); pPr.append(shd)


def code(t):
    p = DOC.add_paragraph(); p.paragraph_format.left_indent = Pt(4); p.paragraph_format.space_after = Pt(6); p.paragraph_format.line_spacing = 1.0
    _shade(p, CODE_BG)
    for i, line in enumerate(t.split('\n')):
        r = p.add_run(('' if i == 0 else '\n') + line); r.font.name = 'Consolas'
        r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas'); r.font.size = Pt(8.5); r.font.color.rgb = RGBColor(0x1F, 0x2D, 0x3D)


def table(headers, rows):
    t = DOC.add_table(rows=1, cols=len(headers)); t.style = 'Light Grid Accent 1'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hc = t.rows[0].cells
    for i, x in enumerate(headers):
        hc[i].text = ''; r = hc[i].paragraphs[0].add_run(x); r.bold = True; r.font.size = Pt(9.5); _east(r)
    for row in rows:
        cc = t.add_row().cells
        for i, v in enumerate(row):
            cc[i].text = ''; r = cc[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(9); _east(r)
    DOC.add_paragraph().paragraph_format.space_after = Pt(2)


def file_block(title, relpath, base, before, after):
    h2(title)
    for b in before:
        para(b)
    full = os.path.join(base, relpath)
    with open(full, 'r', encoding='utf-8') as f:
        code(f.read())
    para('文件路径：' + relpath, bold=True)
    for a in after:
        para(a)


# 封面
tt = DOC.add_paragraph(); tt.alignment = WD_ALIGN_PARAGRAPH.CENTER; tt.paragraph_format.space_before = Pt(90)
r = tt.add_run('基于 XGBoost 的银行信贷风险评估\n与可视化预警系统'); r.font.size = Pt(26); r.bold = True; r.font.color.rgb = BLUE; _east(r)
sub = DOC.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER; sub.paragraph_format.space_before = Pt(20)
r = sub.add_run('完整代码版 · 逐文件详解与答辩深挖指南'); r.font.size = Pt(16); r.font.color.rgb = RGBColor(0x55, 0x55, 0x55); _east(r)
info = DOC.add_paragraph(); info.alignment = WD_ALIGN_PARAGRAPH.CENTER; info.paragraph_format.space_before = Pt(120)
for line in ['学生：杨航　学号：2023102282', '班级：大数据 231　指导教师：尹兰兰', '河池学院 · 大数据与计算机学院']:
    rr = info.add_run(line + '\n'); rr.font.size = Pt(12); _east(rr)
DOC.add_page_break()

h1('使用说明')
para('本版在“全流程拆解版”基础上，把每个源文件的完整代码原样列出（直接读取自项目，与运行代码一致），并在代码前说明用途、代码后逐段讲清关键逻辑与答辩可能追问点。'
     '建议先看“用途”，再对照完整代码，最后看“逐段解释”。')

# ============ 后端 ============
h1('第一部分　后端完整代码（Django + DRF）')

h2('1.0 环境准备与工程创建')
para('先创建并激活虚拟环境，安装依赖，再创建工程与应用，最后做首次迁移。')
code('''python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
django-admin startproject credit_risk
python manage.py startapp riskapp
python manage.py makemigrations
python manage.py migrate''')
para('逐段解释：venv 隔离依赖；startproject 生成工程配置目录 credit_risk；startapp 生成业务应用 riskapp；makemigrations 把模型变化生成迁移文件，migrate 把迁移同步到数据库。')

file_block('1.1 工程配置 settings.py', r'credit_risk\settings.py', BACKEND,
    ['用途：Django 工程的总配置，决定注册哪些应用、中间件顺序、数据库、跨域、时区、模型目录与自定义用户。'],
    ['逐段解释：',
     '（1）INSTALLED_APPS 注册 rest_framework、corsheaders、riskapp，Django 才会加载它们；顺序上自定义应用放最后。',
     '（2）MIDDLEWARE 中 CorsMiddleware 放最前，保证跨域请求最先被处理；其余依次负责安全、会话、通用、CSRF、认证、消息。',
     '（3）DATABASES 指定 SQLite，数据库即 BASE_DIR 下的 db.sqlite3 单文件，无需安装数据库服务。',
     '（4）REST_FRAMEWORK 设为 AllowAny 且认证类为空，登录由自定义 LoginView 实现；CORS_ALLOW_ALL_ORIGINS 允许前端 5173 跨域访问。',
     '（5）TIME_ZONE 设为 Asia/Shanghai、USE_TZ=True，数据库存 UTC、显示转本地；LANGUAGE_CODE 用 en-us 规避 Windows 缺中文翻译文件问题。',
     '（6）MODEL_DIR 指向 models 目录并自动创建，用于存放 joblib 模型；AUTH_USER_MODEL 指定自定义用户表 riskapp.AdminUser。',
     '答辩追问点：为什么能平滑迁移 MySQL？因为业务代码基于 ORM，迁移时只需改 ENGINE/NAME 等配置并重新 migrate，模型与视图代码不动。'])

file_block('1.2 工程级路由 credit_risk/urls.py', r'credit_risk\urls.py', BACKEND,
    ['用途：工程入口路由，把 /admin 交给后台，把 /api 转发给 riskapp 的路由。'],
    ['逐段解释：include 把子路由挂载到 api/ 前缀下，因此所有业务接口都以 /api/ 开头；这种两级路由让工程与应用职责分离。'])

file_block('1.3 应用配置 apps.py', r'riskapp\apps.py', BACKEND,
    ['用途：声明 riskapp 应用的配置类，Django 启动时据此初始化应用。'],
    ['逐段解释：AppConfig 定义 name、default_auto_field（主键默认类型 BigAutoField），可在 ready() 中挂载信号，本项目未使用信号。'])

file_block('1.4 数据模型 models.py（六张表完整代码）', r'riskapp\models.py', BACKEND,
    ['用途：用 ORM 把业务实体定义为六张表，是系统持久化的基础。'],
    ['逐表解释：',
     'AdminUser 继承 AbstractUser，扩展 phone 与 role（管理员/风控审核/只读）；必须重写 groups、user_permissions 并改 related_name，否则与内置 User 的反向关系冲突。',
     'CreditCustomer 存客户：customer_id 唯一并建索引，LIMIT_BAL/SEX/EDUCATION/MARRIAGE/AGE 为核心字段，features_json 存原始整行，label 为真实标签，predicted_* 为预测结果，created_at 自动写入。',
     'TrainingLog 存每次训练：models_metrics 指标、models_params 参数、features 特征列表均为 JSONField。',
     'PredictHistory 存每次预测留痕：输入特征、预测标签、概率、模型名。',
     'FeatureWeight 存特征权重：model_name 与 weights(JSON)。',
     'RiskAlert 存高风险告警：status 三态（pending/reviewed/ignored）、reviewed_at、review_note，支持复核闭环。',
     '答辩追问点：表间为何没有物理外键？六张表通过 customer_id 等字段做逻辑关联，降低耦合、便于批量导入与数据库迁移；__str__ 用于后台可读展示。'])

file_block('1.5 后台注册 admin.py', r'riskapp\admin.py', BACKEND,
    ['用途：把六张表注册到 Django 自带后台，便于直接增删改查与数据核对。'],
    ['逐段解释：AdminUser 配合 UserAdmin 保留用户管理能力，其余模型直接注册；访问 /admin 即可管理，是开发期核查数据的重要工具。'])

file_block('1.6 序列化器 serializers.py', r'riskapp\serializers.py', BACKEND,
    ['用途：在模型对象与 JSON 之间转换，是 DRF 数据进出的标准方式。'],
    ['逐段解释：每个 ModelSerializer 按 model 与 fields 自动生成；RiskAlertSerializer 额外用 get_status_display 输出中文状态 status_display，前端无需再做映射。'])

file_block('1.7 机器学习核心 ml_service.py（完整代码）', r'riskapp\ml_service.py', BACKEND,
    ['用途：封装“预处理→划分→采样→训练→评估→保存→预测”全流程，是系统算法大脑。'],
    ['逐方法解释：',
     '__init__：自动识别含 default/payment 的标签列，特征列排除标签列与 ID 列，从源头防止标签泄漏；初始化 StandardScaler、models、metrics 容器。',
     'preprocess：数值列用中位数填充缺失、非数值列填 0，再用 StandardScaler 标准化（均值0、方差1），消除量纲差异。',
     'train_test_split：按比例切分，stratify 分层保证两边类别比例一致，random_state 固定保证可复现。',
     'apply_smote：SMOTE 对训练集少数类插值合成，缓解不平衡；只作用于训练集，测试集保持真实分布。',
     '_evaluate：输出七项指标；无 predict_proba 的 SVM 用 decision_function 再经 sigmoid（Platt scaling）转概率；KS 取 TPR-FPR 最大值，PR-AUC 用 average_precision_score。',
     'get_roc_data：计算 ROC 并降采样到约 200 点，避免前端数据过大。',
     'grid_search_cv：GridSearchCV 交叉验证挑选最优超参数，评分用 roc_auc。',
     'train_all：在重采样训练集训练五模型、在未采样测试集评估，最后用 joblib 加时间戳保存每个模型。',
     'get_feature_importance：优先取 XGBoost 特征重要性并排序，缺失时回退随机森林。',
     'predict_single：对齐特征列、缺失补 0、用同一 scaler 转换；SVM 单样本不能用 min-max（min=max 恒为0），故用 sigmoid；返回标签与概率。',
     '答辩追问点：为什么先划分后采样？若先采样再划分，合成样本会泄漏到测试集，导致评估虚高。AUC=1 多为标签泄漏，已通过列筛选规避。'])

file_block('1.8 业务视图 views.py（17 接口完整代码）', r'riskapp\views.py', BACKEND,
    ['用途：承接前端请求，编排 MLService 与 ORM，是前端与算法/数据库之间的桥梁。'],
    ['逐视图解释：',
     'local_time_str：用 timezone.localtime 把 UTC 转本地字符串。',
     'Login/Logout/UserInfo：登录校验用户名密码并返回角色与 token；登出与用户信息接口。',
     'FileUpload：解析 CSV/Excel，识别标签列，逐行构造 CreditCustomer 并 bulk_create 批量入库。',
     'DataPreview：分页返回前 N 条；DeleteAllData：清空客户及关联训练/预测/权重记录；DataStats：返回总数、正负样本、最近上传时间。',
     'TrainModels：从数据库取数构造 DataFrame，依次执行预处理、划分、SMOTE，统计采样前后 class_distribution，train_all 训练并写 TrainingLog、FeatureWeight。',
     'TrainingHistory：取最近 20 次训练，计算每次 AUC 最高的最佳模型。',
     'Predict：加载模型并单条预测，按 0.3/0.7 三档分级，写 PredictHistory；概率≥0.7 自动创建 RiskAlert，返回 alert_id。',
     'BatchPredict：逐行预测并统计高/中/低数量，高风险批量建告警（上限500）。',
     'ModelDetail：返回指标、混淆矩阵 TN/FP/FN/TP 与 ROC 数据。',
     'SHAP：树模型用 TreeExplainer、其余用 KernelExplainer，输出按绝对值排序的 Top15 贡献。',
     'DashboardData：聚合最新指标、特征权重与分布；ExportReport：openpyxl 生成 Excel 报告并以附件返回。',
     'AlertList：按状态筛选与分页，返回待复核数；AlertReview：把告警标记为已复核/已忽略并记录时间与备注。',
     '答辩追问点：为什么告警只在预测页触发、不在训练页？AUC 是整体排序能力指标，不等于某个客户的违约概率；告警针对具体客户概率≥0.7 才有业务意义。'])

file_block('1.9 应用路由 riskapp/urls.py', r'riskapp\urls.py', BACKEND,
    ['用途：把 17 个视图绑定到具体 URL，供前端调用。'],
    ['逐段解释：每个 path 对应一个 APIView 的 as_view()；model-detail 用 <str:model_name> 传模型名，alerts/review 用 <int:alert_id> 传告警主键。'])

# ============ 前端 ============
h1('第二部分　前端完整代码（Vue3 + Vite）')

h2('2.0 工程创建')
code('''npm create vite@latest frontend -- --template vue
cd frontend
npm install''')
para('逐段解释：Vite 生成 Vue3 脚手架，npm install 安装依赖；开发服务器默认端口 5173，被占用会自动顺延。')

file_block('2.1 入口 main.js', r'src\main.js', FRONTEND,
    ['用途：创建应用实例，注册路由与 Element Plus，挂载到 #app。'],
    ['逐段解释：引入 Element Plus 及其样式，app.use 依次注册 router 与组件库，mount 挂载；全局组件在所有页面可用。'])

file_block('2.2 路由 router/index.js', r'src\router\index.js', FRONTEND,
    ['用途：定义 URL 与页面组件映射，并通过守卫做登录访问控制。'],
    ['逐段解释：routes 中登录页 meta.public=true，其余路径对应各页面；beforeEach 检查 localStorage 的 auth_token，无 token 一律跳 /login。'])

file_block('2.3 接口封装 api/index.js', r'src\api\index.js', FRONTEND,
    ['用途：用 axios 统一封装后端接口，baseURL 指向 8000，超时设 10 分钟容纳 SVM 训练。'],
    ['逐段解释：上传/批量预测用 FormData；其余为 JSON；各接口导出为函数，页面 import 后直接调用，避免重复写 URL。'])

file_block('2.4 主布局 App.vue', r'src\App.vue', FRONTEND,
    ['用途：登录页单独全屏，其余页面统一侧边栏+内容区；侧边栏含导航与告警角标。'],
    ['逐段解释：isLoginPage 切换布局；onMounted 拉取待复核数并每 30 秒轮询，onUnmounted 清理定时器；doLogout 清 token 并跳登录。'])

frontend_pages = [
    ('2.5 登录页 Login.vue', r'src\views\Login.vue',
     '账号密码登录，成功后写入 token 与用户名并跳转首页；表单做非空校验，错误信息由后端返回。'),
    ('2.6 数据管理 Upload.vue', r'src\views\Upload.vue',
     '上传数据集、统计卡片、前10条预览、清空全部数据；删除前用确认框，操作后刷新统计与预览。'),
    ('2.7 模型训练 Train.vue', r'src\views\Train.vue',
     '配置 SMOTE 比例与调参方式，结果表展示七项指标与 PR-AUC，并用 ECharts 画采样前后类别对比图。'),
    ('2.8 风险预测 Predict.vue', r'src\views\Predict.vue',
     '单条/批量两个 Tab：单条录入特征出概率、三档进度条与 SHAP 因素分析；批量出高/中/低统计与明细表。'),
    ('2.9 模型详情 ModelDetail.vue', r'src\views\ModelDetail.vue',
     '展示指标、混淆矩阵与 ROC 曲线（ECharts），从路由参数取模型名并拉取详情。'),
    ('2.10 训练历史 TrainingHistory.vue', r'src\views\TrainingHistory.vue',
     '列出历次训练记录与最佳模型，按 models_metrics 渲染对比表。'),
    ('2.11 风险告警 Alert.vue', r'src\views\Alert.vue',
     '统计卡片、状态筛选、分页表格，支持复核通过/忽略并填写备注，形成闭环。'),
    ('2.12 可视化大屏 Dashboard.vue', r'src\views\Dashboard.vue',
     '五张 ECharts 图（AUC对比、违约饼图、综合指标、特征重要性、雷达图）加顶部统计卡与实时时钟，支持导出报告。'),
]
for title, rel, explain in frontend_pages:
    file_block(title, rel, FRONTEND, ['用途：' + explain],
        ['逐段解释：template 负责结构与 Element Plus 组件，setup 用 ref/computed 管理状态、调用 api 函数并处理加载与错误，scoped style 只作用于当前页面；ECharts 在 onMounted 后初始化、onUnmounted 释放。'])

# ============ 联调 ============
h1('第三部分　系统联调与运行')
h2('3.1 启动后端')
code('''cd backend
.venv\\Scripts\\activate
python manage.py runserver 0.0.0.0:8000''')
h2('3.2 启动前端')
code('''cd frontend
npm run serve''')
h2('3.3 完整业务闭环')
para('登录 → 数据管理上传数据集 → 模型训练（等待 SVM 完成）→ 查看大屏与模型详情 → 风险预测 → 高风险自动告警 → 告警中心复核 → 导出报告。')
para('联调要点：前端经 CORS 跨域访问后端；接口字段以 views 返回 JSON 为准；模型文件与数据库分别持久化，重启后可继续使用。')

DOC.add_page_break()
# ============ 答辩十题 ============
h1('附：答辩高频十题及参考答案')
qa = [
 ('1. 为什么最终选择 XGBoost？LightGBM 的 AUC 不是更高吗？',
  'AUC 只是单一指标，选型综合召回率、精确率、F1、KS、PR-AUC、稳定性与工程成熟度。XGBoost 在信贷风控落地案例多、与 SHAP 工具链成熟，且系统默认使用它；LightGBM 默认参数 AUC 略高，二者接近，调参后 XGBoost 同样有竞争力。'),
 ('2. 类别不平衡怎么处理？',
  '违约样本约 22%。采用 SMOTE 对训练集少数类插值合成，严格先划分后采样，只对训练集处理、测试集保持真实分布，并用召回、KS、PR-AUC 等对不平衡敏感的指标评估，避免只看准确率。'),
 ('3. 遇到过 AUC=1 吗？原因？',
  '遇到过，本质是标签泄漏，标签列被当成特征。初始化时自动排除含 default/payment 的列与 ID 列，从源头规避，修复后 AUC 回到合理的 0.8 左右。'),
 ('4. AUC、KS、PR-AUC 分别是什么？',
  'AUC 是 ROC 曲线下面积，衡量整体区分能力，0.5 随机、1 完美；KS 是 TPR 与 FPR 最大差值，衡量最大区分度；PR-AUC 是精确率-召回率曲线下面积，不平衡时更敏感。'),
 ('5. 为什么用 SQLite？',
  '系统定位原型验证，约 3 万样本、单机演示，SQLite 零配置易部署。基于 ORM 实现数据库无关，迁移 MySQL 只需改配置并重新 migrate，业务代码不动。'),
 ('6. 一条数据从输入到出结果的完整流程？',
  '前端录入 → POST predict → 加载模型 → 对齐特征并用同一 scaler 标准化 → 输出违约概率 → 按 0.3/0.7 分档 → 写预测历史，概率≥0.7 自动告警 → 返回前端展示。'),
 ('7. 三档阈值怎么定的？',
  '结合业务经验：≥0.7 高风险并告警，0.3–0.7 中风险人工复核，<0.3 低风险正常审批；阈值前端可调，适配不同风险偏好。'),
 ('8. SHAP 是什么？为什么用？',
  '基于博弈论 Shapley 值，把预测分解到各特征，量化正负向贡献，解决黑箱问题，让风控决策可解释、可审计。'),
 ('9. 前后端如何交互？跨域怎么解决？',
  '前端用 axios 以 JSON 调 REST 接口，后端用 django-cors-headers 配置 CORS 允许前端来源；通过接口契约解耦，可独立开发部署。'),
 ('10. 不足与改进？',
  'SQLite 不支持高并发，生产换 MySQL/PostgreSQL；特征工程可加分箱与交叉特征；增加模型在线更新；可引入深度学习对比并结合 LIME 等更多解释工具。'),
]
for q, a in qa:
    h3(q); para(a)

OUT = os.path.join(BACKEND, '毕设完整代码版-逐文件详解与答辩指南.docx')
DOC.save(OUT)
print('saved:', OUT, 'paragraphs:', len(DOC.paragraphs))
