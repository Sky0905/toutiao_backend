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
├── frontend/         # 可直接由 FastAPI 托管的登录注册页面
│   ├── app.js        # 页面交互和接口调用
│   ├── config.js     # 前端接口地址配置
│   ├── index.html
│   └── styles.css
├── logs/              # 运行时日志目录，不提交到 Git
├── tests/
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## 启动

### PyCharm

项目已经配置好 `FastAPI` 运行配置：  测试

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
JWT_SECRET_KEY=请替换为随机长字符串
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REDIS_URL=redis://127.0.0.1:6379/0
REDIS_CACHE_TTL_SECONDS=300
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

## Redis 缓存

项目使用 `redis.asyncio` 连接 Redis。你的 Redis 3.0.504 版本较老，
因此项目固定使用 RESP2 协议，并建议 Python 依赖使用 `redis>=4.6,<5.0`。
配置项位于 `.env`：

```env
REDIS_URL=redis://127.0.0.1:6379/0
REDIS_CACHE_TTL_SECONDS=300
```

健康检查：

```http
GET /health/redis
```

新闻列表接口已接入缓存：

```http
GET /api/v1/news?page=1&page_size=20
```

处理流程：

```text
先查 Redis
Redis 命中 -> 直接返回缓存
Redis 未命中 -> 查询 MySQL -> 写入 Redis -> 返回结果
```

新增新闻后会自动清理：

```text
news:list:*
```

相关代码：

- `app/cache/redis.py`：Redis 连接、关闭、PING、按模式删除缓存
- `app/routers/news.py`：新闻列表缓存读写和新增新闻后清理缓存

## 用户认证

### 注册

```http
POST /api/v1/auth/register
Content-Type: application/json
```

请求体：

```json
{
  "username": "demo",
  "email": "demo@example.com",
  "password": "123456"
}
```

### 登录

```http
POST /api/v1/auth/login
Content-Type: application/json
```

登录成功后返回：

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

调用受保护接口时，在请求头中携带：

```http
Authorization: Bearer JWT_TOKEN
```

当前用户接口：

```http
GET /api/v1/auth/me
```

密码使用 bcrypt 哈希保存，JWT 使用 HS256 签名。JWT 密钥只放在 `.env`，不要提交到 GitHub。

## 前端页面

启动后直接访问：

<http://127.0.0.1:8000/>

前端文件位于 `frontend/`：

- `frontend/config.js`：修改接口前缀和接口地址
- `frontend/app.js`：修改登录注册交互
- `frontend/index.html`：修改页面结构
- `frontend/styles.css`：修改页面样式

页面会把登录成功后的 JWT 保存在浏览器 `localStorage`，请求当前用户时自动携带 Bearer Token。

## 统一响应格式

接口成功时统一返回：

```json
{
  "code": 0,
  "message": "登录成功",
  "data": {}
}
```

参数校验失败时返回：

```json
{
  "code": 42200,
  "message": "请求参数校验失败",
  "data": [
    {
      "field": "body.email",
      "message": "value is not a valid email address"
    }
  ]
}
```

项目保留真实 HTTP 状态码，例如 `401`、`404`、`409`、`422`、`500`，
同时在 JSON 中使用 `code` 和 `message` 方便前端统一处理。

删除接口使用 `204 No Content`，按照 HTTP 规范不返回 JSON 正文。

## 日志

日志由 [app/utils/app_logging.py](app/utils/app_logging.py) 统一配置：

- 控制台输出启动和请求日志
- 文件日志保存到 `logs/app.log`
- 单个日志文件达到 5 MB 后自动轮转
- 最多保留 5 个历史日志文件
- 请求日志包含请求 ID、请求方法、路径、状态码和耗时
- 未知异常会记录完整堆栈，但不会把堆栈返回给前端

全局异常处理器位于 `app/exceptions/handlers.py`，统一处理：

- `HTTPException`
- 请求参数校验异常
- 数据库完整性异常
- SQLAlchemy 数据库异常
- 未知服务器异常

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
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
