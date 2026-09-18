# Toutiao Backend

一个按 `crud / models / routers / schemas / utils` 分层的 FastAPI 项目骨架，使用 FastAPI、SQLAlchemy 2.0 和 MySQL 异步连接。

## 项目结构

```text
toutiao_backend/
├── app/
│   ├── crud/          # 数据访问与 CRUD 操作
│   ├── models/        # SQLAlchemy 数据库模型
│   ├── routers/       # API 路由
│   ├── schemas/       # Pydantic 请求和响应模型
│   ├── utils/         # 通用工具函数
│   ├── config.py      # 配置
│   ├── database.py    # 数据库连接和会话
│   ├── dependencies.py
│   └── main.py
├── tests/
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## 启动

### PyCharm

项目已经配置好 `FastAPI` 运行配置：

1. 用 PyCharm 打开 `D:\codex\toutiao_backend`
2. 确认右下角 Python 解释器选择项目里的 `.venv`
3. 顶部运行配置选择 `FastAPI`
4. 点击绿色三角形运行按钮

也可以直接右键项目根目录下的 `run.py`，选择 **Run 'run'**。

### VS Code

打开项目后按 `F5`，选择 `FastAPI` 配置。

### 命令行

```powershell
cd D:\codex\toutiao_backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

说明：

- `.venv` 是项目的独立 Python 虚拟环境。
- `Activate.ps1` 只负责激活虚拟环境，不会启动 FastAPI。
- `pip install -r requirements.txt` 只需要首次安装依赖时执行。
- 真正启动服务的是 `python run.py`。

启动后访问：

- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Health: <http://127.0.0.1:8000/health>
- Database Health: <http://127.0.0.1:8000/health/db>

访问 `/health/db` 会执行一次 `SELECT 1`：

- 返回 `200` 且 `"status": "ok"`：MySQL 连接正常
- 返回 `503` 且 `"status": "error"`：项目启动了，但数据库连接失败

## MySQL 配置

### 1. 创建数据库

先在 MySQL 中创建数据库。数据库名可以使用 `toutiao`：

```sql
CREATE DATABASE toutiao
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

### 2. 安装 MySQL 异步驱动

如果已经按照 `requirements.txt` 安装过依赖，重新执行一次即可：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

项目使用 `aiomysql` 作为 SQLAlchemy 的 MySQL 异步驱动。

### 3. 配置连接地址

在项目根目录新建 `.env` 文件，填写自己的 MySQL 用户名、密码、地址和数据库名：

```env
APP_ENV=development
DEBUG=true
DATABASE_URL=mysql+aiomysql://root:你的密码@127.0.0.1:3306/toutiao?charset=utf8mb4
API_V1_PREFIX=/api/v1
```

不要把真实密码提交到 Git。`.env` 已经被 `.gitignore` 忽略。

如果密码中包含 `@`、`#`、`/`、`:` 等特殊字符，需要先进行 URL 编码。例如：

```text
原密码：abc@123
连接密码：abc%40123
```

### 4. 启动并自动建表

配置完成后，直接用 IDE 的 `FastAPI` 运行配置，或者执行：

```powershell
python run.py
```

应用启动时会通过异步引擎自动创建 `users`、`news`、`favorites`、`histories` 四张表。
代码只负责建表，不负责创建 MySQL 数据库本身。

## 基础接口

- `POST /api/v1/users`
- `GET /api/v1/users`
- `POST /api/v1/news`
- `GET /api/v1/news`
- `POST /api/v1/favorites`
- `GET /api/v1/favorites/{user_id}`
- `DELETE /api/v1/favorites/{user_id}/{news_id}`
- `POST /api/v1/history`
- `GET /api/v1/history/{user_id}`
- `DELETE /api/v1/history/{user_id}`
