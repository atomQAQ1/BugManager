from flask import Blueprint, send_from_directory, request, jsonify, current_app
from models.file_model import FileModel
from utils.file_utils import allowed_file
from utils.excel_process_init import is_in_white_list
files_bp = Blueprint('files', __name__)
#下载文件
@files_bp.route('/downloads/<filename>')
def download_file(filename):
    try:
        return send_from_directory(
            current_app.config['DOWNLOADS_FOLDER'],
            filename,
            as_attachment=True
        )
    except FileNotFoundError:
        return jsonify({'error': '文件不存在'}), 404
#上传文件到服务器
@files_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '未选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '无效文件名'}), 400
    
    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify({'error': '文件类型不允许'}), 400

    try:
        filename, size = FileModel.save_file(file)
        return jsonify({
            'success': True,
            'filename': filename,
            'size': size
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# 删除文件
@files_bp.route('/delete_file/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        FileModel.delete_file(filename)
        return jsonify({'success': True})
    except FileNotFoundError:
        return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# 分离白名单
@files_bp.route('/whetherInWhite',methods=['GET'])
def whetherInWhite():
    try:
        is_in_white_list()
        return jsonify({
            'success': True,
            'message': '白名单分离完成'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@files_bp.route('/switchFileList', methods=['GET'])
def switch_file_list():
    try:
        # 切换当前配置的文件夹
        if current_app.config['CURRENT_FOLDER'] == 'downloads':
            current_app.config['CURRENT_FOLDER'] = 'uploads'
        else:
            current_app.config['CURRENT_FOLDER'] = 'downloads'
            
        return jsonify({
            'success': True,
            'message': f'已切换到 {current_app.config["CURRENT_FOLDER"]} 文件夹'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500