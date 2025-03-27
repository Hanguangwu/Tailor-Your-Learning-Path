from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from .auth import get_current_user
import random
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# 配置OpenAI API
# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("CHATANYWHERE_API_KEY"),
    base_url=f"{os.getenv('CHATANYWHERE_URL')}/v1"
)

class QuestionRequest(BaseModel):
    content: str
    count: int = 5

class Option(BaseModel):
    text: str
    is_correct: bool

class Question(BaseModel):
    question: str
    options: List[str]
    correctIndex: int
    explanation: str

@router.post("/generate", response_model=List[Question])
async def generate_questions(request: QuestionRequest, current_user: str = Depends(get_current_user)):
    try:
        # 检查内容长度
        if len(request.content) < 50:
            raise HTTPException(status_code=400, detail="内容太短，无法生成有效的测试题")
        
        # 限制题目数量
        count = min(request.count, 10)
        
        # 调用OpenAI API生成测试题
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的教育测试题生成器。请根据提供的内容生成单选题，每个题目有4个选项，只有一个正确答案。"},
                {"role": "user", "content": f"请根据以下内容生成{count}道单选题，每题4个选项，只有1个正确答案。同时提供每题的解析。\n\n内容：{request.content}\n\n请按以下JSON格式返回：\n[{{'question': '问题', 'options': ['选项A', '选项B', '选项C', '选项D'], 'correctIndex': 0, 'explanation': '解析'}}]"}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # 解析返回的内容
        content = response.choices[0].message.content
        
        # 尝试提取JSON部分
        import json
        import re
        
        # 查找JSON数组
        json_match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            questions_data = json.loads(json_str)
        else:
            # 如果没有找到JSON数组，尝试解析整个内容
            questions_data = json.loads(content)
        
        # 验证和处理问题数据
        questions = []
        for q_data in questions_data:
            # 确保有4个选项
            if len(q_data.get("options", [])) != 4:
                continue
                
            # 确保correctIndex在有效范围内
            correct_index = q_data.get("correctIndex")
            if not isinstance(correct_index, int) or correct_index < 0 or correct_index > 3:
                continue
                
            questions.append(Question(
                question=q_data.get("question", ""),
                options=q_data.get("options", []),
                correctIndex=correct_index,
                explanation=q_data.get("explanation", "")
            ))
        
        # 如果没有有效问题，抛出异常
        if not questions:
            raise HTTPException(status_code=500, detail="无法生成有效的测试题，请尝试提供更详细的内容")
            
        return questions
        
    except Exception as e:
        print(f"生成测试题错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成测试题失败: {str(e)}")