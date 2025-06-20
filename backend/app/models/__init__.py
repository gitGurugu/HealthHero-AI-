# 模型包初始化文件

# 首先导入 Base
from .base import Base
from .user import User
from .vector_store import VectorStore
from .exercise_log import ExerciseLog
from .health_goals import HealthGoal
from .sleep_record import SleepRecord
from .symptom_records import SymptomRecord
from .health_data import HealthData

# 导出所有模型，确保 Alembic 能够检测到它们
__all__ = [
    "Base",
    "User", 
    "VectorStore",
    "ExerciseLog",
    "HealthGoal",
    "SleepRecord",
    "SymptomRecord",
    "HealthData"
]
