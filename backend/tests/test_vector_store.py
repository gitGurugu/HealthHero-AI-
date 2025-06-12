from sqlalchemy.orm import Session, sessionmaker
from app.models.vector_store import VectorStore
from app.db.session import engine
import json
import numpy as np
from sqlalchemy import text

def test_vector_store():
    # 创建会话工厂
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()

    try:
        # 创建测试数据
        test_vector = np.random.rand(1536)
        test_data = VectorStore(
            content="这是一个测试文本",
            embedding=json.dumps(test_vector.tolist()),
            source="test",
            meta_info=json.dumps({"type": "test"})
        )
        
        # 插入数据并立即提交
        session.add(test_data)
        session.commit()
        print("\n数据已提交")
        
        # 立即验证插入结果
        stored_data = session.query(VectorStore).order_by(VectorStore.id.desc()).first()
        if stored_data:
            print("\n=== 新插入的向量数据 ===")
            print(f"ID: {stored_data.id}")
            print(f"内容: {stored_data.content}")
            print(f"向量维度: {len(json.loads(stored_data.embedding))}")
            print(f"来源: {stored_data.source}")
            print(f"创建时间: {stored_data.created_at}")
            
            # 查询总记录数
            count = session.query(VectorStore).count()
            print(f"\n数据库中共有 {count} 条记录")
            
            # 查询具体内容匹配的记录数
            content_count = session.query(VectorStore).filter_by(content="这是一个测试文本").count()
            print(f"匹配当前内容的记录数: {content_count}")
            
        else:
            print("\n错误：未能找到刚插入的数据")
            
    except Exception as e:
        session.rollback()
        print(f"\n发生错误: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    # 先清理可能存在的重复数据
    with Session(engine) as cleanup_session:
        try:
            cleanup_session.query(VectorStore).filter_by(content="这是一个测试文本").delete()
            cleanup_session.commit()
            print("清理完成")
        except Exception as e:
            cleanup_session.rollback()




    test_vector_store()    # 运行测试                print(f"清理时发生错误: {str(e)}")            print(f"清理时发生错误: {str(e)}")
    
    # 运行测试
    test_vector_store()