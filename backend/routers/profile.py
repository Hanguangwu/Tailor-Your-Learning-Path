from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from pydantic import BaseModel
from typing import List, Optional
from database import db
from .auth import get_current_user, verify_password, get_password_hash

router = APIRouter()

# 数据模型定义
class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

class InterestUpdate(BaseModel):
    interest: str

# API路由
@router.get("/selected-courses")
async def get_selected_courses(current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        # 获取用户选择的课程ID列表
        selected_course_ids = [ObjectId(id) for id in user.get("selected_courses", [])]
        if not selected_course_ids:
            return {"courses": [], "total": 0}
        
        # 获取课程进度信息
        course_progress = user.get("course_progress", {})
            
        # 联合查询课程信息
        courses = list(db.courses.find({"_id": {"$in": selected_course_ids}}))
        processed_courses = []
        
        for course in courses:
            course_id = str(course["_id"])
            processed_course = {
                "_id": course_id,
                "course_name": course.get("course_name", ""),
                "description": course.get("description", ""),
                "course_url": course.get("course_url", ""),
                "course_logo_url": course.get("course_logo_url", ""),
                "category": course.get("category", ""),
                "difficulty": course.get("difficulty", ""),
                "rating": course.get("rating", 0),
                "enrollment_count": course.get("enrollment_count", 0),
                "status": course_progress.get(course_id, "进行中")
            }
            processed_courses.append(processed_course)
            
        return {
            "courses": processed_courses,
            "total": len(processed_courses)
        }
    except Exception as e:
        print(f"Error in get_selected_courses: {str(e)}")  # 添加调试日志
        raise HTTPException(status_code=500, detail=str(e))
"""
@router.get("/selected-courses")
async def get_selected_courses(current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        selected_course_ids = user.get("selected_courses", [])
        if not selected_course_ids:
            return {"courses": [], "total": 0}
            
        courses = list(db.courses.find({"_id": {"$in": selected_course_ids}}))
        processed_courses = []
        
        for course in courses:
            processed_course = {
                "_id": str(course["_id"]),
                "course_name": course.get("course_name", ""),
                "description": course.get("description", ""),
                "course_url": course.get("course_url", ""),
                "course_logo_url": course.get("course_logo_url", ""),
                "category": course.get("category", ""),
                "difficulty": course.get("difficulty", ""),
                "rating": course.get("rating", 0),
                "enrollment_count": course.get("enrollment_count", 0)
            }
            processed_courses.append(processed_course)
            
        return {
            "courses": processed_courses,
            "total": len(processed_courses)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""

@router.get("/interests")
async def get_interests(current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return {"interests": user.get("interests", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interests")
async def add_interest(interest_data: InterestUpdate, current_user: str = Depends(get_current_user)):
    try:
        result = db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$addToSet": {"interests": interest_data.interest}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="添加兴趣失败")
        return {"message": "兴趣添加成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/interests/{interest}")
async def remove_interest(interest: str, current_user: str = Depends(get_current_user)):
    try:
        result = db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$pull": {"interests": interest}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="删除兴趣失败")
        return {"message": "兴趣删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update")
async def update_profile(profile: ProfileUpdate, current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        update_data = {}
        
        # 更新用户名
        if profile.username and profile.username != user.get("username"):
            existing_user = db.users.find_one({
                "username": profile.username,
                "_id": {"$ne": ObjectId(current_user)}
            })
            if existing_user:
                raise HTTPException(status_code=400, detail="用户名已存在")
            update_data["username"] = profile.username

        # 更新密码
        if profile.new_password:
            if not profile.current_password:
                raise HTTPException(status_code=400, detail="需要提供当前密码")
            
            if not verify_password(profile.current_password, user["password"]):
                raise HTTPException(status_code=400, detail="当前密码错误")
            
            update_data["password"] = get_password_hash(profile.new_password)

        if update_data:
            result = db.users.update_one(
                {"_id": ObjectId(current_user)},
                {"$set": update_data}
            )
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="更新失败")

        return {"message": "个人信息更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-path")
async def get_learning_path(current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        user_interests = user.get("interests", [])
        selected_courses = user.get("selected_courses", [])

        # 根据用户兴趣和难度级别获取课程
        def get_courses_by_difficulty(difficulty: str, limit: int = 3):
            return list(db.courses.find({
                "category": {"$in": user_interests},
                "difficulty": difficulty
            }).limit(limit))

        # 处理课程数据
        def process_courses(courses):
            return [{
                "_id": str(course["_id"]),
                "course_name": course.get("course_name", ""),
                "description": course.get("description", ""),
                "course_url": course.get("course_url", ""),
                "difficulty": course.get("difficulty", ""),
                "is_selected": course["_id"] in selected_courses
            } for course in courses]

        # 获取不同难度的课程
        basic_courses = get_courses_by_difficulty("初级")
        intermediate_courses = get_courses_by_difficulty("中级")
        advanced_courses = get_courses_by_difficulty("高级")

        learning_path = [
            {
                "title": "基础阶段",
                "description": "掌握基础知识和概念",
                "courses": process_courses(basic_courses),
                "completed": all(course["_id"] in selected_courses for course in basic_courses)
            },
            {
                "title": "进阶阶段",
                "description": "深入学习核心技能",
                "courses": process_courses(intermediate_courses),
                "completed": all(course["_id"] in selected_courses for course in intermediate_courses)
            },
            {
                "title": "高级阶段",
                "description": "掌握高级特性和最佳实践",
                "courses": process_courses(advanced_courses),
                "completed": all(course["_id"] in selected_courses for course in advanced_courses)
            }
        ]

        return {"path": learning_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.put("/courses/{course_id}/status")
async def update_course_status(course_id: str, current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 更新课程状态
        course = db.courses.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 在用户的课程进度中更新状态
        current_status = user.get("course_progress", {}).get(course_id, "进行中")
        new_status = "已完成" if current_status == "进行中" else "进行中"

        result = db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$set": {f"course_progress.{course_id}": new_status}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="更新状态失败")

        return {"message": "课程状态更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/courses/{course_id}")
async def unselect_course(course_id: str, current_user: str = Depends(get_current_user)):
    try:
        # 先检查用户是否存在
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 检查课程是否存在
        course = db.courses.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 检查用户是否已选择该课程
        if str(course_id) not in user.get("selected_courses", []):
            raise HTTPException(status_code=400, detail="未选择该课程")

        # 更新用户的选课记录
        result = db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$pull": {"selected_courses": str(course_id)}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="退选失败")

        # 更新课程的选课人数
        db.courses.update_one(
            {"_id": ObjectId(course_id)},
            {"$inc": {"enrollment_count": -1}}
        )

        return {"message": "退选成功"}
    except Exception as e:
        print(f"退选课程错误: {str(e)}")  # 添加错误日志
        raise HTTPException(status_code=500, detail=str(e))
@router.get("")
async def get_user_profile(current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        return {
            "id": str(user["_id"]),
            "username": user.get("username", ""),
            "email": user.get("email", ""),
            "interests": user.get("interests", []),
            "selected_courses_count": len(user.get("selected_courses", [])),
            "completed_courses_count": len([
                k for k, v in user.get("course_progress", {}).items() 
                if v == "已完成"
            ])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))