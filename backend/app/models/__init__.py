# 模型包初始化文件

# 首先导入 Base
from app.models.base import Base  # noqa

# 然后导入所有模型，确保它们在SQLAlchemy中注册
from app.models.user import User  # noqa
from app.models.vector_store import VectorStore  # noqa
from app.models.health_data import HealthData  # noqa
from app.models.diet_record import DietRecord  # noqa
from app.models.exercise_log import ExerciseLog  # noqa
from app.models.sleep_record import SleepRecord  # noqa
from app.models.health_goals import HealthGoal, GoalStatus, GoalType  # noqa
from app.models.symptom_records import SymptomRecord  # noqa
from app.models.body_measurements import BodyMeasurement  # noqa
from app.models.health_reminders import HealthReminder, ReminderFrequency, ReminderType  # noqa

__all__ = [
    'Base', 
    'User', 
    'VectorStore', 
    'HealthData', 
    'DietRecord', 
    'ExerciseLog',
    'SleepRecord',
    'HealthGoal',
    'GoalStatus',
    'GoalType',
    'SymptomRecord',
    'BodyMeasurement',
    'HealthReminder',
    'ReminderFrequency',
    'ReminderType'
]
