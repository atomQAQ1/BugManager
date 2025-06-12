from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)

    # 确保上传目录存在
    import os
    os.makedirs(app.config['UPLOADS_FOLDER'], exist_ok=True)

    # 注册蓝图
    from routes.main import main_bp
    from routes.files import files_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(files_bp)

    return app