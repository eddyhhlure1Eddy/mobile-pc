from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
from pathlib import Path
import datetime
import mimetypes
import socket
import webbrowser
import uvicorn
import json

# Create application
app = FastAPI(title="File Transfer Station")

# Configuration file path
CONFIG_FILE = Path("config.json")

# Default configuration
DEFAULT_CONFIG = {
    "folder_path": str(Path("./storage").resolve())
}

# Load configuration
def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load configuration file: {e}")
    return DEFAULT_CONFIG

# Save configuration
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# Get configuration
config = load_config()

# Get storage path
STORAGE_PATH = Path(config["folder_path"])
if not STORAGE_PATH.exists():
    try:
        STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {STORAGE_PATH}")
    except Exception as e:
        print(f"Cannot create directory {STORAGE_PATH}: {e}")
        STORAGE_PATH = Path("./storage").resolve()
        STORAGE_PATH.mkdir(exist_ok=True)
        config["folder_path"] = str(STORAGE_PATH)
        save_config(config)

# Set static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render homepage"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "folder_path": config["folder_path"]
    })

@app.post("/api/set-folder")
async def set_folder(folder_path: str = Form(...)):
    """Set shared folder path"""
    folder = Path(folder_path)
    
    if not folder.exists():
        try:
            folder.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {folder}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Cannot create directory: {str(e)}")
    
    if not folder.is_dir():
        raise HTTPException(status_code=400, detail="Specified path is not a directory")
    
    global STORAGE_PATH
    STORAGE_PATH = folder
    config["folder_path"] = str(folder)
    save_config(config)
    
    return {"success": True, "folder_path": str(folder)}

@app.get("/api/current-folder")
async def get_current_folder():
    """Get current shared folder path"""
    return {"folder_path": config["folder_path"]}

@app.get("/api/files")
async def list_files():
    """List all files"""
    files = []
    
    try:
        for file_path in STORAGE_PATH.glob("*"):
            if file_path.is_file():
                file_type = get_file_type(file_path.name)
                if file_type == "video":
                    stats = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "size": stats.st_size,
                        "size_formatted": format_size(stats.st_size),
                        "modified": datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "type": file_type
                    })
        return {"files": sorted(files, key=lambda x: x["modified"], reverse=True)}
    except Exception as e:
        print(f"Failed to read file list: {e}")
        return {"files": [], "error": str(e)}

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download file"""
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
    """Upload file"""
    try:
        file_path = STORAGE_PATH / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"success": True, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.delete("/api/delete/{filename}")
async def delete_file(filename: str):
    """Delete file"""
    file_path = STORAGE_PATH / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"success": True}

def format_size(size_bytes):
    """Format file size"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"

def get_file_type(filename):
    """Get file type"""
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

def get_ip():
    """Get local IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    ip = get_ip()
    port = 8000
    
    print(f"\nFile Transfer service started!")
    print(f"===========================================")
    print(f"Current shared folder: {STORAGE_PATH}")
    print(f"Access on computer: http://127.0.0.1:{port}")
    print(f"Access on mobile: http://{ip}:{port}")
    print(f"===========================================\n")
    
    # Open in browser automatically
    webbrowser.open(f"http://127.0.0.1:{port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 