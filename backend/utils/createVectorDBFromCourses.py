import os
import chromadb
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from getOpenAIAPIKey import get_chatanywhere_api_key, get_chatanywhere_url
from bson import ObjectId
# 加载环境变量
load_dotenv()

# 初始化 OpenAI 嵌入模型
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

# 获取或创建集合
collection = chroma_client.get_or_create_collection(
    name="course_collection",
    metadata={"hnsw:space": "cosine"}
)

# # MongoDB 连接
client = MongoClient(os.getenv("MONGODB_URL"))
db = client.get_database("CourseRec")  # 替换为你的数据库名称
courses_collection = db.get_collection("courses")
#from database import db

# 进度文件路径
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "count.txt")

def get_last_processed_index():
    """获取上次处理的索引"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as file:
            return int(file.read().strip())
    return -1

def update_progress(index):
    """更新进度文件"""
    with open(PROGRESS_FILE, 'w') as file:
        file.write(str(index))

def create_vector_database():
    """创建向量数据库"""
    last_processed_index = get_last_processed_index()
    cursor = courses_collection.find().skip(last_processed_index + 1)

    for index, course in enumerate(cursor, start=last_processed_index + 1):
        try:
            # 将 ObjectId 转换为字符串
            course_id = str(course['_id'])
            title = course.get('course_name', '')
            description = course.get('description', '')

            # 创建文本表示
            text_representation = f"课程标题: {title}\n描述: {description}"

            # 生成嵌入向量
            embedding = embeddings.embed_query(text_representation)

            # 将所有元数据中的 ObjectId 转换为字符串
            course_metadata = {k: str(v) if isinstance(v, ObjectId) else v for k, v in course.items()}

            # 存储到 ChromaDB
            collection.add(
                ids=[course_id],
                embeddings=[embedding],
                documents=[text_representation],
                metadatas=[course_metadata]
            )

            update_progress(index)  # 更新进度

            if index % 100 == 0:
                print(f"已处理 {index} 条课程数据")

        except Exception as e:
            print(f"处理课程数据时出错 (索引 {index}): {str(e)}")

if __name__ == "__main__":
    print("开始创建向量数据库...")
    create_vector_database()
    print("向量数据库创建完成。")