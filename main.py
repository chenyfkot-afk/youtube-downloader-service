import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from supabase import create_client, Client

# 简化版下载服务配置
app = FastAPI(title="YouTube视频下载服务", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase配置
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://djjxxszmtxegownxwzgl.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

# 初始化Supabase客户端
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    supabase = None

class DownloadRequest(BaseModel):
    task_id: str
    video_url: str
    quality: str = "1080p"
    format: str = "mp4"
    download_type: str = "video"
    include_subtitles: bool = False

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "YouTube下载服务",
        "version": "1.0.0",
        "supabase_connected": supabase is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """服务信息"""
    return {
        "service": "YouTube视频下载服务",
        "version": "1.0.0",
        "status": "running",
        "supabase_connected": supabase is not None,
        "endpoints": {
            "/health": "GET - 健康检查",
            "/download": "POST - 创建下载任务"
        }
    }

@app.post("/download")
async def create_download(request: DownloadRequest):
    """创建下载任务"""
    try:
        print(f"📥 收到下载请求: {request.task_id}")
        print(f"🎥 视频URL: {request.video_url}")
        print(f"🎯 质量: {request.quality}, 格式: {request.format}")
        
        # 如果Supabase连接正常，更新任务状态
        if supabase:
            try:
                supabase.table('download_tasks').update({
                    'status': 'processing',
                    'updated_at': datetime.now().isoformat()
                }).eq('id', request.task_id).execute()
            except Exception as e:
                print(f"⚠️ 更新任务状态失败: {e}")
        
        # 模拟下载处理
        import time
        time.sleep(2)  # 模拟下载时间
        
        # 模拟下载结果
        mock_file_url = f"https://storage.googleapis.com/youtube-downloads/{request.task_id}.mp4"
        
        # 如果Supabase连接正常，更新完成状态
        if supabase:
            try:
                supabase.table('download_tasks').update({
                    'status': 'completed',
                    'progress': 100,
                    'file_url': mock_file_url,
                    'completed_at': datetime.now().isoformat()
                }).eq('id', request.task_id).execute()
            except Exception as e:
                print(f"⚠️ 更新完成状态失败: {e}")
        
        print(f"✅ 下载任务完成: {request.task_id}")
        
        return {
            "success": True,
            "message": "下载任务创建成功",
            "task_id": request.task_id,
            "status": "completed",
            "file_url": mock_file_url,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        
        # 如果Supabase连接正常，更新失败状态
        if supabase:
            try:
                supabase.table('download_tasks').update({
                    'status': 'failed',
                    'error_message': str(e),
                    'updated_at': datetime.now().isoformat()
                }).eq('id', request.task_id).execute()
            except Exception as e:
                print(f"⚠️ 更新失败状态失败: {e}")
        
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print("=" * 50)
    print("🎬 YouTube视频下载服务启动中...")
    print("=" * 50)
    print(f"🌐 服务地址: http://{host}:{port}")
    print(f"🔗 健康检查: http://{host}:{port}/health")
    print(f"🔗 Supabase URL: {SUPABASE_URL}")
    print(f"🔗 Supabase连接: {'✅ 正常' if supabase else '❌ 失败'}")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        exit(1)
