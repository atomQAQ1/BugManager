from flask import Blueprint, render_template
from models.file_model import FileModel
from models.data_model import DataModel
from config import Config
from flask import jsonify
from flask import request
import os
from werkzeug.utils import secure_filename
from utils.mongodb_connect import get_mongodb_collection
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template(
        'index.html',
        files=FileModel.get_files()
    )

# 数据展示路由
@main_bp.route('/data')
def show_data():
    collection = get_mongodb_collection()
    page = request.args.get('page', 1, type=int)
    per_page = 30
    offset = (page - 1) * per_page
    
    # 获取多条件筛选参数
    query = {}
    i = 0
    while True:
        column_key = f'search_column_{i}'
        value_key = f'search_value_{i}'
        
        if column_key not in request.args:
            break
            
        column = request.args.get(column_key)
        value = request.args.get(value_key)
        
        if column and value:
            # 将字段值转换为字符串后进行正则匹配
            query['$and'] = query.get('$and', [])
            query['$and'].append({
                '$expr': {
                    '$regexMatch': {
                        'input': {'$toString': {'$ifNull': [f'${column}', '']}},
                        'regex': str(value),
                        'options': 'i'
                    }
                }
            })
        i += 1
    
    # 获取总记录数
    total_count = collection.count_documents(query)
    
    # 获取分页数据（按_id倒序）
    data = collection.find(query).sort('_id', -1).skip(offset).limit(per_page)

    '''
    # 从样本文档获取所有可能的列名
    sample_doc = collection.find_one() or {}
    unvisible_columns = ['_id','威胁分值','分类-威胁','分类-服务','分类-系统','分类-CVE年份',
                         '分类-时间','分类-应用', '解决方案','详细描述',
                         '周次','年份','数量','超期天数(2025年开始统计)','import_time']
    columns = [col for col in sample_doc.keys() if col not in unvisible_columns]
'''
    
    visible_columns = ['漏洞名称', '受影响主机', '受影响端口', '推动人', '关联资产', '年份', '周次', '修复结果', '修复日期', 
     '需要完成时间', '发现日期', 'CVEID']  # 替换为实际需要显示的字段名

    # 从样本文档中获取数据
    sample_doc = collection.find_one() or {}

    # 确保所有可见字段都存在于列列表中
    columns = []
    for col in visible_columns:
        if col in sample_doc:
            columns.append(col)
        else:
            columns.append(col)
        # 如果需要为缺失的列设置默认值，可以在这里处理
            sample_doc[col] = None  # 取消注释此行以设置默认值为None


    return render_template('data.html',
                        table_data=data,
                        columns=columns,
                        current_page=page,
                        total_pages=max(1, (total_count + per_page - 1) // per_page))
from bson.objectid import ObjectId
#删除一项数据
@main_bp.route('/delete_record/<id>', methods=['DELETE'])
def delete_record(id):
    try:
        data_model = DataModel()
        success = data_model.delete_record(ObjectId(id))
        return jsonify({'success': success})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)}), 400
# 更新某项
@main_bp.route('/update_record/<id>', methods=['PUT'])
def update_record(id):
    try:
        data_model = DataModel()
        updates = request.json
        success = data_model.update_record(id, updates)
        return jsonify({'success': success})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)}), 400
#批量操作
@main_bp.route('/batch_operation', methods=['POST'])
def batch_operation():
    try:
        data_model = DataModel()
        data = request.json
        action = data.get('action')
        ids = data.get('ids')
        # 修改操作处理
        if action == 'modify':
            column = data.get('column')
            value = data.get('value')
            if not all([column, value]):
                return jsonify({'success': False, 'error': '缺少必要参数'}), 400
            success = data_model.batch_modify(column, value, ids)
        else:
            success = data_model.batch_operation(action, ids)
        return jsonify({'success': success})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)}), 400

# 添加新路由 - 获取全部记录ID
@main_bp.route('/get_all_record_ids', methods=['POST'])
def get_all_record_ids():
    try:
        collection = get_mongodb_collection()
        data = request.json
        
        # 构建与数据展示页面相同的查询条件
        query = {}
        search_params = data.get('search_params', [])
        
        # 使用与数据展示页面完全一致的查询构建逻辑
        for param in search_params:
            column = param.get('column')
            value = param.get('value')
            
            if column and value:
                query.setdefault('$and', [])
                query['$and'].append({
                    '$expr': {
                        '$regexMatch': {
                            'input': {'$toString': {'$ifNull': [f'${column}', '']}},
                            'regex': str(value),
                            'options': 'i'
                        }
                    }
                })

        # 获取所有符合条件的记录ID
        records = collection.find(query, {'_id': 1})
        ids = [str(record['_id']) for record in records]
        
        return jsonify({'success': True, 'ids': ids})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

@main_bp.route('/upload_data', methods=['POST'])
def upload_data():
    try:
        if 'file' not in request.files:
            return jsonify(success=False, error="未选择文件")
            
        file = request.files['file']
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify(success=False, error="仅支持Excel文件")
        
        # 创建临时目录
        tmp_dir = Config.TMP_PATH
        os.makedirs(tmp_dir, exist_ok=True)
        
        # 保存临时文件
        temp_path = tmp_dir+'/'+file.filename
        file.save(temp_path)
        
        # 导入数据
        data_model = DataModel()
        success = data_model.import_from_excel(temp_path)
        
        # 清理临时文件
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"删除临时文件失败: {str(e)}")
        
        return jsonify(success=success)
        
    except Exception as e:
        return jsonify(success=False, error=str(e))