# app/__init__.py
from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager

mysql = MySQL()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    @app.template_filter('currency')
    def currency_format(value):
        try:
            return "Rp {:,.0f}".format(value).replace(',', '.')
        except:
            return value

    # Inisialisasi extension
    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register template filter
    @app.template_filter('currency')
    def currency_format(value):
        try:
            return "Rp {:,.0f}".format(value).replace(',', '.')
        except:
            return value

    # Import dan daftarkan blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app