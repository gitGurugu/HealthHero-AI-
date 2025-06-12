import asyncio
import json
from datetime import datetime
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.rag_service import RAGService
import logging
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 健康主题列表
HEALTH_TOPICS = [
    "营养与饮食", "运动健身", "心理健康", "睡眠质量", 
    "疾病预防", "慢性病管理"
]

async def generate_health_content(topic: str, count: int = 5):
    """使用 GPT 生成健康知识"""
    try:
        # 修复 API 基础 URL
        base_url = settings.OPENAI_BASE_URL.rstrip('/')
        if not base_url.endswith('/v1'):
            base_url = f"{base_url}/v1"
            
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=base_url
        )
        
        logger.info(f"使用 API URL: {base_url}")
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的医疗健康顾问。"},
                {"role": "user", "content": f"""
请生成{count}条关于"{topic}"的健康知识，每条100-200字。
要求：
1. 内容准确专业
2. 通俗易懂
3. 实用性强
4. 每条知识独立成段
5. 直接返回内容，不要带序号
                """}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        knowledge_points = [p.strip() for p in content.split('\n\n') if p.strip()]
        return knowledge_points
        
    except Exception as e:
        logger.error(f"生成内容失败: {str(e)}")
        logger.error(f"API配置: base_url={base_url}")
        return []

async def main():
    rag = RAGService()
    
    total_count = 0
    target_count = 1000
    pbar = tqdm(total=target_count, desc="生成进度")
    all_content = []
    
    try:
        while total_count < target_count:
            for topic in HEALTH_TOPICS:
                batch_size = min(5, target_count - total_count)
                if batch_size <= 0:
                    break
                    
                contents = await generate_health_content(topic, batch_size)
                
                for content in contents:
                    if total_count >= target_count:
                        break
                        
                    try:
                        success = await rag.store_vector(
                            content=content,
                            source=topic
                        )
                        if success:
                            all_content.append({
                                "content": content,
                                "topic": topic,
                                "timestamp": datetime.now().isoformat()
                            })
                            total_count += 1
                            pbar.update(1)
                            
                    except Exception as e:
                        logger.error(f"存储失败: {str(e)}")
                        
                await asyncio.sleep(1)
                
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
    finally:
        pbar.close()
        
        # 保存 JSON 文件
        json_path = "data/generated_health_knowledge.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "total_count": total_count,
                "generate_time": datetime.now().isoformat(),
                "topics": HEALTH_TOPICS,
                "knowledge": all_content
            }, f, ensure_ascii=False, indent=2)
        
        # 保存 Markdown 文件
        md_path = "data/generated_health_knowledge.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# 健康知识库\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总条目：{total_count}\n\n")
            
            topic_content = {}
            for item in all_content:
                if item["topic"] not in topic_content:
                    topic_content[item["topic"]] = []
                topic_content[item["topic"]].append(item["content"])
            
            for topic, contents in topic_content.items():
                f.write(f"## {topic}\n\n")
                for content in contents:
                    f.write(f"- {content}\n\n")
        
        logger.info(f"成功生成并存储了 {total_count} 条健康知识")
        logger.info(f"JSON文件已保存至: {json_path}")
        logger.info(f"Markdown文件已保存至: {md_path}")

if __name__ == "__main__":
    asyncio.run(main())