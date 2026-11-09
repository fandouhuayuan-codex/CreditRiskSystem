# 基于 XGBoost 的银行信贷风险评估与可视化预警系统（后端）

> 作者：杨航　学号：2023102282　班级：大数据231　指导教师：尹兰兰
> 河池学院 · 大数据与计算机学院 · 数据科学与大数据技术专业

本文件夹是系统的 **后端（Django）工程**，前端工程位于上一级目录的 `../frontend`。
系统采用 Django（DRF）后端 + Vue3 前端 + SQLite 数据库，在 UCI 信用卡客户违约数据集（30000 条样本）上
训练并横向对比逻辑回归、SVM、随机森林、LightGBM、XGBoost 五种模型，通过 SMOTE 过采样处理类别不平衡，
并实现“预测—分档—告警—复核”的完整业务闭环。

---

## 一、功能特性

| 模块 | 说明 |
| --- | --- |
| 登录认证 | 基于角色的登录（管理员 / 审核员 / 只读） |
| 数据管理 | 上传 CSV/Excel、分页预览、样本统计、单条删除与批量清空 |
| 模型训练 | 一次训练五种模型，输出准确率/精确率/召回率/F1/AUC/KS 六维指标 |
| 模型详情 | 混淆矩阵、ROC 曲线、KS 值、特征重要性 |
| 风险预测 | 单条 + 批量预测，输出违约概率与高/中/低三档风险 |
| 可解释性 | SHAP 特征贡献度分析 |
| 风险告警 | 高风险（概率≥0.7）自动生成告警，支持待复核/已复核/已忽略闭环 |
| 报告导出 | 一键导出 Excel 模型评估报告 |

---

## 二、环境要求

| 环境 | 版本要求 | 开发机实际版本 |
| --- | --- | --- |
| Python | 3.10 及以上（推荐 3.11/3.12/3.13） | 3.13.7 |
| Node.js（前端用） | 16 及以上 | 22.23.2 |

---

## 三、需要下载的依赖（后端）

后端依赖已写在本目录的 `requirements.txt` 中，共 13 个包，用途如下：

| 依赖包 | 用途 |
| --- | --- |
| Django / djangorestframework | Web 框架与 REST API |
| django-cors-headers | 解决前后端跨域 |
| pandas / numpy | 数据读取、清洗与数值计算 |
| scikit-learn | 逻辑回归、SVM、随机森林、数据划分、标准化、评估指标 |
| scipy | scikit-learn、shap 的底层科学计算库 |
| xgboost | 核心模型 XGBoost |
| lightgbm | LightGBM 模型 |
| imbalanced-learn | SMOTE 过采样，处理违约样本不平衡 |
| joblib | 训练模型的保存与加载（.joblib） |
| shap | 模型可解释性 / 特征贡献度 |
| openpyxl | 导出 Excel 评估报告 |
| uvicorn | 生产部署（本地 runserver 调试用不到） |

**下载安装命令**（在本目录终端执行）：

```bash
pip install -r requirements.txt
```

国内下载慢可使用清华镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 四、后端启动步骤（在本目录 PyCharm 终端执行）

（1）创建并激活虚拟环境（推荐，已创建可跳过）：

```bash
python -m venv .venv
.venv\Scripts\activate
```

（2）安装依赖：

```bash
pip install -r requirements.txt
```

（3）生成数据库表（首次运行才需要）：

```bash
python manage.py makemigrations
python manage.py migrate
```

（4）创建登录用的超级用户（首次运行才需要，按提示设置用户名和密码）：

```bash
python manage.py createsuperuser
```

（5）启动后端服务：

```bash
python manage.py runserver 0.0.0.0:8000
```

看到 `Starting development server at http://0.0.0.0:8000/` 即成功。
后台管理地址：http://localhost:8000/admin/

---

## 五、启动前端

**另开一个终端**，进入上一级目录的前端工程：

```bash
cd ../frontend
npm install        # 首次运行才需要
npm run serve
```

浏览器打开 **http://localhost:5173**，默认账号：`admin` / `admin123`（以 createsuperuser 时设置的为准）。

---

## 六、后端目录结构

```
backend/
├── credit_risk/          # Django 工程配置（settings.py、urls.py、wsgi.py）
├── riskapp/              # 核心应用
│   ├── models.py         # 6 张数据表（用户/客户/训练记录/预测历史/特征权重/告警）
│   ├── views.py          # 17 个 REST API 视图
│   ├── urls.py           # 应用路由
│   ├── ml_service.py     # 机器学习核心（训练/评估/预测/SMOTE/ROC/特征重要性）
│   ├── serializers.py    # 序列化器
│   ├── admin.py          # 后台管理注册
│   └── migrations/       # 数据库迁移文件
├── models/               # 训练好的模型文件（.joblib）
├── upload_datasets/      # 数据集（含 UCI_Credit_Card.csv）
├── requirements.txt      # 后端依赖清单
├── manage.py             # Django 管理脚本
└── db.sqlite3            # SQLite 数据库
```

---

## 七、数据集与实验结果

- 数据集：UCI 信用卡客户违约数据集（`upload_datasets/UCI_Credit_Card.csv`）
- 样本量：30000 条，23 个特征，违约客户约 6636 条（违约率约 22.12%）
- 系统自动识别列名含 `default` / `payment.next.month` 的列为标签列并从特征中排除，避免标签泄漏
- 默认参数（测试集比例 0.3、SMOTE 采样比例 0.5）下，XGBoost 表现最优，AUC 约 0.83、KS 约 0.49
- 特征重要性中 `PAY_0`（最近一期还款状态）贡献最大，符合业务直觉

---

## 八、常见问题

**Q1：启动报 `No translation files found for default language zh-hans`？**
A：Windows 下缺少中文翻译文件，把 `credit_risk/settings.py` 中的 `LANGUAGE_CODE` 改为 `'en-us'`。

**Q2：训练 AUC 等于 1.0（异常）？**
A：标签泄漏。系统已自动排除含 `default`/`payment` 的标签列；自定义数据集请确保标签列名包含上述关键词。

**Q3：SVM 批量预测概率全部为 0%？**
A：SVM 使用 `probability=False` 时需用 sigmoid（Platt scaling）转换 decision_function，`ml_service.py` 已修复。

**Q4：时间比北京时间晚 8 小时？**
A：Django `USE_TZ=True` 存的是 UTC 时间，项目已用 `timezone.localtime()` 转换，并设置 `TIME_ZONE='Asia/Shanghai'`。

**Q5：如何重置数据库？**
A：删除 `db.sqlite3`，删除 `riskapp/migrations/` 下除 `__init__.py` 外的所有文件，再依次执行 `makemigrations`、`migrate`、`createsuperuser`。

---

*本项目为本科毕业设计，仅供学习与研究使用。*
