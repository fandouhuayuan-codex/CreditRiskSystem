# 基于 XGBoost 的银行信贷风险评估与可视化预警系统

> 作者：杨航　学号：2023102282　班级：大数据 231　指导教师：尹兰兰
> 河池学院・大数据与计算机学院・数据科学与大数据技术专业

一个采用 **Django（DRF）后端 + Vue3 前端 + SQLite 数据库** 的前后端分离全栈信用风险评估系统。

系统在 UCI 信用卡客户违约数据集（30000 条样本）上，训练并横向对比逻辑回归、SVM、随机森林、LightGBM、XGBoost 五种模型，

通过 SMOTE 过采样处理类别不平衡，并实现了 “预测 — 分档 — 告警 — 复核” 的完整业务闭环和可视化大屏。



***

## 一、功能特性



| 模块    | 说明                                          |
| ----- | ------------------------------------------- |
| 登录认证  | 基于角色的登录（管理员 / 审核员 / 只读），未登录自动跳转登录页          |
| 数据管理  | 上传 CSV/Excel、数据预览（分页）、样本统计、单条删除与批量清空        |
| 模型训练  | 一次训练五种模型，输出准确率 / 精确率 / 召回率 / F1/AUC/KS 六维指标 |
| 模型详情  | 混淆矩阵、ROC 曲线、KS 值、特征重要性可视化                   |
| 风险预测  | 单条预测 + 批量预测，输出违约概率与高 / 中 / 低三档风险            |
| 可解释性  | SHAP 特征贡献度分析，说明每个特征对预测结果的影响                 |
| 风险告警  | 高风险（概率≥0.7）自动生成告警，支持待复核 / 已复核 / 已忽略闭环       |
| 可视化大屏 | 数据卡片、AUC 柱状图、违约饼图、特征重要性、模型雷达图               |
| 报告导出  | 一键导出 Excel 模型评估报告                           |



***

## 二、技术栈



* **后端**：Django 4.2+/6.x、Django REST Framework、django-cors-headers

* **机器学习**：scikit-learn、XGBoost、LightGBM、imbalanced-learn（SMOTE）、SHAP

* **数据处理**：pandas、numpy、openpyxl（Excel 导出）

* **前端**：Vue3、Vite、Vue Router、Element Plus、Axios、ECharts 5

* **数据库**：SQLite（本地，免安装；生产可迁移 MySQL/PostgreSQL）



***

## 三、环境要求



| 环境      | 版本要求                        | 开发机实际版本 |
| ------- | --------------------------- | ------- |
| Python  | 3.10 及以上（推荐 3.11/3.12/3.13） | 3.13.7  |
| Node.js | 16 及以上（推荐 18 LTS 或 20+）     | 22.23.2 |
| npm     | 随 Node 安装即可                 | —       |



***

## 四、需要下载的依赖

### 4.1 后端依赖（Python）

后端依赖已全部写在 `backend/requirements.txt` 中，包含 13 个包，用途如下：



| 依赖包                          | 用途                           |
| ---------------------------- | ---------------------------- |
| Django / djangorestframework | Web 框架与 REST API             |
| django-cors-headers          | 解决前后端跨域问题                    |
| pandas / numpy               | 数据读取、清洗与数值计算                 |
| scikit-learn                 | 逻辑回归、SVM、随机森林、数据划分、标准化、评估指标  |
| scipy                        | scikit-learn、shap 的底层科学计算库   |
| xgboost                      | 核心模型 XGBoost                 |
| lightgbm                     | LightGBM 模型                  |
| imbalanced-learn             | SMOTE 过采样，解决违约样本不平衡          |
| joblib                       | 训练模型的保存与加载（.joblib）          |
| shap                         | 模型可解释性 / 特征贡献度               |
| openpyxl                     | 导出 Excel 评估报告                |
| uvicorn                      | 生产环境部署（本地 `runserver` 调试用不到） |

**安装方式**：进入 `backend` 目录后执行一条命令即可（见下方 “快速启动”）。

### 4.2 前端依赖（Node）

前端依赖写在 `frontend/package.json` 中，主要包括：



* 运行依赖：vue、vue-router、axios、element-plus、echarts

* 开发依赖：vite、@vitejs/plugin-vue

**安装方式**：进入 `frontend` 目录后执行 `npm install`，会自动下载全部前端依赖。



***

## 五、项目结构



```
CreditRiskSystem/
├── backend/                     # 后端项目
│   ├── credit_risk/             # Django 工程配置
│   │   ├── settings.py          # 配置（数据库、跨域、语言、时区等）
│   │   ├── urls.py              # 根路由
│   │   └── wsgi.py
│   ├── riskapp/                 # 核心应用
│   │   ├── models.py            # 6 张数据表
│   │   ├── views.py             # 17 个 REST API 视图
│   │   ├── urls.py              # 应用路由
│   │   ├── ml_service.py        # 机器学习核心（训练/评估/预测/SMOTE/ROC）
│   │   ├── serializers.py       # 序列化器
│   │   └── admin.py             # 后台管理注册
│   ├── models/                  # 训练好的模型文件（.joblib）
│   ├── upload_datasets/         # 上传的数据集（含 UCI_Credit_Card.csv）
│   ├── requirements.txt         # 后端依赖清单
│   ├── manage.py                # Django 管理脚本
│   └── db.sqlite3               # SQLite 数据库
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── views/               # 8 个页面（登录/大屏/上传/训练/预测/详情/历史/告警）
│   │   ├── api/index.js         # 接口封装（axios）
│   │   ├── router/index.js      # 路由 + 登录守卫
│   │   └── App.vue              # 侧边栏布局与告警角标
│   ├── package.json             # 前端依赖清单
│   └── vite.config.js
└── README.md                    # 本文件
```



***

## 六、快速启动（第一次运行照做）

### 第一步：启动后端

打开 **PyCharm 的终端（Terminal）**，进入后端目录：



```
cd backend
```

（1）创建并激活虚拟环境（推荐，已创建可跳过）：



```
python -m venv .venv
.venv\Scripts\activate
```

（2）下载安装后端依赖：



```
pip install -r requirements.txt
```

> 若国内下载慢，可使用清华镜像：
> `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

（3）生成数据库表（首次运行才需要）：



```
python manage.py makemigrations
python manage.py migrate
```

（4）创建登录用的超级用户（首次运行才需要，按提示设置用户名和密码）：



```
python manage.py createsuperuser
```

（5）启动后端服务：



```
python manage.py runserver 0.0.0.0:8000
```

看到 `Starting development server at http://0.0.0.0:8000/` 即成功。

后台管理地址：[http://localhost:8000/admin/](http://localhost:8000/admin/)

### 第二步：启动前端

**再新开一个终端窗口**（后端不要关闭），进入前端目录：



```
cd frontend
```

（1）下载安装前端依赖（首次运行才需要）：



```
npm install
```

> 若报 
>
> `ERESOLVE`
>
>  依赖冲突，改用：
>
> `npm install --legacy-peer-deps`

（2）启动前端：



```
npm run serve
```

### 第三步：访问系统

浏览器打开： [http://localhost:5173](http://localhost:5173)



* 登录账号：`admin`

* 登录密码：`admin123`（以你 createsuperuser 时设置的为准）



***

## 七、数据集说明



* 数据集：UCI 信用卡客户违约数据集（`backend/upload_datasets/UCI_Credit_Card.csv`）

* 样本量：30000 条，23 个特征，违约客户约 6636 条（违约率约 22.12%）

* 系统会自动识别列名中含 `default` / `payment.next.month` 的列作为标签列，并从特征中排除，避免标签泄漏。



***

## 八、主要实验结果

在默认参数（测试集比例 0.3、SMOTE 采样比例 0.5）下，五种模型横向对比：



* XGBoost 表现最优，AUC 约 **0.83**、KS 约 **0.49**；

* 特征重要性中 `PAY_0`（最近一期还款状态）贡献最大，符合 “最近还款行为最能预测违约” 的业务直觉。



***

## 九、常见问题

**Q1：启动后端报&#x20;**`No translation files found for default language zh-hans`**？**

A：Windows 下缺少中文翻译文件。把 `backend/credit_risk/settings.py` 中的 `LANGUAGE_CODE` 改为 `'en-us'` 即可。

**Q2：训练结果 AUC 等于 1.0（异常）？**

A：这是标签泄漏。系统已自动排除含 `default`/`payment` 的标签列；若使用自定义数据集，请确保标签列名包含上述关键词。

**Q3：SVM 批量预测概率全部为 0%？**

A：SVM 使用 `probability=False` 时需用 sigmoid（Platt scaling）将 decision\_function 转为概率，项目 `ml_service.py` 中已修复该问题。

**Q4：页面显示的时间比北京时间晚 8 小时？**

A：Django `USE_TZ=True` 存的是 UTC 时间。项目已通过 `timezone.localtime()` 转换，并在 `settings.py` 中设置 `TIME_ZONE='Asia/Shanghai'`。

**Q5：前端启动后页面空白？**

A：检查是否安装了 `@vitejs/plugin-vue`，并确认 `vite.config.js` 中已注册 vue 插件。

**Q6：如何重置数据库？**

A：删除 `backend/db.sqlite3`，删除 `riskapp/migrations/` 下除 `__init__.py` 外的所有文件，再依次执行 `makemigrations`、`migrate`、`createsuperuser`。



***

*本项目为本科毕业设计，仅供学习与研究使用。*