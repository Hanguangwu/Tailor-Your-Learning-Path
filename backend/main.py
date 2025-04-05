from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, profile, courses, chat, comments, documents, self_test
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # 允许前端开发服务器的地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(self_test.router, prefix="/api/self-test", tags=["self-test"])

@app.get("/")  
def read_root():  
    return {"message": "Hello, World!"}  

# 如果需要支持 HEAD 请求，可以这样定义  
@app.head("/")  
def head_root():  
    return { "message": "Hello, World!" }  

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000)