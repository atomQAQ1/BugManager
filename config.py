import os

class Config:
    UPLOADS_FOLDER = 'uploads'
    DOWNLOADS_FOLDER = 'downloads'
    CURRENT_FOLDER = 'downloads'  # 默认显示downloads文件夹
    LOG_PATH = 'log'
    WEEKLY_SCAN_RESULT_PATH="主机扫描周表.xlsx"#本周漏洞表名称
    WHITELIST_PATH=UPLOADS_FOLDER+'/白名单.txt'
    PUSHER_PATH=UPLOADS_FOLDER+"/区域漏洞负责人.xlsx"
    TMP_PATH="tmp"
    TMP_MAIL_PATH=TMP_PATH+"/mail"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xlsx', 'xls'}
    MONGODB_SETTINGS = {
        'host': '127.0.0.1',
        'port': 27017,
        'db': 'vuln_db',
        'collection': 'file_records'
    }
class MAIL_CONFIG:
    # 邮箱配置
    SENDER = 'zhiruikang@intra.nsfocus.com'       # 发件人邮箱
    PASSWORD = 'wwX36WCw5'
    SMTP_SERVER = 'mail.intra.nsfocus.com'
    ADMIN_EMAIL = "zhiruikang@intra.nsfocus.com"  # 管理员邮箱
    PORT = 25
    
    # 邮件内容s
    SUBJECT = '安全员负责区域漏洞推送提醒'
    CONTENT = '''您好！附件中是您负责的区域本周的高危漏洞，麻烦您联系下相关负责人尽量在本周五前修复。\
    修复完成后请填写表格中的修复时间和修复结果，并将结果通过企业微信发送给支睿康。\
        修复完成或存在任何问题请通过邮箱或企业微信联系何恩寒，感谢您的配合！'''
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False