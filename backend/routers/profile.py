from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from pydantic import BaseModel
from typing import List, Optional
from database import db
from .auth import get_current_user, verify_password, get_password_hash
from datetime import datetime

router = APIRouter()

# 数据模型定义
class UpdateProfileModel(BaseModel):
    username: Optional[str] = None
    currentPassword: Optional[str] = None
    newPassword: Optional[str] = None


class InterestModel(BaseModel):
    interest: str

# 成就模型
class Badge(BaseModel):
    badgeId: str
    earnedAt: str

class UserAchievements(BaseModel):
    points: int
    badges: List[Badge]

class LeaderboardUser(BaseModel):
    id: str
    username: str
    points: int
    badgeCount: int

# Todo模型
class Todo(BaseModel):
    content: str
    completed: bool = False

# 成就日记模型
class AchievementDiary(BaseModel):
    title: str
    content: str
    tags: List[str] = []

# API路由

@router.post("/profile")
async def update_profile(profile_data: UpdateProfileModel, current_user: str = Depends(get_current_user)):
    user = db.users.find_one({"_id": ObjectId(current_user)})
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    print("即将开始验证")
    # 验证当前密码
    if profile_data.currentPassword and not verify_password(profile_data.currentPassword, user['password']):
        raise HTTPException(status_code=400, detail="当前密码不正确")
    print("即将开始更新用户名")
    # 更新用户名
    if profile_data.username:
        db.users.update_one({"_id": ObjectId(current_user)}, {"$set": {"username": profile_data.username}})
    print("即将开始更新密码")
    # 更新密码
    if profile_data.newPassword:
        hashed_password = get_password_hash(profile_data.newPassword)
        db.users.update_one({"_id": ObjectId(current_user)}, {"$set": {"password": hashed_password}})

    return {"message": "个人信息更新成功"}


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
                "platform": course.get("platform", "其他")
            }
            processed_courses.append(processed_course)
            
        return {
            "courses": processed_courses,
            "total": len(processed_courses)
        }
    except Exception as e:
        print(f"Error in get_selected_courses: {str(e)}")  # 添加调试日志
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/interests")
async def get_interests(current_user: str = Depends(get_current_user)):
    user = db.users.find_one({"_id": ObjectId(current_user)})
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return {"interests": user.get("interests", [])}

@router.post("/interests")
async def add_interest(interest_data: InterestModel, current_user: str = Depends(get_current_user)):
    interest = interest_data.interest
    db.users.update_one(
        {"_id": ObjectId(current_user)},
        {"$addToSet": {"interests": interest}}
    )
    return {"interest": interest}
@router.delete("/interests/{interest}")
async def remove_interest(interest: str, current_user: str = Depends(get_current_user)):
    db.users.update_one(
        {"_id": ObjectId(current_user)},
        {"$pull": {"interests": interest}}
    )
    return {"message": "兴趣已删除"}

@router.get("/learning-pbl")
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

@router.get("/achievements")
async def get_user_achievements(current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 计算用户成就
        achievements = []
        points = 0

        # 检查课程相关成就
        selected_courses_count = len(user.get("selected_courses", []))
        
        # 初次选课成就
        if selected_courses_count >= 1:
            achievements.append({
                "badgeId": "first_course",
                "earnedAt": user.get("first_course_date", None)
            })
            points += 10

        # 课程收藏家成就
        if selected_courses_count >= 5:
            achievements.append({
                "badgeId": "course_collector_bronze",
                "earnedAt": user.get("bronze_collector_date", None)
            })
            points += 20

        if selected_courses_count >= 10:
            achievements.append({
                "badgeId": "course_collector_silver",
                "earnedAt": user.get("silver_collector_date", None)
            })
            points += 50

        if selected_courses_count >= 20:
            achievements.append({
                "badgeId": "course_collector_gold",
                "earnedAt": user.get("gold_collector_date", None)
            })
            points += 100

        # 个人资料完善成就
        if user.get("profile_completed", False):
            achievements.append({
                "badgeId": "profile_complete",
                "earnedAt": user.get("profile_complete_date", None)
            })
            points += 15

        # 评论相关成就 - 从comments表中获取评论数量
        comments_count = db.comments.count_documents({"user_id": current_user})
        
        # 保存评论数量到用户表中，方便其他地方使用
        db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$set": {"comments_count": comments_count}}
        )
        
        if comments_count >= 1:
            achievements.append({
                "badgeId": "first_comment",
                "earnedAt": user.get("first_comment_date", None)
            })
            points += 10

        if comments_count >= 10:
            achievements.append({
                "badgeId": "social_butterfly",
                "earnedAt": user.get("social_butterfly_date", None)
            })
            points += 30

        # 更新用户积分到数据库
        db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$set": {
                "points": points,
                "badges": achievements
            }}
        )

        return {
            "points": points,
            "badges": achievements
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard")
async def get_leaderboard():
    try:
        # 获取所有用户
        users = list(db.users.find({}, {
            "username": 1,
            "points": 1,
            "badges": 1
        }))

        leaderboard = []
        for user in users:
            # 使用数据库中已有的积分和成就数据
            user_points = user.get("points", 0)
            user_badges = user.get("badges", [])
            
            leaderboard.append({
                "_id": str(user["_id"]),
                "username": user.get("username", "未知用户"),
                "points": user_points,
                "badgeCount": len(user_badges)
            })

        # 先按积分降序排序，再按成就数量降序排序
        leaderboard.sort(key=lambda x: (x["points"], x["badgeCount"]), reverse=True)
        return leaderboard[:10]  # 返回前10名

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 成就检查和更新函数
@router.post("/check-achievements")
async def check_achievements(current_user: str = Depends(get_current_user)):
    try:
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")
        # 获取用户当前成就
        current_badges = []
        if user.get("badges"):
            current_badges = user.get("badges", [])
        
        current_badge_ids = {badge.get("badgeId") for badge in current_badges if "badgeId" in badge}
        new_badges = []
        total_points = 0
        
        # 获取用户选择的课程数量
        selected_courses_count = len(user.get("selected_courses", []))
        
        # 获取用户评论数量 - 从comments表中获取
        comments_count = db.comments.count_documents({"user_id": current_user})
        # 保存评论数量到用户表中，方便其他地方使用
        db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$set": {"comments_count": comments_count}}
        )
        
        # 检查是否完成个人资料
        profile_complete = user.get("profile_completed", False)
        # 检查是否使用过学习路径
        learning_path_used = user.get("learning_path_used", False)
        # 计算所有成就和积分
        
        # 初出茅庐
        if selected_courses_count >= 1:
            if "first_course" not in current_badge_ids:
                new_badges.append({
                    "badgeId": "first_course",
                    "earnedAt": datetime.now().isoformat()
                })
            total_points += 10
        
        # 课程收藏家 I
        if selected_courses_count >= 5:
            if "course_collector_bronze" not in current_badge_ids:
                new_badges.append({
                    "badgeId": "course_collector_bronze",
                    "earnedAt": datetime.now().isoformat()
                })
            total_points += 20
        
        # 课程收藏家 II
        if selected_courses_count >= 10:
            if "course_collector_silver" not in current_badge_ids:
                new_badges.append({
                    "badgeId": "course_collector_silver",
                    "earnedAt": datetime.now().isoformat()
                })
            total_points += 50
        
        # 课程收藏家 III
        if selected_courses_count >= 20:
            if "course_collector_gold" not in current_badge_ids:
                new_badges.append({
                    "badgeId": "course_collector_gold",
                    "earnedAt": datetime.now().isoformat()
                })
            total_points += 100
        
        # 完善档案
        if profile_complete:
            if "profile_complete" not in current_badge_ids:
                new_badges.append({
                    "badgeId": "profile_complete",
                    "earnedAt": datetime.now().isoformat()
                })
            total_points += 15
        
        # 规划未来
        if learning_path_used:
            if "learning_path" not in current_badge_ids:
                new_badges.append({
                    "badgeId": "learning_path",
                    "earnedAt": datetime.now().isoformat()
                })
            total_points += 25
        
        # 初次发声
        if comments_count >= 1:
            if "first_comment" not in current_badge_ids:
                new_badges.append({
                    "badgeId": "first_comment",
                    "earnedAt": datetime.now().isoformat()
                })
            total_points += 10
        
        # 社交达人
        if comments_count >= 10:
            if "social_butterfly" not in current_badge_ids:
                new_badges.append({
                    "badgeId": "social_butterfly",
                    "earnedAt": datetime.now().isoformat()
                })
            total_points += 30
        
        # 更新用户成就和积分
        updated_badges = current_badges + new_badges
        
        db.users.update_one(
            {"_id": ObjectId(current_user)},
            {"$set": {
                "points": total_points,
                "badges": updated_badges
            }}
        )
        
        return {
            "success": True,
            "new_badges": new_badges,
            "points_earned": total_points - user.get("points", 0),
            "total_points": total_points
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/todos")
async def get_todos(current_user: str = Depends(get_current_user)):
    try:
        todos = list(db.todos.find({"user_id": ObjectId(current_user)}).sort("createdAt", -1))
        for todo in todos:
            todo["_id"] = str(todo["_id"])
            todo["user_id"] = str(todo["user_id"])
        return todos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/todos")
async def create_todo(todo: Todo, current_user: str = Depends(get_current_user)):
    try:
        todo_dict = todo.dict()
        todo_dict["user_id"] = ObjectId(current_user)
        todo_dict["createdAt"] = datetime.utcnow()
        result = db.todos.insert_one(todo_dict)
        created_todo = db.todos.find_one({"_id": result.inserted_id})
        created_todo["_id"] = str(created_todo["_id"])
        created_todo["user_id"] = str(created_todo["user_id"])
        return created_todo
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/todos/{todo_id}")
async def update_todo(todo_id: str, todo: Todo, current_user: str = Depends(get_current_user)):
    try:
        # 确保待办事项存在且属于当前用户
        existing_todo = db.todos.find_one({
            "_id": ObjectId(todo_id),
            "user_id": ObjectId(current_user)
        })
        
        if not existing_todo:
            raise HTTPException(status_code=404, detail="待办事项不存在")
            
        # 更新待办事项
        db.todos.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": {
                "completed": todo.completed,
                "content": todo.content
            }}
        )
        
        return {"message": "更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str, current_user: str = Depends(get_current_user)):
    try:
        result = db.todos.delete_one({
            "_id": ObjectId(todo_id),
            "user_id": ObjectId(current_user)
        })
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="待办事项不存在")
        return {"message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/achievement-diaries")
async def get_achievement_diaries(current_user: str = Depends(get_current_user)):
    try:
        diaries = list(db.achievement_diaries.find(
            {"user_id": ObjectId(current_user)}
        ).sort("createdAt", -1))
        
        for diary in diaries:
            diary["_id"] = str(diary["_id"])
            diary["user_id"] = str(diary["user_id"])
        return diaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/achievement-diaries")
async def create_achievement_diary(
    diary: AchievementDiary,
    current_user: str = Depends(get_current_user)
):
    try:
        diary_dict = diary.dict()
        diary_dict["user_id"] = ObjectId(current_user)
        diary_dict["createdAt"] = datetime.utcnow()
        
        result = db.achievement_diaries.insert_one(diary_dict)
        created_diary = db.achievement_diaries.find_one({"_id": result.inserted_id})
        
        created_diary["_id"] = str(created_diary["_id"])
        created_diary["user_id"] = str(created_diary["user_id"])
        return created_diary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/achievement-diaries/{diary_id}")
async def delete_achievement_diary(
    diary_id: str,
    current_user: str = Depends(get_current_user)
):
    try:
        result = db.achievement_diaries.delete_one({
            "_id": ObjectId(diary_id),
            "user_id": ObjectId(current_user)
        })
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="成就日记不存在")
        return {"message": "删除成功"}
    except Exception as e:
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
            "selected_courses_count": len(user.get("selected_courses", []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))