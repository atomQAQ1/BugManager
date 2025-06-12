import { showAlert, showModal } from './utils.js';

// 初始化文件上传功能
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const fileNameSpan = document.getElementById('fileName');
    
    fileInput.addEventListener('change', function(e) {
        const fileName = this.files[0]?.name || '未选择文件';
        fileNameSpan.textContent = fileName;
        
        clearTimeout(this.uploadTimer);
        this.uploadTimer = setTimeout(() => {
            if(this.files[0]) uploadFile();
        }, 500);
    });
});

const FileManager = {
    upload: async function() {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        const progress = document.querySelector('.progress');
        const progressBar = document.querySelector('.progress-bar');

        if (!file) {
            showAlert('请先选择文件', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            progress.style.display = 'block';
            const xhr = new XMLHttpRequest();

            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    progressBar.style.width = percent + '%';
                }
            };

            xhr.open('POST', '/upload');
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

            xhr.onload = function() {
                const response = JSON.parse(xhr.responseText);
                if (xhr.status === 200) {
                    showAlert('文件上传成功');
                    location.reload(); 
                } else {
                    showAlert(response.error || '上传失败', 'error');
                }
                progress.style.display = 'none';
                progressBar.style.width = '0%';
                fileInput.value = '';
                document.getElementById('fileName').textContent = '';
            };

            xhr.send(formData);
        } catch (error) {
            showAlert(error.message, 'error');
            progress.style.display = 'none';
        }
    },

    download: function(filename) {
        const link = document.createElement('a');
        link.href = `/downloads/${encodeURIComponent(filename)}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    },

    delete: async function(filename, event) {
        event.preventDefault();
        if (!confirm(`确定要删除 ${filename} 吗？`)) return;
        
        try {
            const response = await fetch(`/delete_file/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            if (data.success) {
                showAlert('文件删除成功');
                location.reload();
            } else {
                showAlert(data.error || '删除失败', 'error');
            }
        } catch (error) {
            showAlert('请求失败: ' + error.message, 'error');
        }
    }
};

// 导出接口
window.uploadFile = FileManager.upload;
window.downloadFile = FileManager.download;
window.deleteFile = FileManager.delete;

// 文件操作函数
function switchFileList() {
    fetch('/switchFileList', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showAlert(data.error || '切换失败', 'error');
        }
    })
    .catch(error => showAlert('请求失败: ' + error.message, 'error'));
}

function whetherInWhite(){
    fetch('/whetherInWhite', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showModal('白名单检查完成，请下载结果文件');
            setTimeout(() => location.reload(), 10000);
        } else {
            showModal(data.error || '处理失败', 'error');
        }
    });
}

window.switchFileList = switchFileList;
window.whetherInWhite = whetherInWhite;