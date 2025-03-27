from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, profile, courses, chat, comments, documents, self_test

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许前端开发服务器的地址
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

if __name__ == "__main__":
    import uvicorn
    import signal
    import sys


    def signal_handler(sig, frame):
        print('Exiting gracefully...')
        sys.exit(0)


    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)