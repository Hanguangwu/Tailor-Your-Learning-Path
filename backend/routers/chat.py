from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from pydantic import BaseModel
import os
from openai import OpenAI
from .auth import get_current_user

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

@router.post("")
async def chat(request: ChatRequest, current_user: str = Depends(get_current_user)):
    try:
        print(f"Received chat request: {request.dict()}")  # 调试日志
        
        response = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}],
            temperature=0.7,
            max_tokens=1000
        )
        
        print(f"API Response: {response}")  # 调试日志
        
        return {
            "response": response.choices[0].message.content
        }
    except Exception as e:
        print(f"Chat error: {str(e)}")  # 错误日志
        raise HTTPException(status_code=500, detail=f"聊天服务错误: {str(e)}")