import os
from flask import Flask, redirect, url_for
from config import Config
from Barberia0222.models import db, Usuario
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar la base de datos
    db.init_app(app)
    
    # Configuración de Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Redirige aquí si se requiere login
    login_manager.login_message = "Por favor inicia sesión para acceder."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Flask-Login usa esto para cargar al usuario de la sesión
        return Usuario.query.get(int(user_id))

    # --- RUTAS PRINCIPALES ---
    
    @app.route('/')
    def index():
        # Redirigimos automáticamente al login para que no veas el error 404
        return redirect(url_for('auth.login'))

    # --- REGISTRO DE BLUEPRINTS ---
    
    from Barberia0222.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app