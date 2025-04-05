from fastapi import APIRouter, HTTPException
from bson import ObjectId
from database import db

# 创建路由
router = APIRouter()

@router.get("/showAll")
async def get_all_websites():
    try:
        # 从数据库中查询所有网站数据
        websites = list(db.websites.find({}, {"_id": 1, "name": 1, "logoUrl": 1, "description": 1, "url": 1}))
        
        # 将 ObjectId 转换为字符串，以便 JSON 序列化
        for website in websites:
            website["_id"] = str(website["_id"])
            
        return websites
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取网站数据失败: {str(e)}")

@router.get("/category/{category}")
async def get_websites_by_category(category: str):
    try:
        # 从数据库中查询指定类别的网站数据
        websites = list(db.websites.find(
            {"category": category}, 
            {"_id": 1, "name": 1, "logoUrl": 1, "description": 1, "url": 1, "category": 1}
        ))
        
        # 将 ObjectId 转换为字符串，以便 JSON 序列化
        for website in websites:
            website["_id"] = str(website["_id"])
            
        return websites
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取{category}类别网站数据失败: {str(e)}")