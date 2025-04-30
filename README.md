# 局域网文件传输

一个基于FastAPI的局域网文件传输工具，使用美观的H5界面，实现电脑与移动设备间的便捷文件传输。

## 功能特点

- 简洁直观的用户界面
- 指定任意文件夹进行共享
- 拖放上传文件
- 文件类型识别与预览
- 实时上传进度显示
- 响应式设计，适配各种屏幕尺寸
- 文件管理（上传、下载、删除）

## 使用方法

### 安装依赖

```
pip install -r requirements.txt
```

### 运行应用

方式1：直接运行，使用默认存储路径(./storage)
```
python app.py
```

方式2：指定共享文件夹路径
```
python app.py --path "D:/Videos"
```

方式3：使用批处理文件(Windows系统)
```
双击运行 run.bat
```

### 命令行参数

- `--path`: 指定要共享的文件夹路径
- `--port`: 指定服务器端口(默认8000)

### 在移动设备上访问

1. 确保您的电脑和移动设备连接到同一个局域网
2. 运行应用，记下控制台显示的IP地址
3. 在移动设备的浏览器中访问 `http://[电脑IP]:8000`

## 自定义配置

默认情况下，文件将存储在应用目录下的`storage`文件夹中。如需更改存储位置，请修改`main.py`中的`STORAGE_PATH`变量。

```python
# 设置存储路径为特定位置
STORAGE_PATH = Path("D:/Videos")  # Windows示例
# 或
STORAGE_PATH = Path("/home/user/videos")  # Linux示例
```

## 技术栈

- 后端: FastAPI, Python
- 前端: HTML5, CSS3, JavaScript
- UI: 响应式设计, Font Awesome图标

## 安全注意事项

此应用设计用于私人局域网中使用，不建议将其暴露在公共网络上，因为它没有实现用户认证和数据加密功能。 