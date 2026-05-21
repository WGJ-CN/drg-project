from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import group

app = FastAPI(
    title="DRG 分组服务",
    description="DRG 疾病诊断相关分组工具",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改成具体前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(group.router, prefix="/api", tags=["分组"])

@app.get("/")
async def root():
    return {"message": "DRG 分组服务已启动", "status": "running"}