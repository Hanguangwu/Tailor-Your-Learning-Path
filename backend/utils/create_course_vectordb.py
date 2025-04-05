import os
import pandas as pd
import chromadb
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import json
from langchain_community.embeddings import OpenAIEmbeddings
from getOpenAIAPIKey import get_chatanywhere_api_key, get_chatanywhere_url
# 加载环境变量
load_dotenv()

# 获取OpenAI API密钥
# openai_api_key = os.getenv("OPENAI_API_KEY")
# if not openai_api_key:
#     raise ValueError("请在.env文件中设置OPENAI_API_KEY")

# 初始化嵌入模型
# embeddings = OpenAIEmbeddings(
#     model="text-embedding-ada-002",
#     openai_api_key=openai_api_key
# )
embeddings = OpenAIEmbeddings(
    #model="text-embedding-ada-002",
    api_key=get_chatanywhere_api_key(),
    base_url=get_chatanywhere_url()
)
# 初始化ChromaDB客户端
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
os.makedirs(CHROMA_DB_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# 创建或获取集合
collection = chroma_client.get_or_create_collection(
    name="course_collection",
    metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
)

def process_csv_files():
    """处理所有CSV文件并存储到向量数据库"""
    # 数据目录
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    # 处理Coursera数据
    # coursera_path = os.path.join(data_dir, "coursera.csv")
    # if os.path.exists(coursera_path):
    #     print(f"处理Coursera数据: {coursera_path}")
    #     process_coursera_data(coursera_path)
    
    # 处理edX数据
    # edx_path = os.path.join(data_dir, "edx_courses.csv")
    # if os.path.exists(edx_path):
    #     print(f"处理edX数据: {edx_path}")
    #     process_edx_data(edx_path)
    
    # 处理MOOC数据
    # mooc_path = os.path.join(data_dir, "mooc.csv")
    # if os.path.exists(mooc_path):
    #     print(f"处理MOOC数据: {mooc_path}")
    #     process_mooc_data(mooc_path)

    mooc_path = os.path.join(data_dir, "mooc.csv")
    if os.path.exists(mooc_path):
        print(f"处理MOOC数据: {mooc_path}")
        process_mooc_data(mooc_path)

def process_coursera_data(file_path):
    """处理Coursera数据"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        # 如果编码错误，尝试其他编码
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='latin1')
        except:
            df = pd.read_csv(file_path, encoding='gbk')
    
    # 处理每一行数据
    for index, row in df.iterrows():
        try:
            # 提取关键字段
            #course_id = f"coursera_{index}"
            course_id = str(row.get('course_id', ''))
            title = str(row.get('course_name', '')) if 'course_name' in df.columns else str(row.get('name', ''))
            description = str(row.get('description', '')) if 'description' in df.columns else ''
            skills = str(row.get('skills', '')) if 'skills' in df.columns else ''
            
            # 创建课程文档
            course_doc = {
                "id": course_id,
                "title": title,
                "description": description,
                "skills": skills,
                "platform": "Coursera",
                "source": "coursera.csv"
            }
            
            # 创建文本表示
            text_representation = f"课程标题: {title}\n描述: {description}\n技能: {skills}\n平台: Coursera"
            
            # 生成嵌入向量
            embedding = embeddings.embed_query(text_representation)
            
            # 存储到ChromaDB
            collection.add(
                ids=[course_id],
                embeddings=[embedding],
                documents=[text_representation],
                metadatas=[course_doc]
            )
            
            if index % 100 == 0:
                print(f"已处理 {index} 条Coursera课程数据")
                
        except Exception as e:
            print(f"处理Coursera课程时出错 (行 {index}): {str(e)}")

def process_edx_data(file_path):
    """处理edX数据"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='latin1')
        except:
            df = pd.read_csv(file_path, encoding='gbk')
    
    for index, row in df.iterrows():
        try:
            # 提取关键字段
            course_id = f"edx_{index}"
            title = str(row.get('title', '')) if 'title' in df.columns else str(row.get('name', ''))
            description = str(row.get('description', '')) if 'description' in df.columns else ''
            subjects = str(row.get('subjects', '')) if 'subjects' in df.columns else ''
            
            # 创建课程文档
            course_doc = {
                "id": course_id,
                "title": title,
                "description": description,
                "subjects": subjects,
                "platform": "edX",
                "source": "edx_courses.csv"
            }
            
            # 创建文本表示
            text_representation = f"课程标题: {title}\n描述: {description}\n学科: {subjects}\n平台: edX"
            
            # 生成嵌入向量
            embedding = embeddings.embed_query(text_representation)
            
            # 存储到ChromaDB
            collection.add(
                ids=[course_id],
                embeddings=[embedding],
                documents=[text_representation],
                metadatas=[course_doc]
            )
            
            if index % 100 == 0:
                print(f"已处理 {index} 条edX课程数据")
                
        except Exception as e:
            print(f"处理edX课程时出错 (行 {index}): {str(e)}")

def process_mooc_data(file_path):
    """处理MOOC数据"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='latin1')
        except:
            df = pd.read_csv(file_path, encoding='gbk')
    
    for index, row in df.iterrows():
        try:
            # 提取关键字段
            course_id = f"mooc_{index}"
            title = str(row.get('课程名称', '')) if '课程名称' in df.columns else str(row.get('name', ''))
            school = str(row.get('开课机构', '')) if '开课机构' in df.columns else ''
            teacher = str(row.get('教师', '')) if '教师' in df.columns else ''
            category = str(row.get('课程类别', '')) if '课程类别' in df.columns else ''
            
            # 创建课程文档
            course_doc = {
                "id": course_id,
                "title": title,
                "school": school,
                "teacher": teacher,
                "category": category,
                "platform": "MOOC",
                "source": "mooc.csv"
            }
            
            # 创建文本表示
            text_representation = f"课程标题: {title}\n开课机构: {school}\n教师: {teacher}\n课程类别: {category}\n平台: MOOC"
            
            # 生成嵌入向量
            embedding = embeddings.embed_query(text_representation)
            
            # 存储到ChromaDB
            collection.add(
                ids=[course_id],
                embeddings=[embedding],
                documents=[text_representation],
                metadatas=[course_doc]
            )
            
            if index % 100 == 0:
                print(f"已处理 {index} 条MOOC课程数据")
                
        except Exception as e:
            print(f"处理MOOC课程时出错 (行 {index}): {str(e)}")

if __name__ == "__main__":
    print("开始处理课程数据并存储到向量数据库...")
    process_csv_files()
    print(f"处理完成。数据已存储到: {CHROMA_DB_PATH}")
    print(f"向量数据库中的课程总数: {collection.count()}")