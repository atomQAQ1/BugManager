import os
from datetime import datetime
from flask import current_app

class FileModel:
    @staticmethod
    def get_files():
        files = []
        # 使用当前配置的文件夹
        current_folder = current_app.config['CURRENT_FOLDER']
        folder_path = current_app.config[f'{current_folder.upper()}_FOLDER']
        
        for filename in os.listdir(folder_path):
            path = os.path.join(folder_path, filename)
            if os.path.isfile(path):
                stat = os.stat(path)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'upload_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                })
        return sorted(files, key=lambda x: x['upload_time'], reverse=True)

    @staticmethod
    def delete_file(filename):
        download_folder = current_app.config['DOWNLOADS_FOLDER']
        filepath = os.path.join(download_folder, filename)
        os.remove(filepath)

    @staticmethod
    def save_file(file):
        upload_folder = current_app.config['UPLOADS_FOLDER']
        filename = f"{file.filename}"
        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)
        return filename, os.path.getsize(save_path)