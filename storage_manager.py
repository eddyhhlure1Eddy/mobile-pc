import os
import json
import shutil
import datetime
import mimetypes
from pathlib import Path

# Configuration file path
CONFIG_FILE = Path("config.json")

# Default configuration
DEFAULT_CONFIG = {
    "folder_path": str(Path("./storage").resolve())
}

class StorageManager:
    def __init__(self):
        self.config = self._load_config()
        self.storage_path = self._initialize_storage_path()
        
    def _load_config(self):
        """Load configuration file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load config file: {e}")
        return DEFAULT_CONFIG.copy()
    
    def _save_config(self):
        """Save configuration to file"""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def _initialize_storage_path(self):
        """Initialize storage path"""
        storage_path = Path(self.config["folder_path"])
        if not storage_path.exists():
            try:
                storage_path.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {storage_path}")
            except Exception as e:
                print(f"Cannot create directory {storage_path}: {e}")
                storage_path = Path("./storage").resolve()
                storage_path.mkdir(exist_ok=True)
                self.config["folder_path"] = str(storage_path)
                self._save_config()
        return storage_path
    
    def get_storage_path(self):
        """Get current storage path"""
        return self.storage_path
    
    def set_storage_path(self, folder_path):
        """Set storage path"""
        folder = Path(folder_path)
        
        if not folder.exists():
            try:
                folder.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {folder}")
            except Exception as e:
                raise Exception(f"Cannot create directory: {str(e)}")
        
        if not folder.is_dir():
            raise Exception("Specified path is not a directory")
        
        self.storage_path = folder
        self.config["folder_path"] = str(folder)
        self._save_config()
        
        return str(folder)
    
    def list_files(self):
        """List all files"""
        files = []
        
        try:
            for file_path in self.storage_path.glob("*"):
                if file_path.is_file():
                    stats = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "size": stats.st_size,
                        "size_formatted": self.format_size(stats.st_size),
                        "modified": datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "type": self.get_file_type(file_path.name)
                    })
            return sorted(files, key=lambda x: x["modified"], reverse=True)
        except Exception as e:
            print(f"Failed to read file list: {e}")
            return []
    
    def get_file_path(self, filename):
        """Get complete file path"""
        file_path = self.storage_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {filename}")
        return file_path
    
    def save_uploaded_file(self, file_obj, filename):
        """Save uploaded file"""
        file_path = self.storage_path / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return filename
    
    def delete_file(self, filename):
        """Delete file"""
        file_path = self.storage_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {filename}")
        os.remove(file_path)
        return True
    
    @staticmethod
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
    
    @staticmethod
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