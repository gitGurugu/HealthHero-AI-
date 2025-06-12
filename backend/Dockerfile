FROM python:3.10-slim

WORKDIR /app/

# 安装依赖
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY . /app/

# 设置环境变量
ENV PYTHONPATH=/app

# 运行预启动脚本
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 