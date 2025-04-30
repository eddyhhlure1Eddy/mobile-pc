document.addEventListener('DOMContentLoaded', () => {
  // 元素引用
  const fileList = document.getElementById('file-list');
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const progressBar = document.querySelector('.progress-bar-fill');
  const progressContainer = document.querySelector('.upload-progress');
  const folderForm = document.getElementById('folderForm');
  
  // 移动端上传按钮元素
  const mobileUploadBtn = document.getElementById('mobileUploadBtn');
  const mobileFileInput = document.getElementById('mobile-file-input');
  
  // 创建toast容器
  const toastContainer = document.createElement('div');
  toastContainer.className = 'toast-container';
  document.body.appendChild(toastContainer);
  
  // 处理文件夹设置表单提交
  folderForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(folderForm);
    const folderPath = formData.get('folder_path');
    
    try {
      const response = await fetch('/api/set-folder', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        showToast(`共享文件夹已设置为: ${data.folder_path}`, 'success');
        fetchFiles();
      } else {
        showToast(`设置文件夹失败: ${data.detail || '未知错误'}`, 'error');
      }
    } catch (error) {
      console.error('设置文件夹错误:', error);
      showToast('设置文件夹失败', 'error');
    }
  });
  
  // 移动端上传按钮点击事件
  mobileUploadBtn.addEventListener('click', () => {
    mobileFileInput.click();
  });
  
  // 移动端文件选择事件
  mobileFileInput.addEventListener('change', () => {
    if (mobileFileInput.files.length) {
      mobileUploadBtn.classList.add('active');
      uploadFiles(mobileFileInput.files);
    }
  });

  // 文件上传完成后移除动画效果
  function removeUploadAnimation() {
    mobileUploadBtn.classList.remove('active');
    mobileFileInput.value = '';
  }
  
  // 关闭预览模态框
  function closePreviewModal() {
    const previewModal = document.getElementById('previewModal');
    if (previewModal) {
      previewModal.style.display = 'none';
      const previewContent = document.getElementById('modalPreviewContent');
      if (previewContent) {
        previewContent.innerHTML = '';
      }
    }
  }
  
  // 添加关闭预览模态框事件
  const closeModalBtn = document.querySelector('.close-modal');
  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', closePreviewModal);
  }
  
  // 点击模态框背景关闭
  const previewModal = document.getElementById('previewModal');
  if (previewModal) {
    previewModal.addEventListener('click', (e) => {
      if (e.target === previewModal) {
        closePreviewModal();
      }
    });
  
    // 添加ESC键关闭模态框
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && previewModal.style.display === 'flex') {
        closePreviewModal();
      }
    });
  }
  
  // 获取文件列表
  fetchFiles();
  
  // 添加高亮效果，提示用户正在拖拽区域内
  document.addEventListener('dragenter', function() {
    dropzone.classList.add('highlight');
  });
  
  // 拖拽上传事件
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => {
      dropzone.classList.add('active');
    });
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => {
      dropzone.classList.remove('active');
      dropzone.classList.remove('highlight');
    });
  });
  
  // 全局拖放事件，无论拖放到页面哪里都能上传
  document.body.addEventListener('drop', handleDrop);
  dropzone.addEventListener('drop', handleDrop);
  dropzone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
      uploadFiles(fileInput.files);
    }
  });
  
  // 处理文件拖放
  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
      // 滚动到上传区域
      dropzone.scrollIntoView({ behavior: 'smooth' });
      uploadFiles(files);
    }
  }
  
  // 上传文件
  async function uploadFiles(files) {
    if (files.length === 0) return;
    
    // 显示进度条
    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';
    
    let successCount = 0;
    let errorCount = 0;
    let totalSize = 0;
    let uploadedSize = 0;
    
    // 计算总大小
    for (let i = 0; i < files.length; i++) {
      totalSize += files[i].size;
    }
    
    for (let i = 0; i < files.length; i++) {
      const formData = new FormData();
      formData.append('file', files[i]);
      
      try {
        const xhr = new XMLHttpRequest();
        
        xhr.open('POST', '/api/upload');
        
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            // 更新当前文件的进度
            const fileProgress = e.loaded / e.total;
            const fileContribution = (files[i].size / totalSize) * fileProgress;
            
            // 更新总进度
            uploadedSize = (i > 0 ? uploadedSize : 0) + (e.loaded * (files[i].size / totalSize));
            const totalProgress = (uploadedSize / totalSize) * 100;
            progressBar.style.width = `${totalProgress}%`;
          }
        });
        
        xhr.onload = function() {
          if (xhr.status === 200) {
            successCount++;
            
            // 如果是最后一个文件
            if (i === files.length - 1) {
              const message = files.length === 1 
                ? '文件上传成功' 
                : `成功上传 ${successCount} 个文件${errorCount > 0 ? `, ${errorCount} 个文件失败` : ''}`;
              
              showToast(message, 'success');
              fetchFiles();
              fileInput.value = '';
              removeUploadAnimation(); // 移除移动端上传按钮动画
              
              // 上传完成后隐藏进度条
              setTimeout(() => {
                progressContainer.style.display = 'none';
              }, 500);
            }
          } else {
            errorCount++;
            if (files.length === 1) {
              showToast('上传失败: ' + (xhr.response ? JSON.parse(xhr.response).detail : xhr.statusText), 'error');
              removeUploadAnimation(); // 出错时也移除移动端上传按钮动画
            }
          }
        };
        
        xhr.onerror = function() {
          errorCount++;
          if (files.length === 1) {
            showToast('上传出错', 'error');
            removeUploadAnimation(); // 出错时也移除移动端上传按钮动画
          }
        };
        
        xhr.send(formData);
      } catch (error) {
        errorCount++;
        if (files.length === 1) {
          showToast('上传错误: ' + error.message, 'error');
          removeUploadAnimation(); // 出错时也移除移动端上传按钮动画
        }
      }
    }
  }
  
  // 格式化文件大小
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  // 下载文件
  function downloadFile(filename) {
    window.location.href = `/api/download/${filename}`;
  }
  
  // 获取文件列表
  async function fetchFiles() {
    try {
      console.log('[Debug] 正在请求文件列表...');
      const response = await fetch('/api/files');
      console.log('[Debug] API响应状态:', response.status);
      
      const data = await response.json();
      console.log('[Debug] API返回数据:', data);
      
      // 检查数据结构
      if (typeof data === 'object') {
        console.log('[Debug] 数据类型:', Object.keys(data));
      }
      
      if (data.error) {
        showToast(`获取文件列表失败: ${data.error}`, 'error');
        renderFiles([]);
        return;
      }
      
      // 检查文件列表格式
      if (data.files) {
        console.log('[Debug] 找到文件列表，数量:', data.files.length);
        renderFiles(data.files);
      } else if (Array.isArray(data)) {
        // 可能API直接返回数组而不是对象
        console.log('[Debug] API直接返回文件数组，数量:', data.length);
        renderFiles(data);
      } else {
        console.error('[Debug] 未找到预期的文件列表格式');
        showToast('获取文件列表失败: 数据格式错误', 'error');
        renderFiles([]);
      }
    } catch (error) {
      console.error('获取文件列表失败:', error);
      showToast('获取文件列表失败: ' + error.message, 'error');
      renderFiles([]);
    }
  }
  
  // 渲染文件列表
  function renderFiles(files) {
    fileList.innerHTML = '';
    
    if (!files || files.length === 0) {
      fileList.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-file-upload"></i>
          <h3>暂无文件</h3>
          <p>在上方设置共享文件夹，或拖拽文件到此处上传</p>
        </div>
      `;
      return;
    }
    
    files.forEach(file => {
      const fileCard = document.createElement('div');
      fileCard.className = 'file-card';
      
      let previewHtml = '';
      
      // 根据文件类型生成不同的预览内容
      switch(file.type) {
        case 'image':
          previewHtml = `<div class="file-preview image">
                           <img src="/api/download/${file.name}" alt="${file.name}">
                         </div>`;
          break;
        
        case 'video':
          previewHtml = `<div class="file-preview video">
                           <i class="fas fa-play-circle"></i>
                           <video src="/api/download/${file.name}"></video>
                         </div>`;
          break;
        
        case 'audio':
          previewHtml = `<div class="file-preview audio">
                           <i class="fas fa-music"></i>
                         </div>`;
          break;
        
        default:
          const iconMap = {
            'document': '<i class="fas fa-file-alt"></i>',
            'other': '<i class="fas fa-file"></i>'
          };
          
          previewHtml = `<div class="file-preview ${file.type}">
                           ${iconMap[file.type] || iconMap.other}
                         </div>`;
      }
      
      const fileSizeStr = formatFileSize(file.size);
      fileCard.innerHTML = `
        ${previewHtml}
        <div class="file-info">
          <div class="file-name" title="${file.name}">${file.name}</div>
          <div class="file-meta">
            <span class="file-size">${fileSizeStr}</span>
            <span class="file-date">${new Date(file.lastModified).toLocaleDateString()}</span>
          </div>
          <div class="file-actions">
            <button class="download-btn" data-filename="${file.name}"><i class="fas fa-download"></i></button>
            <button class="delete-btn" data-filename="${file.name}"><i class="fas fa-trash"></i></button>
          </div>
        </div>
      `;
      
      fileList.appendChild(fileCard);
      
      // 添加下载按钮事件
      const downloadBtn = fileCard.querySelector('.download-btn');
      downloadBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        downloadFile(file.name);
      });
      
      // 添加删除按钮事件
      const deleteBtn = fileCard.querySelector('.delete-btn');
      deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteFile(file.name);
      });
      
      // 添加点击打开预览事件
      const filePreview = fileCard.querySelector('.file-preview');
      
      if (file.type === 'image' || file.type === 'video' || file.type === 'audio') {
        filePreview.addEventListener('click', () => {
          showFilePreview(file);
        });
      }
    });
  }
  
  // 显示预览模态框
  function showFilePreview(file) {
    let previewHtml = '';
    
    if (file.type === 'image') {
      previewHtml = `<div class="file-preview image">
                       <img src="/api/download/${file.name}" alt="${file.name}">
                     </div>`;
    } else if (file.type === 'video') {
      previewHtml = `<div class="video-container">
                       <video src="/api/download/${file.name}" controls autoplay></video>
                       <div class="file-title">${file.name}</div>
                     </div>`;
    } else if (file.type === 'audio') {
      previewHtml = `<div class="audio-container">
                       <div class="audio-icon"><i class="fas fa-music"></i></div>
                       <audio src="/api/download/${file.name}" controls autoplay></audio>
                       <div class="file-title">${file.name}</div>
                     </div>`;
    } else {
      const iconMap = {
        'document': '<i class="fas fa-file-alt"></i>',
        'other': '<i class="fas fa-file"></i>'
      };
      
      previewHtml = `<div class="file-preview ${file.type}">
                       ${iconMap[file.type] || iconMap.other}
                     </div>`;
      
      showToast('此文件类型不支持预览', 'error');
      return;
    }
    
    const previewContent = document.getElementById('modalPreviewContent');
    previewContent.innerHTML = previewHtml;
    
    const previewModal = document.getElementById('previewModal');
    previewModal.style.display = 'flex';
  }
  
  // 删除文件
  async function deleteFile(filename) {
    if (!confirm(`确定要删除 ${filename} 吗？`)) {
      return;
    }
    
    try {
      const response = await fetch(`/api/delete/${filename}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        showToast('文件已删除', 'success');
        fetchFiles();
      } else {
        showToast('删除失败', 'error');
      }
    } catch (error) {
      showToast('删除错误: ' + error.message, 'error');
    }
  }
  
  // 显示通知
  function showToast(message, type = 'success') {
    const iconClass = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="${iconClass}"></i> ${message}`;
    
    toastContainer.appendChild(toast);
    
    // 强制浏览器重绘
    void toast.offsetWidth;
    
    // 显示通知
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        toastContainer.removeChild(toast);
      }, 300);
    }, 3000);
  }

  function getFileType(fileName) {
    const extension = fileName.split('.').pop().toLowerCase();
    
    const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'];
    const videoExtensions = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'];
    const audioExtensions = ['mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac'];
    const documentExtensions = ['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx'];
    
    if (imageExtensions.includes(extension)) {
      return 'image';
    } else if (videoExtensions.includes(extension)) {
      return 'video';
    } else if (audioExtensions.includes(extension)) {
      return 'audio';
    } else if (documentExtensions.includes(extension)) {
      return 'document';
    } else {
      return 'other';
    }
  }
}); 