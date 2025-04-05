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
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import random
import string
import sys
sys.path.append("..")
from utils.email import generate_verification_code, send_reset_password_email
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

# 确保 reset_codes 集合存在
try:
    # 检查集合是否存在
    collections = db.list_collection_names()
    if "reset_codes" not in collections:
        # 创建 reset_codes 集合
        db.create_collection("reset_codes")
        # 创建过期索引，使验证码在过期时间后自动删除
        db.reset_codes.create_index([("expires_at", 1)], expireAfterSeconds=0)
        print("已创建 reset_codes 集合和过期索引")
except Exception as e:
    print(f"创建 reset_codes 集合时出错: {e}")
    # 创建一个内存存储作为备用
    verification_codes = {}

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

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class SendCodeRequest(BaseModel):
    email: EmailStr
    type: str

# 添加验证码验证模型
class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str
    type: str

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
        "points": 0,            # 积分
        "badges": [],           # 成就
        "profile_completed": False,  # 个人资料完善状态
        "comments_count": 0,    # 评论数
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
    if not user:
        raise HTTPException(
            status_code=401,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token({"sub": str(user["_id"])})
    
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

@router.post("/send-code")
async def send_verification_code(request: SendCodeRequest, background_tasks: BackgroundTasks):
    """发送验证码"""
    try:
        # 验证邮箱是否存在（针对重置密码）
        if request.type == "reset_password":
            user = db.users.find_one({"email": request.email})
            if user == None:
                raise HTTPException(status_code=404, detail="该邮箱未注册")
        
        # 生成验证码
        code = generate_verification_code()
        
        # 存储验证码并设置10分钟过期时间
        try:
            db.reset_codes.insert_one({
                "email": request.email,
                "code": code,
                "type": request.type,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=10)
            })
        except Exception as db_error:
            print(f"存储验证码到数据库失败: {db_error}")
            # 使用内存存储作为备用
            if 'verification_codes' not in globals():
                global verification_codes
                verification_codes = {}
            
            verification_codes[request.email] = {
                "code": code,
                "type": request.type,
                "expires_at": datetime.utcnow() + timedelta(minutes=10)
            }
            print(f"验证码已存储在内存中: {verification_codes}")
        
        # 在后台任务中发送邮件
        def send_email_task():
            try:
                success = send_reset_password_email(request.email, code)
                if not success:
                    print(f"发送邮件到 {request.email} 失败")
            except Exception as e:
                print(f"发送邮件异常: {e}")
        
        background_tasks.add_task(send_email_task)
        
        return {"message": "验证码已发送"}
    except Exception as e:
        print(f"发送验证码异常: {e}")
        raise HTTPException(status_code=500, detail=f"发送验证码失败: {str(e)}")

@router.post("/forgot-password")
async def forgot_password(request: ResetPasswordRequest, background_tasks: BackgroundTasks):
    """发送重置密码验证码（保留原有接口兼容性）"""
    try:
        # 验证邮箱是否存在
        user = db.users.find_one({"email": request.email})
        if not user:
            raise HTTPException(status_code=404, detail="该邮箱未注册")
        
        # 生成验证码
        code = generate_verification_code()
        print("生成的验证码:", code)
        
        # 存储验证码并设置10分钟过期时间
        try:
            db.reset_codes.insert_one({
                "email": request.email,
                "code": code,
                "type": "reset_password",
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=10)
            })
        except Exception as db_error:
            print(f"存储验证码到数据库失败: {db_error}")
            # 使用内存存储作为备用
            if 'verification_codes' not in globals():
                global verification_codes
                verification_codes = {}
            
            verification_codes[request.email] = {
                "code": code,
                "type": "reset_password",
                "expires_at": datetime.utcnow() + timedelta(minutes=10)
            }
            print(f"验证码已存储在内存中: {verification_codes}")
        
        # 在后台任务中发送邮件
        def send_email_task():
            try:
                success = send_reset_password_email(request.email, code)
                if not success:
                    print(f"发送邮件到 {request.email} 失败")
            except Exception as e:
                print(f"发送邮件异常: {e}")
        
        background_tasks.add_task(send_email_task)
        
        return {"message": "重置密码邮件已发送"}
    except Exception as e:
        print(f"发送验证码异常: {e}")
        raise HTTPException(status_code=500, detail=f"发送重置密码邮件失败: {str(e)}")

@router.post("/reset-password")
async def reset_password(request: ResetPasswordConfirm):
    """重置密码"""
    try:
        # 首先尝试从数据库验证
        reset_record = None
        try:
            reset_record = db.reset_codes.find_one({
                "email": request.email,
                "code": request.code,
                "type": "reset_password",
                "expires_at": {"$gt": datetime.utcnow()}  # 确保验证码未过期
            })
        except Exception as db_error:
            print(f"从数据库验证验证码失败: {db_error}")
        
        # 如果数据库验证失败，尝试从内存验证
        valid_code = reset_record is not None
        if not valid_code and 'verification_codes' in globals():
            code_data = verification_codes.get(request.email)
            if (code_data and code_data["code"] == request.code and 
                code_data["type"] == "reset_password" and 
                code_data["expires_at"] > datetime.utcnow()):
                valid_code = True
                # 从内存中删除验证码
                del verification_codes[request.email]
        
        if not valid_code:
            raise HTTPException(status_code=400, detail="验证码无效或已过期")
        
        # 更新密码
        hashed_password = get_password_hash(request.new_password)
        result = db.users.update_one(
            {"email": request.email},
            {"$set": {"password": hashed_password}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 如果使用的是数据库验证码，删除它
        if reset_record:
            try:
                db.reset_codes.delete_one({"_id": reset_record["_id"]})
            except Exception as db_error:
                print(f"删除数据库验证码失败: {db_error}")
        
        return {"message": "密码重置成功"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"重置密码异常: {e}")
        raise HTTPException(status_code=500, detail=f"重置密码失败: {str(e)}")

@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest):
    """验证验证码"""
    try:
        # 首先尝试从数据库验证
        reset_record = None
        try:
            reset_record = db.reset_codes.find_one({
                "email": request.email,
                "code": request.code,
                "type": request.type,
                "expires_at": {"$gt": datetime.utcnow()}  # 确保验证码未过期
            })
        except Exception as db_error:
            print(f"从数据库验证验证码失败: {db_error}")
        
        # 如果数据库验证失败，尝试从内存验证
        valid_code = reset_record is not None
        if not valid_code and 'verification_codes' in globals():
            code_data = verification_codes.get(request.email)
            if (code_data and code_data["code"] == request.code and 
                code_data["type"] == request.type and 
                code_data["expires_at"] > datetime.utcnow()):
                valid_code = True
        
        if not valid_code:
            raise HTTPException(status_code=400, detail="验证码无效或已过期")
        
        # 验证成功，但不删除验证码，因为后续重置密码还需要验证
        return {"message": "验证码验证成功"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"验证验证码异常: {e}")
        raise HTTPException(status_code=500, detail=f"验证验证码失败: {str(e)}")