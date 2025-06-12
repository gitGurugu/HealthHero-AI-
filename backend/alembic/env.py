import os
import sys
from logging.config import fileConfig
from urllib.parse import quote_plus

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 导入配置和模型
from app.core.config import settings
from app.models.base import Base  # 这里导入包含所有模型的 Base
# 导入所有模型以确保它们被注册到 metadata 中
from app.models import *  # 这会导入所有模型 
# this is the Alembic Config object
config = context.config

# 处理数据库 URL 中的特殊字符
db_url = settings.SQLALCHEMY_DATABASE_URI.replace('%', '%%')
config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置 metadata 目标
target_metadata = Base.metadata

# 添加 schema 支持
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and object.schema != "public":
        return False
    return True

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'offline' mode."""
    configuration = config.get_section(config.config_ini_section)
    
    # 打印调试信息
    print("MetaData 信息:")
    for table in Base.metadata.tables.values():
        print(f"表名: {table.name}")
        print(f"列: {[column.name for column in table.columns]}")
    
    configuration["sqlalchemy.url"] = settings.SQLALCHEMY_DATABASE_URI
    
    # 添加调试信息
    print("已加载的表:", Base.metadata.tables.keys())
    print("数据库 URL:", configuration["sqlalchemy.url"])
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            compare_type=True,
            version_table_schema="public"  # 指定version表的schema
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
