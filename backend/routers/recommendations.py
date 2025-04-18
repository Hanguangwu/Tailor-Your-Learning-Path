from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional
from .auth import get_current_user
from database import db
from bson import ObjectId
import os
from dotenv import load_dotenv
import sys
import json
from datetime import datetime
# 添加utils目录到路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "utils"))

# 导入RAG推荐器
from utils.rag_recommender import recommend_courses

# 加载环境变量
load_dotenv()

router = APIRouter()

class RecommendationRequest(BaseModel):
    count: int = 5  # 默认推荐5门课程

class CourseRecommendation(BaseModel):
    course_id: str
    title: str
    description: str
    reason: str

@router.post("/learning-path", response_model=List[CourseRecommendation])
async def recommend_learning_path(
    request: RecommendationRequest = Body(...),
    current_user: str = Depends(get_current_user)
):
    try:
        # 获取用户信息
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")
        
        # 准备用户信息
        user_info = {
            "username": user.get("username", ""),
            "age": user.get("age"),
            "education": user.get("education", ""),
            "industry": user.get("industry", ""),
            "jobTitle": user.get("jobTitle", ""),
            "careerPath": user.get("careerPath", ""),
            "interests": user.get("interests", []),
            "technicalSkills": user.get("technicalSkills", []),
            "softSkills": user.get("softSkills", []),
            "tools": user.get("tools", []),
            "learningGoals": user.get("learningGoals", []),
            "goalDescription": user.get("goalDescription", ""),
            "learningPreferences": user.get("learningPreferences", [])
        }
        
        # 使用RAG推荐器获取推荐
        recommendations = recommend_courses(user_info, count=request.count)
        
        # 验证推荐结果
        validated_recommendations = []
        for rec in recommendations:
            # 添加到验证后的推荐列表
            validated_recommendations.append(CourseRecommendation(
                course_id=rec["course_id"],
                title=rec["title"],
                description=rec.get("description", ""),
                reason=rec["reason"]
            ))
        
        # 更新用户的learning_path_used属性为True
        db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$set": {"learning_path_used": True}}
        )
        
        # 如果是第一次使用学习路径，记录日期
        if not user.get("learning_path_used", False):
            db.users.update_one(
                {"_id": ObjectId(current_user)},
                {"$set": {"learning_path_date": datetime.now().isoformat()}}
            )
        
        return validated_recommendations
        
    except Exception as e:
        print(f"推荐学习路径错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"推荐学习路径失败: {str(e)}")