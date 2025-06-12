from sqlalchemy import create_engine
import logging
from urllib.parse import quote_plus

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 对密码进行URL编码
password = quote_plus("openGauss@1234")

# 构建连接URL
DATABASE_URL = f"postgresql://test1:{password}@116.205.100.45:26000/health"

try:
    # 创建引擎并打开详细日志
    engine = create_engine(DATABASE_URL, echo=True)
    
    # 测试连接
    with engine.connect() as connection:
        result = connection.execute("SELECT 1")
        logger.info("数据库连接成功！")
except Exception as e:
    logger.error(f"连接错误: {str(e)}")
    logger.error(f"连接URL: {DATABASE_URL}")