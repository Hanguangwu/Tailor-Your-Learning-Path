from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from typing import Dict
from pydantic import BaseModel
from .auth import get_current_user
from database import db

router = APIRouter()

class CommentCreate(BaseModel):
    content: str

@router.post("/{course_id}")
async def create_comment(course_id: str, comment: CommentCreate, current_user: str = Depends(get_current_user)):
    try:
        # 验证课程是否存在
        course = db.courses.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        comment_data = {
            "user_id": current_user,
            "course_id": course_id,
            "content": comment.content,
            "created_at": datetime.utcnow(),
            "likes": 0,
            "dislikes": 0,
            "liked_by": [],
            "disliked_by": []
        }
        
        result = db.comments.insert_one(comment_data)
        return {"id": str(result.inserted_id), "message": "评论发表成功"}
    except Exception as e:
        print(f"Create comment error: {str(e)}")  # 添加错误日志
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{course_id}")
async def get_comments(course_id: str):
    try:
        comments = list(db.comments.find({"course_id": course_id}).sort("created_at", -1))
        for comment in comments:
            comment["_id"] = str(comment["_id"])
            user = db.users.find_one({"_id": ObjectId(comment["user_id"])})
            # 如果用户不存在，使用默认值"未知用户"
            if user is None:
                comment["username"] = "未知用户"
            else:
                comment["username"] = user["username"] if "username" in user else "未知用户"
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{comment_id}/like")
async def like_comment(comment_id: str, current_user: str = Depends(get_current_user)):
    try:
        comment = db.comments.find_one({"_id": ObjectId(comment_id)})
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")

        if current_user in comment["disliked_by"]:
            # 如果用户之前踩过，移除踩
            db.comments.update_one(
                {"_id": ObjectId(comment_id)},
                {
                    "$pull": {"disliked_by": current_user},
                    "$inc": {"dislikes": -1}
                }
            )

        if current_user not in comment["liked_by"]:
            # 添加点赞
            db.comments.update_one(
                {"_id": ObjectId(comment_id)},
                {
                    "$push": {"liked_by": current_user},
                    "$inc": {"likes": 1}
                }
            )
            return {"message": "点赞成功"}
        else:
            # 取消点赞
            db.comments.update_one(
                {"_id": ObjectId(comment_id)},
                {
                    "$pull": {"liked_by": current_user},
                    "$inc": {"likes": -1}
                }
            )
            return {"message": "取消点赞"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{comment_id}/dislike")
async def dislike_comment(comment_id: str, current_user: str = Depends(get_current_user)):
    try:
        comment = db.comments.find_one({"_id": ObjectId(comment_id)})
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")

        if current_user in comment["liked_by"]:
            # 如果用户之前点赞过，移除点赞
            db.comments.update_one(
                {"_id": ObjectId(comment_id)},
                {
                    "$pull": {"liked_by": current_user},
                    "$inc": {"likes": -1}
                }
            )

        if current_user not in comment["disliked_by"]:
            # 添加踩
            db.comments.update_one(
                {"_id": ObjectId(comment_id)},
                {
                    "$push": {"disliked_by": current_user},
                    "$inc": {"dislikes": 1}
                }
            )
            return {"message": "踩成功"}
        else:
            # 取消踩
            db.comments.update_one(
                {"_id": ObjectId(comment_id)},
                {
                    "$pull": {"disliked_by": current_user},
                    "$inc": {"dislikes": -1}
                }
            )
            return {"message": "取消踩"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))