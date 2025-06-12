import requests

def test_articles():
    # 登录获取 token
    login_response = requests.post(
        "http://localhost:8000/api/v1/login/access-token",
        data={"username": "admin", "password": "admin"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建文章
    article_data = {
        "title": "手语入门指南",
        "content": "这是一篇关于手语基础知识的文章..."
    }
    create_response = requests.post(
        "http://localhost:8000/api/v1/articles/",
        json=article_data,
        headers=headers
    )
    print("创建文章响应:", create_response.json())
    
    # 获取所有文章
    articles_response = requests.get(
        "http://localhost:8000/api/v1/articles/"
    )
    print("所有文章:", articles_response.json())

if __name__ == "__main__":
    test_articles()