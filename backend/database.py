from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URL"))
# 获取数据库名称，如果环境变量未设置则使用默认值
database_name = os.getenv("DATABASE_NAME")
if database_name is None:
    raise ValueError("DATABASE_NAME environment variable is not set")
db = client[database_name]

def init_db():
    # 创建唯一索引
    db.users.create_index("email", unique=True)
    
    # 预设兴趣选项
    interests = [
        "计算机", "数学", "艺术", "英语", "体育", "中医",
        "物理", "化学", "生物", "历史", "地理", "音乐"
    ]
    
    # 如果兴趣集合不存在，则创建
    if "interests" not in db.list_collection_names():
        db.interests.insert_many([{"name": interest} for interest in interests])
    
    # 为课程集合创建索引
    db.courses.create_index([
        ("course_name", "text"),
        ("description", "text"),
        ("category", "text")
    ])