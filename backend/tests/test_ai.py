import requests

def test_ai():
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/ai/chat",
            json={"message": "今天天气怎么样，请介绍一下自己"}
        )
        response.raise_for_status()  # 检查响应状态
        result = response.json()
        print("响应内容:", result)
        return result
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

if __name__ == "__main__":
    test_ai()



# from openai import OpenAI
# client = OpenAI(
#     base_url='https://xiaoai.plus/v1',
#     # sk-xxx替换为自己的key
#     api_key='sk-NBiPNo1NgPoOyg02nsoK0WYqHVRtf1wV9v2qsLyRU0CqMYiO'
# )
# completion = client.chat.completions.create(
#   model="gpt-4o",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Hello!"}
#   ]
# )
# print(completion.choices[0].message)