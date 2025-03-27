from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
from .auth import get_current_user
from database import db
import os
from openai import OpenAI

router = APIRouter()

# 定义请求模型
class ChatRequest(BaseModel):
    message: str
    model: str

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("CHATANYWHERE_API_KEY"),
    base_url=f"{os.getenv('CHATANYWHERE_URL')}/v1"
)

class ChatRecord(BaseModel):
    prompt: str
    model: str
    response: str
    response_time: datetime

@router.post("/sendMessage")
async def chat(request: ChatRequest, current_user: str = Depends(get_current_user)):
    try:
        # 获取当前用户信息
        user = db.users.find_one({"_id": ObjectId(current_user)})
        if not user:
            raise HTTPException(status_code=404, detail="用户未找到")
        print(f"Received chat request: {request.dict()}")  # 调试日志
        
        response = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}],
            temperature=0.7,
            max_tokens=1000
        )
        #print("response:", response)
        
        response_text = response.choices[0].message.content
        response_time = datetime.now()

        print(f"API Response: {response_text}")  # 调试日志

        # 存储聊天记录
        chat_record = ChatRecord(
            prompt=request.message,
            model=request.model,
            response=response_text,
            response_time=response_time
        )
        #print("chat_record:", chat_record)
        db.chats.insert_one(chat_record.dict())  # 去掉 await

        return {"response": response_text, "response_time": response_time}
    except Exception as e:
        print(f"Chat error: {str(e)}")  # 错误日志
        raise HTTPException(status_code=500, detail=f"聊天服务错误: {str(e)}")