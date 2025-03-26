from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from .auth import get_current_user
from database import db

router = APIRouter()

class DocumentModel(BaseModel):
    text: str
    createdAt: Optional[datetime] = None

@router.post("/save")
async def save_document(document: DocumentModel, current_user: str = Depends(get_current_user)):
    try:
        # 获取当前用户信息
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")
        
        # 添加用户ID和创建时间
        doc_data = document.model_dump()
        doc_data["userId"] = user.get("_id")
        
        if not doc_data.get("createdAt"):
            doc_data["createdAt"] = datetime.now()
        
        result = db.documents.insert_one(doc_data)
        
        # 返回保存的文档
        saved_doc = db.documents.find_one({"_id": result.inserted_id})
        if saved_doc:
            saved_doc["id"] = str(saved_doc["_id"])
            del saved_doc["_id"]
        
        return saved_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.get("/history")
# async def get_history(current_user: str = Depends(get_current_user)):
#     try:
#         # 获取当前用户信息
#         user = db.users.find_one({"_id": ObjectId(current_user)})
#         if not user:
#             raise HTTPException(status_code=404, detail="用户未找到")
        
#         # 获取当前用户的历史文档
#         documents = []
#         cursor = db.documents.find({"userId": user.get("_id")}).sort("createdAt", -1)
        
#         # 使用普通的for循环而不是async for
#         for doc in cursor:
#             doc_dict = dict(doc)
#             doc_dict["id"] = str(doc_dict["_id"])
#             del doc_dict["_id"]
#             documents.append(doc_dict)
            
#         return documents
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@router.get("/history")
async def get_history(current_user: str = Depends(get_current_user)):
    try:
        # 获取当前用户信息
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")
        
        # 获取当前用户的历史文档
        documents = []
        cursor = db.documents.find({"userId": user.get("_id")}).sort("createdAt", -1)
        
        # 使用普通的for循环而不是async for
        for doc in cursor:
            # 创建一个新的字典来存储处理后的文档
            doc_dict = {}
            for key, value in doc.items():
                # 将ObjectId转换为字符串
                if isinstance(value, ObjectId):
                    doc_dict[key] = str(value)
                else:
                    doc_dict[key] = value
            
            # 添加id字段并删除_id字段
            doc_dict["id"] = str(doc["_id"])
            if "_id" in doc_dict:
                del doc_dict["_id"]
                
            documents.append(doc_dict)
            
        return documents
    except Exception as e:
        print(f"获取历史文档错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: str = Depends(get_current_user)):
    try:
        # 获取当前用户信息
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")
            
        # 确保文档存在且属于当前用户
        document = db.documents.find_one({
            "_id": ObjectId(document_id),
            "userId": user.get("_id")
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在或无权删除")
            
        # 删除文档
        result = db.documents.delete_one({
            "_id": ObjectId(document_id),
            "userId": user.get("_id")
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="文档删除失败")
            
        return {"message": "文档删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))