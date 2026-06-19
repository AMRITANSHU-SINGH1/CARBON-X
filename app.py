from flask import Flask
from config import Config
from extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    print(f"DEBUG: Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Ensure upload folder exists
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.verification import verification_bp
    from routes.marketplace import marketplace_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(verification_bp, url_prefix='/verification')
    app.register_blueprint(marketplace_bp, url_prefix='/marketplace')

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)