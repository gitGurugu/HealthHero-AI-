.PHONY: help install lint test security run migrate db-init clean

help:
	@echo "可用命令:"
	@echo "  make install    - 安装依赖"
	@echo "  make lint       - 运行代码质量检查"
	@echo "  make test       - 运行测试"
	@echo "  make security   - 运行安全检查"
	@echo "  make run        - 运行开发服务器"
	@echo "  make migrate    - 运行数据库迁移"
	@echo "  make db-init    - 初始化数据库"
	@echo "  make clean      - 清理临时文件"

install:
	pip install -r requirements.txt

lint:
	python scripts/lint.py

test:
	python scripts/test.py

security:
	python scripts/security.py

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

db-init:
	python initial_data.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	find . -type f -name *.pyc -delete
	find . -type f -name *.pyo -delete
	find . -type f -name *.pyd -delete
	find . -type f -name .coverage -delete
	find . -type f -name coverage.xml -delete
	find . -type f -name .coverage.* -delete 