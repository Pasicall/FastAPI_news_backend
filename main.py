from fastapi import FastAPI
from routers import news,users,favorite
from fastapi.middleware.cors  import CORSMiddleware
from utils.exception_handlers import register_exception_handlers


app = FastAPI()

#注册异常处理器
register_exception_handlers(app)

#配置跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return{"message": "Hello World"}

# 挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
