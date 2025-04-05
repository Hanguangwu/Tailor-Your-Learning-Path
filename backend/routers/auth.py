from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List
from database import db
from datetime import datetime, timedelta
from bson import ObjectId
import os
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import BackgroundTasks
import random
import string

# 确保在文件开头加载环境变量
load_dotenv()

router = APIRouter()

# 配置密码加密和验证
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 获取环境变量，设置默认值
SECRET_KEY = os.getenv("SECRET_KEY", "1234567890987654321")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 数据模型定义
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    interests: List[str]

class LoginData(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# 密码处理函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 用户认证函数
def authenticate_user(email: str, password: str):
    user = db.users.find_one({"email": email})
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

# Token相关函数
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    return str(user["_id"])

# API路由
@router.post("/register")
async def register(user: UserCreate):
    # 检查邮箱是否已存在
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
    
    # 检查用户名是否已存在
    if db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="该用户名已被使用")
    
    # 创建用户文档
    user_doc = {
        "username": user.username,
        "email": user.email,
        "password": get_password_hash(user.password),
        "interests": user.interests,
        "selected_courses": [],
        "created_at": datetime.utcnow()
    }
    
    # 插入数据库
    result = db.users.insert_one(user_doc)
    
    return {
        "message": "注册成功",
        "id": str(result.inserted_id)
    }

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 使用邮箱登录
    user = authenticate_user(form_data.username, form_data.password)  # form_data.username 实际上是邮箱
    print("执行到auth.py中的login1")
    if not user:
        raise HTTPException(
            status_code=401,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token({"sub": str(user["_id"])})
    print("执行到auth.py中的login2")
    # 确保返回所有需要的用户数据
    user_data = {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "interests": user.get("interests", []),
        "selected_courses": [str(course_id) for course_id in user.get("selected_courses", [])]
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str

# 生成验证码
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

@router.post("/forgot-password")
async def forgot_password(request: ResetPasswordRequest, background_tasks: BackgroundTasks):
    user = db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="该邮箱未注册")
    
    code = generate_verification_code()
    # 存储验证码（实际项目中应该设置过期时间）
    db.reset_codes.insert_one({
        "email": request.email,
        "code": code,
        "created_at": datetime.utcnow()
    })
    
    # TODO: 发送邮件的具体实现
    return {"message": "重置密码邮件已发送"}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordConfirm):
    # 验证码验证
    reset_record = db.reset_codes.find_one({
        "email": request.email,
        "code": request.code
    })
    
    if not reset_record:
        raise HTTPException(status_code=400, detail="验证码无效")
    
    # 更新密码
    hashed_password = get_password_hash(request.new_password)
    db.users.update_one(
        {"email": request.email},
        {"$set": {"password": hashed_password}}
    )
    
    # 删除验证码
    db.reset_codes.delete_one({"_id": reset_record["_id"]})
    
    return {"message": "密码重置成功"}