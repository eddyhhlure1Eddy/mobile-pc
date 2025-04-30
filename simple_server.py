from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import datetime
import socket
import webbrowser
from pathlib import Path

app = Flask(__name__)

# 设置存储路径
STORAGE_PATH = Path("./storage")
STORAGE_PATH.mkdir(exist_ok=True)

@app.route('/')
def index():
    return render_template('simple.html')

@app.route('/files')
def list_files():
    files = []
    for file_path in STORAGE_PATH.glob("*"):
        if file_path.is_file():
            stats = file_path.stat()
            file_size = stats.st_size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size/1024:.2f} KB"
            elif file_size < 1024 * 1024 * 1024:
                size_str = f"{file_size/(1024*1024):.2f} MB"
            else:
                size_str = f"{file_size/(1024*1024*1024):.2f} GB"
                
            files.append({
                "name": file_path.name,
                "size": stats.st_size,
                "size_formatted": size_str,
                "modified": datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })
    return jsonify({"files": sorted(files, key=lambda x: x["modified"], reverse=True)})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(STORAGE_PATH, file.filename)
    file.save(file_path)
    
    return jsonify({"success": True, "filename": file.filename})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(STORAGE_PATH, filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    file_path = os.path.join(STORAGE_PATH, filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    os.remove(file_path)
    return jsonify({"success": True})

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 连接到公共DNS服务器，这样不会实际发送数据
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    ip = get_ip()
    port = 5000
    print(f"\n文件传输服务已启动!")
    print(f"===========================================")
    print(f"在电脑上访问: http://localhost:{port}")
    print(f"在手机上访问: http://{ip}:{port}")
    print(f"===========================================\n")
    
    # 在浏览器中自动打开
    webbrowser.open(f"http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=False) 