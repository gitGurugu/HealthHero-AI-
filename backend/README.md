# 数据库大作业后端

数据库大作业的后端 API。

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **SQLAlchemy**: ORM 工具
- **Pydantic**: 数据验证和设置管理
- **PostgreSQL**: 数据库
- **Alembic**: 数据库迁移工具
- **Docker**: 容器化
- **Loguru**: 日志管理

## 开发环境设置

### 前提条件

- Python 3.10+
- PostgreSQL
- Docker (可选)
- Make (可选，用于运行 Makefile 命令)

### 本地开发

1. 克隆仓库

```bash
git clone <repository-url>
cd SilentRhythm/backend
```

2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
# 或者使用Make
make install
```

4. 创建`.env`文件

```bash
cp .env.example .env
# 编辑.env文件，设置适当的值
```

5. 初始化数据库

```bash
python initial_data.py
# 或者使用Make
make db-init
```

6. 运行开发服务器

```bash
uvicorn app.main:app --reload
# 或者使用Make
make run
```

### 使用 Docker

1. 构建并启动容器

```bash
docker-compose up -d --build
```

2. 查看日志

```bash
docker-compose logs -f
```

3. 停止容器

```bash
docker-compose down
```

## API 文档

启动服务器后，可以在以下 URL 访问 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库迁移

使用 Alembic 进行数据库迁移：

1. 创建迁移

```bash
alembic revision --autogenerate -m "描述"
```

2. 应用迁移

```bash
alembic upgrade head
# 或者使用Make
make migrate
```

## 代码质量和测试

### 代码质量检查

```bash
# 使用black格式化代码
black app tests

# 使用isort排序导入
isort app tests

# 使用flake8检查代码质量
flake8 app tests

# 或者使用Make运行所有检查
make lint
```

### 运行测试

```bash
# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=app --cov-report=term --cov-report=html

# 或者使用Make
make test
```

### 安全检查

```bash
# 使用bandit检查安全漏洞
bandit -r app -x tests

# 使用safety检查依赖安全
safety check --full-report

# 或者使用Make
make security
```

## 常用 Make 命令

项目包含一个 Makefile，提供了一些常用命令：

```bash
# 显示帮助信息
make help

# 安装依赖
make install

# 运行代码质量检查
make lint

# 运行测试
make test

# 运行安全检查
make security

# 运行开发服务器
make run

# 运行数据库迁移
make migrate

# 初始化数据库
make db-init

# 清理临时文件
make clean
```

## 项目结构

```
backend/
├── alembic/              # 数据库迁移
├── app/                  # 应用程序代码
│   ├── api/              # API路由
│   │   └── api_v1/       # API版本1
│   │       ├── endpoints/# API端点
│   │       └── api.py    # API路由聚合
│   ├── core/             # 核心功能
│   │   ├── config.py     # 配置
│   │   ├── security.py   # 安全工具
│   │   ├── middleware.py # 中间件
│   │   └── logging.py    # 日志配置
│   ├── db/               # 数据库
│   │   ├── session.py    # 数据库会话
│   │   └── init_db.py    # 数据库初始化
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic模式
│   ├── services/         # 业务逻辑
│   ├── utils/            # 工具函数
│   └── main.py           # 应用程序入口
├── logs/                 # 日志文件
├── scripts/              # 脚本
│   ├── lint.py           # 代码质量检查
│   ├── test.py           # 测试
│   └── security.py       # 安全检查
├── tests/                # 测试
├── .env                  # 环境变量
├── .env.example          # 环境变量示例
├── .flake8               # Flake8配置
├── pyproject.toml        # 项目配置
├── alembic.ini           # Alembic配置
├── Dockerfile            # Docker配置
├── docker-compose.yml    # Docker Compose配置
├── Makefile              # Make命令
├── initial_data.py       # 初始数据脚本
├── prestart.py           # 预启动脚本
├── requirements.txt      # 依赖
└── README.md             # 文档
```

## 贡献指南

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证
<!-- http://127.0.0.1:8000/docs -->
[MIT](../LICENSE)