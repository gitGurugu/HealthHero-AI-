import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 分钟
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    """
    尝试连接到数据库，确保数据库已准备好
    """
    try:
        db = SessionLocal()
        # 尝试创建会话
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    """
    主函数
    """
    logger.info("初始化服务")
    init()
    logger.info("服务已初始化：数据库已就绪")


if __name__ == "__main__":
    main() 