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

from getOpenAIAPIKey import get_chatanywhere_api_key, get_chatanywhere_url

embeddings = OpenAIEmbeddings(
    api_key=get_chatanywhere_api_key(),
    base_url=get_chatanywhere_url()
)

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
    """精简格式化用户信息，减少 token 消耗"""
    info = []
    
    # 只保留最关键的用户信息
    if user_data.get("username"):
        info.append(f"用户: {user_data.get('username')}")
    
    # 合并教育和职业信息
    edu_job = []
    if user_data.get("education"):
        edu_job.append(user_data.get('education'))
    if user_data.get("industry"):
        edu_job.append(user_data.get('industry'))
    if user_data.get("jobTitle"):
        edu_job.append(user_data.get('jobTitle'))
    
    if edu_job:
        info.append(f"背景: {', '.join(edu_job)}")
    
    # 合并技能信息
    skills = []
    if user_data.get("technicalSkills"):
        skills.extend(user_data.get("technicalSkills", []))
    if user_data.get("softSkills"):
        skills.extend(user_data.get("softSkills", [])[:2])  # 限制软技能数量
    
    if skills:
        info.append(f"技能: {', '.join(skills[:5])}")  # 限制技能数量
    
    # 合并兴趣和目标
    interests_goals = []
    if user_data.get("interests"):
        interests_goals.extend(user_data.get("interests", [])[:3])  # 限制兴趣数量
    if user_data.get("learningGoals"):
        interests_goals.extend(user_data.get("learningGoals", [])[:2])  # 限制目标数量
    
    if interests_goals:
        info.append(f"兴趣和目标: {', '.join(interests_goals)}")
    
    # 只有在有明确描述时才添加
    if user_data.get("goalDescription"):
        # 截断目标描述，减少 token
        desc = user_data.get('goalDescription')
        if len(desc) > 100:
            desc = desc[:100] + "..."
        info.append(f"目标: {desc}")
    
    return "\n".join(info)

def get_relevant_courses(user_data, n_results=10):
    """获取与用户相关的课程，精简描述以减少 token 消耗"""
    
    # 构建查询文本
    query_parts = []
    
    if user_data.get("interests"):
        query_parts.extend(user_data.get("interests", [])[:3])  # 限制兴趣数量
    
    if user_data.get("technicalSkills"):
        query_parts.extend(user_data.get("technicalSkills", [])[:3])  # 限制技能数量
    
    if user_data.get("industry"):
        query_parts.append(user_data.get("industry"))
    
    if user_data.get("jobTitle"):
        query_parts.append(user_data.get("jobTitle"))
    
    if user_data.get("learningGoals"):
        query_parts.extend(user_data.get("learningGoals", [])[:2])  # 限制目标数量
    
    # 如果没有足够的查询信息，使用一些通用术语
    if len(query_parts) < 2:
        if user_data.get("username"):
            query_parts.append(f"适合{user_data.get('username')}的课程")
        query_parts.append("推荐课程")
    
    # 构建查询文本
    query_text = " ".join(query_parts[:10])  # 限制查询文本长度
    
    # 生成查询向量
    query_embedding = embeddings.embed_query(query_text)
    
    # 获取用户已选择的课程ID列表
    selected_courses = user_data.get("selected_courses", [])
    
    # 执行相似性查询 - 减少查询数量以节省 token
    additional_results = min(len(selected_courses), 5)  # 限制额外查询数量
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results + additional_results, 20)  # 限制最大查询数量
    )
    
    # 格式化结果并过滤掉已选择的课程
    formatted_courses = []
    for i in range(len(results["ids"][0])):
        course_id = results["ids"][0][i]
        
        # 跳过已选择的课程
        if course_id in selected_courses:
            continue
            
        metadata = results["metadatas"][0][i]
        
        # 精简课程描述，减少 token 消耗
        description = metadata.get('description', '')
        if len(description) > 100:  # 限制描述长度
            description = description[:100] + "..."
        
        course_info = {
            "course_id": course_id,
            "title": metadata.get('course_name', '')[:50],  # 限制标题长度
            "description": description,
        }
        
        formatted_courses.append(course_info)
        
        # 如果已经收集了足够的课程，就停止
        if len(formatted_courses) >= min(n_results, 10):  # 限制最大课程数量
            break
    
    return formatted_courses

def recommend_courses(user_data, count=5):
    """基于RAG为用户推荐课程，优化 token 消耗"""
    try:
        # 限制推荐数量，减少 token 消耗
        count = min(count, 10)
        
        # 格式化用户信息
        user_info = format_user_info(user_data)
        
        # 获取相关课程 - 过滤掉已选择的课程，减少获取的课程数量
        courses = get_relevant_courses(user_data, n_results=10)  # 减少获取的课程数量
        
        # 如果过滤后没有足够的课程可推荐
        if not courses:
            print("没有足够的未选择课程可供推荐")
            return []
        
        # 进一步限制传递给 LLM 的课程数量
        limited_courses = courses[:min(len(courses), 8)]
            
        # 构建RAG链
        rag_chain = (
            {"user_info": lambda _: user_info, 
             "courses": lambda _: limited_courses,
             "count": lambda _: str(min(count, len(limited_courses)))}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # 执行RAG链
        response = rag_chain.invoke({})
        
        # 解析JSON响应
        try:
            recommendations = json.loads(response)
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
        # 如果是 token 限制错误，返回一个简单的推荐列表
        # 获取相关课程 - 过滤掉已选择的课程，减少获取的课程数量
        courses = get_relevant_courses(user_data, n_results=10)  # 减少获取的课程数量
        if "token" in str(e).lower() and courses:
            print("检测到 token 限制错误，返回简化推荐")
            return [{"course_id": c["course_id"], 
                     "title": c["title"], 
                     "description": c["description"], 
                     "reason": "基于用户兴趣和技能推荐"} 
                    for c in courses[:min(count, len(courses))]]
        raise