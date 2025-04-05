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
from .RecommendAlgo import RecommendAlgo

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
async def get_recommended_courses(
        page: int = 1,
        page_size: int = 6,
        current_user: str = Depends(get_current_user)
):
    try:
        # 获取当前用户信息
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")

        # 确保用户有已选课程
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

                # 使用ItemCF算法进行推荐
                algo = RecommendAlgo(course_user_matrix)
                recommendations = algo.item_cf(user_selected_courses)

                # 获取所有推荐课程ID
                all_recommended_ids = recommendations.index.tolist()
                total_recommended = len(all_recommended_ids)

                # 计算分页
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                page_recommended_ids = all_recommended_ids[start_idx:end_idx]

                recommended_courses = []
                user = db.users.find_one({"_id": ObjectId(current_user)})
                selected_courses = user.get("selected_courses", [])

                # 获取分页后的推荐课程详情
                for course_id in page_recommended_ids:
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
                            "is_selected": str(course["_id"]) in [str(c) for c in selected_courses]
                        }
                        recommended_courses.append(processed_course)

                return {
                    "courses": recommended_courses,
                    "total": total_recommended,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 9  # 固定返回9页，与精选课程保持一致
                    #"total_pages": (total_recommended + page_size - 1) // page_size
                }
    except Exception as e:
        print(f"推荐课程时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
        
        # 更新用户成就
        user = db.users.find_one({"_id": ObjectId(current_user)})
        selected_courses_count = len(user.get("selected_courses", []))
        
        # 获取现有的成就和积分
        user_badges = user.get("badges", [])
        user_points = user.get("points", 0)
        updates = {}
        
        # 首次选课成就
        if selected_courses_count == 1:
            updates["first_course_date"] = datetime.now()
            if not any(badge["badgeId"] == "first_course" for badge in user_badges):
                user_badges.append({
                    "badgeId": "first_course",
                    "earnedAt": datetime.now()
                })
                user_points += 10
        
        # 课程收藏家成就
        if selected_courses_count == 5:
            updates["bronze_collector_date"] = datetime.now()
            user_badges.append({
                "badgeId": "course_collector_bronze",
                "earnedAt": datetime.now()
            })
            user_points += 20
        elif selected_courses_count == 10:
            updates["silver_collector_date"] = datetime.now()
            user_badges.append({
                "badgeId": "course_collector_silver",
                "earnedAt": datetime.now()
            })
            user_points += 50
        elif selected_courses_count == 20:
            updates["gold_collector_date"] = datetime.now()
            user_badges.append({
                "badgeId": "course_collector_gold",
                "earnedAt": datetime.now()
            })
            user_points += 100
            
        # 更新用户成就和积分
        updates.update({
            "badges": user_badges,
            "points": user_points
        })
        
        db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$set": updates}
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
@router.get("/search")
async def search_courses(
    keyword: str,
    page: int = 1,
    page_size: int = 9,
    current_user: str = Depends(get_current_user)
):
    try:
        if not keyword:  # 添加参数验证
            raise HTTPException(status_code=400, detail="搜索关键词不能为空")
        user = db.users.find_one({"_id": ObjectId(current_user)})
        selected_courses = user.get("selected_courses", []) if user else []

        search_query = {
            "$or": [
                {"course_name": {"$regex": keyword, "$options": "i"}},
                #{"description": {"$regex": keyword, "$options": "i"}},
                #{"category": {"$regex": keyword, "$options": "i"}}
            ]
        }

        total_courses = db.courses.count_documents(search_query)
        courses = list(db.courses.find(search_query)
                      .skip((page - 1) * page_size)
                      .limit(page_size))

        processed_courses = []
        for course in courses:
            course_id = course["_id"]
            processed_course = {
                "_id": str(course_id),
                "course_name": course.get("course_name", ""),
                "description": course.get("description", ""),
                "course_logo_url": course.get("course_logo_url", ""),
                "category": course.get("category", ""),
                "difficulty": course.get("difficulty", ""),
                "course_url": course.get("course_url", ""),
                "rating": float(course.get("rating", 0)),
                "enrollment_count": course.get("enrollment_count", 0),
                "is_selected": str(course_id) in [str(c) for c in selected_courses]
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
        print(f"搜索错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories():
    """获取所有可用的课程类别"""
    try:
        # 从数据库中获取所有不同的类别
        categories = db.courses.distinct("category")
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms")
async def get_platforms():
    """获取所有可用的课程平台"""
    try:
        # 从数据库中获取所有不同的平台
        platforms = db.courses.distinct("platform")
        return {"platforms": platforms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/filter")
async def filter_courses(
    platform: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 9,
    current_user: str = Depends(get_current_user)
):
    try:
        # 获取用户信息和已选课程
        user = db.users.find_one({"_id": ObjectId(current_user)})
        selected_courses = user.get("selected_courses", []) if user else []

        # 构建查询条件
        filter_query = {}
        
        # 添加平台筛选
        if platform:
            filter_query["platform"] = platform
        
        # 添加类别筛选
        if category:
            filter_query["category"] = category
            
        # 添加关键词搜索
        if keyword:
            filter_query["$or"] = [
                {"course_name": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}}
            ]

        # 查询符合条件的课程总数
        total_courses = db.courses.count_documents(filter_query)
        
        # 分页查询课程
        courses = list(db.courses.find(filter_query)
                      .sort("rating", -1)  # 按评分降序排序
                      .skip((page - 1) * page_size)
                      .limit(page_size))

        # 处理课程数据
        processed_courses = []
        for course in courses:
            course_id = course["_id"]
            processed_course = {
                "_id": str(course_id),
                "course_name": course.get("course_name", ""),
                "description": course.get("description", ""),
                "course_logo_url": course.get("course_logo_url", ""),
                "category": course.get("category", ""),
                "difficulty": course.get("difficulty", ""),
                "course_url": course.get("course_url", ""),
                "platform": course.get("platform", ""),
                "rating": float(course.get("rating", 0)),
                "enrollment_count": course.get("enrollment_count", 0),
                "is_selected": str(course_id) in [str(c) for c in selected_courses]
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
        print(f"筛选课程错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
