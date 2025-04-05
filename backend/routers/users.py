from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from .auth import get_current_user, verify_password, get_password_hash
from database import db
from bson import ObjectId

router = APIRouter()

class UserProfileUpdate(BaseModel):
    # 基本信息
    username: Optional[str] = None
    currentPassword: Optional[str] = None
    newPassword: Optional[str] = None
    
    # 详细资料
    age: Optional[int] = None
    education: Optional[str] = None
    industry: Optional[str] = None
    jobTitle: Optional[str] = None
    careerPath: Optional[str] = None
    interests: Optional[List[str]] = None
    technicalSkills: Optional[List[str]] = None
    softSkills: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    learningGoals: Optional[List[str]] = None
    goalDescription: Optional[str] = None
    learningPreferences: Optional[List[str]] = None

# 统一的用户信息获取接口
@router.get("/profile")
async def get_user_profile(current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")
        
        # 创建完整的用户资料
        profile_data = {
            # 基本信息
            'id': str(user["_id"]),
            'username': user.get('username', ''),
            'email': user.get('email', ''),
            'selected_courses': [str(course_id) for course_id in user.get('selected_courses', [])],
            'points': user.get('points', 0),
            'badges': user.get('badges', []),
            
            # 详细资料
            'age': user.get('age'),
            'education': user.get('education', ''),
            'industry': user.get('industry', ''),
            'jobTitle': user.get('jobTitle', ''),
            'careerPath': user.get('careerPath', ''),
            'interests': user.get('interests', []),
            'technicalSkills': user.get('technicalSkills', []),
            'softSkills': user.get('softSkills', []),
            'tools': user.get('tools', []),
            'learningGoals': user.get('learningGoals', []),
            'goalDescription': user.get('goalDescription', ''),
            'learningPreferences': user.get('learningPreferences', []),
            'profile_completed': user.get('profile_completed', False)
        }
            
        return profile_data
    except Exception as e:
        print(f"获取用户资料错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 统一的用户信息更新接口
@router.post("/update-profile")
async def update_user_profile(profile_data: UserProfileUpdate, current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")

        # 构建更新数据
        update_data = {}
        
        # 处理基本信息更新
        if profile_data.username is not None:
            # 检查用户名是否已存在
            existing_user = db.users.find_one({"username": profile_data.username})
            if existing_user and str(existing_user["_id"]) != current_user:
                raise HTTPException(status_code=400, detail="用户名已存在")
            update_data["username"] = profile_data.username
        
        # 处理密码更新
        if profile_data.currentPassword and profile_data.newPassword:
            if not verify_password(profile_data.currentPassword, user["password"]):
                raise HTTPException(status_code=400, detail="当前密码错误")
            update_data["password"] = get_password_hash(profile_data.newPassword)
        
        # 处理详细资料更新
        for field in [
            "age", "education", "industry", "jobTitle", "careerPath", 
            "interests", "technicalSkills", "softSkills", "tools", 
            "learningGoals", "goalDescription", "learningPreferences"
        ]:
            value = getattr(profile_data, field, None)
            if value is not None:
                update_data[field] = value
        
        # 如果有详细资料更新，标记为已完成
        if any(field in update_data for field in [
            "age", "education", "industry", "jobTitle", "careerPath", 
            "interests", "technicalSkills", "softSkills", "tools", 
            "learningGoals", "goalDescription", "learningPreferences"
        ]):
            update_data["profile_completed"] = True

        # 更新数据库
        if update_data:
            result = db.users.update_one(
                {"_id": ObjectId(current_user)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0 and len(update_data) > 0:
                raise HTTPException(status_code=400, detail="更新失败")
        
        # 获取更新后的用户信息
        updated_user = db.users.find_one({"_id": ObjectId(current_user)})
        
        # 返回基本信息或完整信息
        return {
            "message": "个人资料更新成功",
            "username": updated_user.get("username", ""),
            "profile_completed": updated_user.get("profile_completed", False)
        }
        
    except Exception as e:
        print(f"更新用户资料错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))