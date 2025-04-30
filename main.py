from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
from pathlib import Path
import datetime
import mimetypes
import uvicorn

# 创建应用
app = FastAPI(title="文件传输")

# 设置存储路径
STORAGE_PATH = Path("./storage")
STORAGE_PATH.mkdir(exist_ok=True)

# 设置静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """渲染主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/files")
async def list_files():
    """列出所有文件"""
    files = []
    for file_path in STORAGE_PATH.glob("*"):
        if file_path.is_file():
            stats = file_path.stat()
            files.append({
                "name": file_path.name,
                "size": stats.st_size,
                "size_formatted": format_size(stats.st_size),
                "modified": datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "type": get_file_type(file_path.name)
            })
    return {"files": sorted(files, key=lambda x: x["modified"], reverse=True)}

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """下载文件"""
    file_path = STORAGE_PATH / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type=mimetypes.guess_type(filename)[0] or "application/octet-stream"
    )

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    try:
        file_path = STORAGE_PATH / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"success": True, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.delete("/api/delete/{filename}")
async def delete_file(filename: str):
    """删除文件"""
    file_path = STORAGE_PATH / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"success": True}

def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"

def get_file_type(filename):
    """获取文件类型"""
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    if extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv']:
        return "video"
    elif extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
        return "image"
    elif extension in ['mp3', 'wav', 'ogg', 'flac', 'm4a']:
        return "audio"
    elif extension in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']:
        return "document"
    else:
        return "other"

if __name__ == "__main__":
    print(f"启动服务器，请在手机浏览器中访问: http://[电脑IP]:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) 