from pymongo import MongoClient
from config import Config
from utils.data_mail_utils import send_mails
class DataModel:
    def __init__(self):
        client = MongoClient(
        host=Config.MONGODB_SETTINGS['host'],
        port=Config.MONGODB_SETTINGS['port']
        )
        db = client[Config.MONGODB_SETTINGS['db']]
        self.collection = db[Config.MONGODB_SETTINGS['collection']]

    def delete_record(self, record_id):
        """根据_id删除单条记录"""
        result = self.collection.delete_one({'_id': record_id})
        return result.deleted_count > 0
    def batch_operation(self, action, ids):
        """批量操作"""
        from bson.objectid import ObjectId
        object_ids = [ObjectId(id) for id in ids]
        
        if action == 'delete':
            result = self.collection.delete_many({'_id': {'$in': object_ids}})
            return result.deleted_count > 0
        elif action == 'export':
            return self.export_to_excel(object_ids)
        elif action=='remind':
            return self.remind(object_ids)
    def export_to_excel(self, ids):
        """将选中记录导出为Excel格式"""
        import pandas as pd
        from io import BytesIO
        # 查询选中的记录
        records = list(self.collection.find({'_id': {'$in': ids}}))
        if not records:
            return None
        # 转换为DataFrame
        df = pd.DataFrame(records)
        # 移除_id列
        if '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)
        # 如果指定了列顺序，则调整列的顺序
        column_order = ['漏洞名称', '威胁分值', 'CVEID', '分类-威胁', '分类-服务', '分类-系统', '分类-应用',
                         '受影响主机', '受影响端口', '发现日期', '需要完成时间', '修复日期', '修复结果', '推动人',
                           '关联资产', '详细描述', '解决方案', '备注', '周次', '年份']  # 替换为实际需要显示的字段名
        if column_order:
        # 获取DataFrame中实际存在的列
            valid_columns = [col for col in column_order if col in df.columns]
        # 获取不在column_order中但存在于DataFrame的列
            other_columns = [col for col in df.columns if col not in column_order]
        # 按指定顺序重新排列列
            df = df[valid_columns + other_columns]
        # 创建Excel输出
        df.to_excel(Config.DOWNLOADS_FOLDER + '/exported_records.xlsx', index=False)
        return Config.DOWNLOADS_FOLDER + '/exported_records.xlsx'
    
    def remind(self, ids):
        """提醒条目对应的安全员"""
        import pandas as pd
        from io import BytesIO
                # 查询选中的记录
        records = list(self.collection.find({'_id': {'$in': ids}}))
        if not records:
            return None
        # 转换为DataFrame
        df = pd.DataFrame(records)
        # 移除_id列
        if '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)

        return send_mails(df)
    def update_record(self, record_id, updates):
        """更新单条记录"""
        from bson.objectid import ObjectId
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(record_id)},
                {'$set': updates}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"更新记录错误: {str(e)}")
            return False
    def batch_modify(self, column, value, ids):
        """批量修改字段值"""
        from bson.objectid import ObjectId
        try:
            object_ids = [ObjectId(id) for id in ids]
            result = self.collection.update_many(
                {'_id': {'$in': object_ids}},
                {'$set': {column: value}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"批量修改失败: {str(e)}")
            return False
    # ... 已有导入 ...
    
    def import_from_excel(self, file_path):
        """从Excel文件导入数据到数据库"""
        try:
            import pandas as pd
            
            # 读取Excel文件
            df = pd.read_excel(file_path,engine='openpyxl')
            
            # 转换为字典列表并处理数据格式
            records = df.to_dict('records')
            for i, record in enumerate(records):
                # 直接通过索引修改原列表中的元素
                records[i] = {k: v if pd.notnull(v) else None for k, v in record.items()}

                
            # 批量插入数据
            if records:
                result = self.collection.insert_many(records)
                return len(result.inserted_ids) > 0
                
            return False
            
        except Exception as e:
            print(f"数据导入失败: {str(e)}")
            return False
