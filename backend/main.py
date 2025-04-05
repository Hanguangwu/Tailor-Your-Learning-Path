from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, users, profile, courses, chat, comments, documents, self_test, recommendations, websites
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取前端URL，如果未设置则允许所有来源（不推荐用于生产环境）
FRONTEND_URL = os.getenv("FRONTEND_URL")
allowed_origins = [FRONTEND_URL] if FRONTEND_URL else ["*"]

# 获取环境和端口
ENV = os.getenv("ENVIRONMENT", "production")
PORT = int(os.getenv("PORT", 3000))

app = FastAPI(
    title="CSDIY API",
    description="CSDIY学习平台API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(self_test.router, prefix="/api/self-test", tags=["self-test"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(websites.router, prefix="/api/websites", tags=["websites"])

@app.get("/")  
def read_root():  
    return {"message": "Hello, World!"}  

@app.head("/")  
def head_root():  
    return {"message": "Hello, World!"}  

if __name__ == "__main__":
    import uvicorn
    import signal
    import sys

    def signal_handler(sig, frame):
        print('正在优雅退出...')
        sys.exit(0)

    # 注册信号处理器，用于优雅关闭
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 开发环境使用reload=True，生产环境不使用
    is_dev = ENV.lower() == "development"
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=is_dev)