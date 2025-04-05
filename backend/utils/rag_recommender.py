import os
import chromadb  # ChromaDB 向量数据库
from openai import OpenAI  # OpenAI 客户端
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

# 获取OpenAI API密钥
# openai_api_key = os.getenv("OPENAI_API_KEY")
# if not openai_api_key:
#     raise ValueError("请在.env文件中设置OPENAI_API_KEY")

from getOpenAIAPIKey import get_chatanywhere_api_key, get_chatanywhere_url

embeddings = OpenAIEmbeddings(
    api_key=get_chatanywhere_api_key(),
    base_url=get_chatanywhere_url()
)
# 初始化 OpenAI 客户端 (替换成自己的 API 信息)
# client = OpenAI(
#     api_key=get_chatanywhere_api_key(),
#     base_url=get_chatanywhere_url()
# )

# # 初始化嵌入模型
# embeddings = OpenAIEmbeddings(
#     model="text-embedding-ada-002",
#     openai_api_key=openai_api_key
# )

# 初始化LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=get_chatanywhere_api_key(),
    base_url=get_chatanywhere_url()
)

# 初始化ChromaDB客户端
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# 获取集合
collection = chroma_client.get_or_create_collection(
    name="course_collection",
    metadata={"hnsw:space": "cosine"}
)

# 定义提示模板
template = """
你是一个专业的学习路径推荐系统，根据用户信息和可用课程提供个性化的课程推荐。

用户信息:
{user_info}

以下是根据用户需求检索到的相关课程:
{courses}

请根据用户的背景、兴趣、技能和学习目标，从上述课程中推荐最适合的{count}门课程。
对于每门推荐的课程，请提供详细的推荐理由，解释为什么这门课程适合该用户。

请以以下JSON格式返回结果:
[
    {{
        "course_id": "课程ID",
        "title": "课程标题",
        "description": "课程描述",
        "reason": "详细的推荐理由"
    }}
]

确保你的推荐是多样化的，涵盖用户的不同兴趣和需求。
"""

prompt = ChatPromptTemplate.from_template(template)

def format_user_info(user_data):
    """格式化用户信息"""
    info = []
    
    if user_data.get("username"):
        info.append(f"- 用户名: {user_data.get('username')}")
    
    if user_data.get("age"):
        info.append(f"- 年龄: {user_data.get('age')}")
    
    if user_data.get("education"):
        info.append(f"- 学历: {user_data.get('education')}")
    
    if user_data.get("industry"):
        info.append(f"- 行业: {user_data.get('industry')}")
    
    if user_data.get("jobTitle"):
        info.append(f"- 职位: {user_data.get('jobTitle')}")
    
    if user_data.get("careerPath"):
        info.append(f"- 职业发展阶段: {user_data.get('careerPath')}")
    
    if user_data.get("interests"):
        interests = user_data.get("interests", [])
        if interests:
            info.append(f"- 兴趣领域: {', '.join(interests)}")
    
    if user_data.get("technicalSkills"):
        tech_skills = user_data.get("technicalSkills", [])
        if tech_skills:
            info.append(f"- 技术技能: {', '.join(tech_skills)}")
    
    if user_data.get("softSkills"):
        soft_skills = user_data.get("softSkills", [])
        if soft_skills:
            info.append(f"- 软技能: {', '.join(soft_skills)}")
    
    if user_data.get("tools"):
        tools = user_data.get("tools", [])
        if tools:
            info.append(f"- 工具偏好: {', '.join(tools)}")
    
    if user_data.get("learningGoals"):
        goals = user_data.get("learningGoals", [])
        if goals:
            info.append(f"- 学习目标: {', '.join(goals)}")
    
    if user_data.get("goalDescription"):
        info.append(f"- 目标描述: {user_data.get('goalDescription')}")
    
    if user_data.get("learningPreferences"):
        prefs = user_data.get("learningPreferences", [])
        if prefs:
            info.append(f"- 学习方式偏好: {', '.join(prefs)}")
    
    return "\n".join(info)

def get_relevant_courses(user_data, n_results=10):
    """获取与用户相关的课程"""
    # 构建查询文本
    query_parts = []
    
    if user_data.get("interests"):
        query_parts.extend(user_data.get("interests", []))
    
    if user_data.get("technicalSkills"):
        query_parts.extend(user_data.get("technicalSkills", []))
    
    if user_data.get("industry"):
        query_parts.append(user_data.get("industry"))
    
    if user_data.get("jobTitle"):
        query_parts.append(user_data.get("jobTitle"))
    
    if user_data.get("learningGoals"):
        query_parts.extend(user_data.get("learningGoals", []))
    
    if user_data.get("goalDescription"):
        query_parts.append(user_data.get("goalDescription"))
    
    # 如果没有足够的查询信息，使用一些通用术语
    if len(query_parts) < 2:
        if user_data.get("username"):
            query_parts.append(f"适合{user_data.get('username')}的课程")
        query_parts.append("推荐课程")
    
    # 构建查询文本
    query_text = " ".join(query_parts)
    
    # 生成查询向量
    query_embedding = embeddings.embed_query(query_text)
    
    # 执行相似性查询
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    # 格式化结果
    formatted_courses = []
    for i in range(len(results["ids"][0])):
        course_id = results["ids"][0][i]
        metadata = results["metadatas"][0][i]
        
        course_info = {
            "course_id": course_id,
            "title": metadata.get('course_name', ''),
            "description": metadata.get('description', ''),
            "reason": "根据用户的兴趣和技能推荐"  # 这里可以根据需要生成更详细的推荐理由
        }
        
        formatted_courses.append(course_info)
    
    return formatted_courses

def recommend_courses(user_data, count=5):
    """基于RAG为用户推荐课程"""
    try:
        # 格式化用户信息
        user_info = format_user_info(user_data)
        
        # 获取相关课程
        courses = get_relevant_courses(user_data, n_results=15)  # 获取更多课程供LLM选择
        
        # 构建RAG链
        rag_chain = (
            {"user_info": lambda _: user_info, 
             "courses": lambda _: courses,
             "count": lambda _: str(count)}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # 执行RAG链
        response = rag_chain.invoke({})
        
        # 解析JSON响应
        try:
            recommendations = json.loads(response)
            print(recommendations)
            return recommendations
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试提取JSON部分
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                recommendations = json.loads(json_str)
                return recommendations
            else:
                raise ValueError("无法解析推荐结果")
        
    except Exception as e:
        print(f"推荐课程时出错: {str(e)}")
        raise

# if __name__ == "__main__":
#     # 测试用例
#     test_user = {
#         "username": "测试用户",
#         "age": 25,
#         "education": "本科",
#         "industry": "IT",
#         "jobTitle": "软件工程师",
#         "interests": ["人工智能", "机器学习", "编程"],
#         "technicalSkills": ["Python", "数据分析"],
#         "learningGoals": ["提升技术能力", "职业发展"],
#         "goalDescription": "希望学习人工智能和机器学习相关知识，提升职业竞争力"
#     }
    
#     recommendations = recommend_courses(test_user, count=3)
#     print(json.dumps(recommendations, ensure_ascii=False, indent=2))