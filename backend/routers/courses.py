from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import db
from bson import ObjectId
from .auth import oauth2_scheme
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
router = APIRouter()

class Course(BaseModel):
    course_name: str
    description: str
    course_logo_url: str
    category: str
    difficulty: str
    course_url: str
    rating: float
    enrollment_count: int = 0

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # 确保SECRET_KEY和ALGORITHM存在且不为None
        secret_key = os.getenv("SECRET_KEY")
        algorithm = os.getenv("ALGORITHM")
        
        if not secret_key or not algorithm:
            raise HTTPException(
                status_code=500, 
                detail="服务器配置错误：缺少必要的认证参数"
            )
            
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证令牌")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证令牌")
@router.get("/featured")
async def get_featured_courses(
    page: int = 1, 
    page_size: int = 6, 
    current_user: str = Depends(get_current_user)
):
    try:
        # 获取用户信息和已选课程
        user = db.users.find_one({"_id": ObjectId(current_user)})
        selected_courses = user["selected_courses"] if user and "selected_courses" in user else []

        # 获取所有课程并按评分排序
        total_courses = db.courses.count_documents({})
        courses = list(db.courses.find().sort("rating", -1).skip((page - 1) * page_size).limit(page_size))
        
        # 处理每个课程的数据
        processed_courses = []
        for course in courses:
            processed_course = {
                "_id": str(course["_id"]),
                "course_name": course.get("course_name", ""),
                "course_url": course.get("course_url", ""),
                "course_logo_url": course.get("course_logo_url", ""),
                "category": course.get("category", ""),
                "difficulty": course.get("difficulty", ""),
                "description": course.get("description", ""),
                "rating": float(course.get("rating", 0)),
                "enrollment_count": course.get("enrollment_count", 0),
                "is_selected": course["_id"] in selected_courses
            }
            processed_courses.append(processed_course)
        
        return {
            "courses": processed_courses,
            "total": total_courses,
            "page": page,
            "page_size": page_size,
            "total_pages": 9  # 固定返回9页
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommended")
async def get_recommended_courses(current_user: str = Depends(get_current_user)):
    try:
        # 获取当前用户信息
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")
        
        # 获取所有用户和课程数据
        all_users = list(db.users.find())
        all_courses = list(db.courses.find())
        
        # 创建课程-用户矩阵
        course_ids = [str(course["_id"]) for course in all_courses]
        user_ids = [str(user["_id"]) for user in all_users]
        course_user_matrix = pd.DataFrame(0, index=pd.Index(course_ids), columns=pd.Index(user_ids))
        
        # 填充课程-用户矩阵
        for user in all_users:
            user_selected_courses = [str(course_id) for course_id in user.get("selected_courses", [])]
            for course_id in user_selected_courses:
                if course_id in course_user_matrix.index:
                    course_user_matrix.at[course_id, str(user["_id"])] = 1
        
        # 计算课程相似度
        course_similarity_matrix = cosine_similarity(course_user_matrix)
        course_similarity_df = pd.DataFrame(
            course_similarity_matrix, 
            index=course_user_matrix.index, 
            columns=course_user_matrix.index
        )
        
        # 获取用户已选课程
        user_courses = [str(course_id) for course_id in user.get("selected_courses", [])]
        
        # 计算推荐分数
        recommendations = pd.Series(dtype='float64')
        for course_id in user_courses:
            if course_id in course_similarity_df.index:
                sim_scores = course_similarity_df[course_id]
                recommendations = recommendations.add(sim_scores, fill_value=0)
        
        # 排除已选课程
        recommendations = recommendations[~recommendations.index.isin(user_courses)]
        
        # 获取推荐课程详情
        # 将推荐结果排序并获取前6个课程ID
        # 将Series转换为numpy数组并排序
        recommendations_array = np.array(recommendations)
        sorted_indices = np.argsort(recommendations_array)[::-1][:6]
        # 获取推荐课程ID列表
        # 获取推荐课程ID列表，使用recommendations的索引和值
        # 使用recommendations的索引获取推荐课程ID
        recommended_course_ids = [recommendations.index[i] for i in sorted_indices]
        recommended_courses = []
        
        for course_id in recommended_course_ids:
            # 确保course_id是字符串类型
            course = db.courses.find_one({"_id": ObjectId(str(course_id))})
            if course:
                processed_course = {
                    "_id": str(course["_id"]),
                    "course_name": course.get("course_name", ""),
                    "course_url": course.get("course_url", ""),
                    "course_logo_url": course.get("course_logo_url", ""),
                    "category": course.get("category", ""),
                    "difficulty": course.get("difficulty", ""),
                    "description": course.get("description", ""),
                    "rating": float(course.get("rating", 0)),
                    "enrollment_count": course.get("enrollment_count", 0),
                    "is_selected": False
                }
                recommended_courses.append(processed_course)
        
        return recommended_courses
    except Exception as e:
        print(f"推荐课程时出错: {str(e)}")  # 添加调试信息
        return []

@router.post("/select/{course_id}")
async def select_course(course_id: str, current_user: str = Depends(get_current_user)):
    try:
        # 检查课程是否存在
        course = db.courses.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="课程未找到")
        
        # 检查用户是否已选择该课程
        user = db.users.find_one({
            "_id": ObjectId(current_user),
            "selected_courses": ObjectId(course_id)
        })
        
        if user:
            return {"message": "已经选择过该课程"}
        
        # 更新用户的已选课程
        db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$addToSet": {"selected_courses": ObjectId(course_id)}}
        )
        
        # 更新课程的选课人数
        db.courses.update_one(
            {"_id": ObjectId(course_id)},
            {"$inc": {"enrollment_count": 1}}
        )
        
        return {"message": "选课成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/select/{course_id}")
async def unselect_course(course_id: str, current_user: str = Depends(get_current_user)):
    try:
        result = db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$pull": {"selected_courses": ObjectId(course_id)}}
        )
        
        if result.modified_count == 0:
            return {"message": "课程未被选择"}
            
        # 更新课程的选课人数
        db.courses.update_one(
            {"_id": ObjectId(course_id)},
            {"$inc": {"enrollment_count": -1}}
        )
        
        return {"message": "已取消选课"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/{course_id}")
async def get_course_detail(course_id: str, current_user: str = Depends(get_current_user)):
    try:
        # 查找课程
        course = db.courses.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 获取用户信息以检查课程状态
        user = db.users.find_one({"_id": ObjectId(current_user)})
        
        # 处理课程数据
        course_data = {
            "_id": str(course["_id"]),
            "course_name": course.get("course_name", ""),
            "description": course.get("description", ""),
            "course_url": course.get("course_url", ""),
            "course_logo_url": course.get("course_logo_url", ""),
            "category": course.get("category", ""),
            "difficulty": course.get("difficulty", ""),
            "rating": course.get("rating", 0),
            "enrollment_count": course.get("enrollment_count", 0),
            "is_selected": str(course["_id"]) in user.get("selected_courses", []),
            #"status": user.get("course_progress", {}).get(str(course["_id"]), "进行中")
        }
        
        return course_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/search")
async def search_courses(q: str, page: int = 1, page_size: int = 9, current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        selected_courses = user["selected_courses"] if user and "selected_courses" in user else []
        
        # 构建搜索条件
        search_query = {
            "$or": [
                {"course_name": {"$regex": q, "$options": "i"}},
                #{"category": {"$regex": q, "$options": "i"}},
                #{"description": {"$regex": q, "$options": "i"}}
            ]
        }
        
        # 获取总数和分页数据
        total_courses = db.courses.count_documents(search_query)
        courses = list(db.courses.find(search_query).skip((page - 1) * page_size).limit(page_size))
        
        processed_courses = []
        for course in courses:
            processed_course = {
                "_id": str(course["_id"]),
                "course_name": course.get("course_name", ""),
                "course_url": course.get("course_url", ""),
                "course_logo_url": course.get("course_logo_url", ""),
                "category": course.get("category", ""),
                "difficulty": course.get("difficulty", ""),
                "description": course.get("description", ""),
                "rating": float(course.get("rating", 0)),
                "enrollment_count": course.get("enrollment_count", 0),
                "is_selected": course["_id"] in selected_courses
            }
            processed_courses.append(processed_course)
        
        return {
            "courses": processed_courses,
            "total": total_courses,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_courses + page_size - 1) // page_size
        }
    except Exception as e:
        return {
            "error": str(e),  # 返回错误信息用于调试
            "courses": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0
        }