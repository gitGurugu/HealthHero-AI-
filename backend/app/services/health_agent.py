from typing import Dict, List
from app.services.base import AIBase
from app.services.rag_factory import get_rag_service
import logging

logger = logging.getLogger(__name__)

class HealthAgent:
    def __init__(self, ai_service: AIBase):
        self.ai_service = ai_service
        self.rag = get_rag_service()
        
        # 定义任务类型和对应的处理方法
        self.tasks = {
            "饮食分析": self._analyze_diet,
            "运动规划": self._plan_exercise,
            "睡眠建议": self._sleep_advice,
            "健康知识": self._query_knowledge
        }

    async def process_request(self, message: str, user_data: Dict = None) -> str:
        """处理用户请求"""
        try:
            # 1. 识别任务类型
            task_type = self._identify_task(message)
            
            # 2. 获取相关知识库内容
            relevant_docs = await self.rag.search_similar(message, k=2)
            context = "\n".join([doc['content'] for doc in relevant_docs])
            
            # 3. 根据任务类型处理请求
            if task_type in self.tasks:
                return await self.tasks[task_type](message, user_data, context)
            
            # 4. 处理通用查询
            return await self._handle_general_query(message, context)
            
        except Exception as e:
            logger.error(f"处理请求失败: {str(e)}")
            return "抱歉，我现在无法处理您的请求。请稍后再试。"

    async def process_request_stream(self, message: str, user_data: Dict = None):
        """流式处理用户请求"""
        try:
            # 1. 识别任务类型
            task_type = self._identify_task(message)
            
            # 2. 获取相关知识库内容
            relevant_docs = await self.rag.search_similar(message, k=2)
            context = "\n".join([doc['content'] for doc in relevant_docs])
            
            # 3. 根据任务类型处理请求
            if task_type == "饮食分析":
                async for chunk in self._analyze_diet_stream(message, user_data, context):
                    yield chunk
            elif task_type == "运动规划":
                async for chunk in self._plan_exercise_stream(message, user_data, context):
                    yield chunk
            elif task_type == "睡眠建议":
                async for chunk in self._sleep_advice_stream(message, user_data, context):
                    yield chunk
            elif task_type == "健康知识":
                async for chunk in self._query_knowledge_stream(message, user_data, context):
                    yield chunk
            else:
                # 4. 处理通用查询
                async for chunk in self._handle_general_query_stream(message, context):
                    yield chunk
            
        except Exception as e:
            logger.error(f"流式处理请求失败: {str(e)}")
            yield "抱歉，我现在无法处理您的请求。请稍后再试。"

    async def _analyze_diet(self, message: str, user_data: Dict, context: str) -> str:
        """分析饮食情况并给出建议"""
        analysis_prompt = f"""
        参考知识：
        {context}
        
        用户信息：
        - 年龄：{user_data.get('age')}
        - 身高：{user_data.get('height')}
        - 体重：{user_data.get('weight')}
        - BMI：{self._calculate_bmi(user_data)}
        
        饮食记录：
        {user_data.get('diet_records', [])}
        
        用户问题：{message}
        
        请基于以上信息进行分析并给出个性化的饮食建议。
        """
        return await self.ai_service.get_response(analysis_prompt)

    async def _plan_exercise(self, message: str, user_data: Dict, context: str) -> str:
        """制定个性化运动计划"""
        plan_prompt = f"""
        参考知识：
        {context}
        
        用户基础信息：
        - 年龄：{user_data.get('age')}
        - 身高：{user_data.get('height')}
        - 体重：{user_data.get('weight')}
        - BMI：{self._calculate_bmi(user_data)}
        - 运动目标：{message}
        - 运动禁忌：{user_data.get('exercise_contraindications', '无')}
        
        请基于以上信息制定安全、科学、个性化的运动计划。
        """
        return await self.ai_service.get_response(plan_prompt)

    async def _sleep_advice(self, message: str, user_data: Dict, context: str) -> str:
        """提供睡眠建议"""
        sleep_prompt = f"""
        参考知识：
        {context}
        
        用户睡眠情况：
        - 平均睡眠时间：{user_data.get('avg_sleep_hours')}
        - 入睡困难：{user_data.get('sleep_issues', [])}
        - 作息时间：{user_data.get('sleep_schedule', {})}
        
        用户问题：{message}
        
        请基于以上信息提供个性化的睡眠改善建议。
        """
        return await self.ai_service.get_response(sleep_prompt)

    async def _query_knowledge(self, message: str, user_data: Dict, context: str) -> str:
        """查询健康知识"""
        knowledge_prompt = f"""
        参考知识：
        {context}
        
        用户问题：{message}
        
        请基于参考知识和专业见解回答用户问题。如果信息不足，可以补充其他相关的专业知识。
        """
        return await self.ai_service.get_response(knowledge_prompt)

    async def _handle_general_query(self, message: str, context: str) -> str:
        """处理通用健康查询"""
        general_prompt = f"""
        参考知识：
        {context}
        
        用户问题：{message}
        
        请提供专业、准确的回答。注意：
        1. 不要给出医疗诊断
        2. 对于需要就医的情况，建议用户及时就医
        3. 保持答复的科学性和可操作性
        """
        return await self.ai_service.get_response(general_prompt)

    async def _analyze_diet_stream(self, message: str, user_data: Dict, context: str):
        """流式分析饮食情况并给出建议"""
        analysis_prompt = f"""
        参考知识：
        {context}
        
        用户信息：
        - 年龄：{user_data.get('age')}
        - 身高：{user_data.get('height')}
        - 体重：{user_data.get('weight')}
        - BMI：{self._calculate_bmi(user_data)}
        
        饮食记录：
        {user_data.get('diet_records', [])}
        
        用户问题：{message}
        
        请基于以上信息进行分析并给出个性化的饮食建议。
        """
        async for chunk in self.ai_service.get_response_stream(analysis_prompt):
            yield chunk

    async def _plan_exercise_stream(self, message: str, user_data: Dict, context: str):
        """流式制定个性化运动计划"""
        plan_prompt = f"""
        参考知识：
        {context}
        
        用户基础信息：
        - 年龄：{user_data.get('age')}
        - 身高：{user_data.get('height')}
        - 体重：{user_data.get('weight')}
        - BMI：{self._calculate_bmi(user_data)}
        - 运动目标：{message}
        - 运动禁忌：{user_data.get('exercise_contraindications', '无')}
        
        请基于以上信息制定安全、科学、个性化的运动计划。
        """
        async for chunk in self.ai_service.get_response_stream(plan_prompt):
            yield chunk

    async def _sleep_advice_stream(self, message: str, user_data: Dict, context: str):
        """流式提供睡眠建议"""
        sleep_prompt = f"""
        参考知识：
        {context}
        
        用户睡眠情况：
        - 平均睡眠时间：{user_data.get('avg_sleep_hours')}
        - 入睡困难：{user_data.get('sleep_issues', [])}
        - 作息时间：{user_data.get('sleep_schedule', {})}
        
        用户问题：{message}
        
        请基于以上信息提供个性化的睡眠改善建议。
        """
        async for chunk in self.ai_service.get_response_stream(sleep_prompt):
            yield chunk

    async def _query_knowledge_stream(self, message: str, user_data: Dict, context: str):
        """流式查询健康知识"""
        knowledge_prompt = f"""
        参考知识：
        {context}
        
        用户问题：{message}
        
        请基于参考知识和专业见解回答用户问题。如果信息不足，可以补充其他相关的专业知识。
        """
        async for chunk in self.ai_service.get_response_stream(knowledge_prompt):
            yield chunk

    async def _handle_general_query_stream(self, message: str, context: str):
        """流式处理通用健康查询"""
        general_prompt = f"""
        参考知识：
        {context}
        
        用户问题：{message}
        
        请提供专业、准确的回答。注意：
        1. 不要给出医疗诊断
        2. 对于需要就医的情况，建议用户及时就医
        3. 保持答复的科学性和可操作性
        """
        async for chunk in self.ai_service.get_response_stream(general_prompt):
            yield chunk

    def _identify_task(self, message: str) -> str:
        """识别用户请求的任务类型"""
        keywords = {
            "饮食分析": ["饮食", "吃", "营养", "食谱", "减肥"],
            "运动规划": ["运动", "锻炼", "健身", "跑步", "力量"],
            "睡眠建议": ["睡眠", "失眠", "作息", "休息", "觉"],
            "健康知识": ["是什么", "怎么办", "如何", "科普", "介绍"]
        }
        
        for task, words in keywords.items():
            if any(word in message for word in words):
                return task
        return "general"

    def _calculate_bmi(self, user_data: Dict) -> float:
        """计算 BMI 指数"""
        try:
            height = float(user_data.get('height', 0)) / 100  # 转换为米
            weight = float(user_data.get('weight', 0))
            if height > 0 and weight > 0:
                return round(weight / (height * height), 2)
            return 0
        except:
            return 0