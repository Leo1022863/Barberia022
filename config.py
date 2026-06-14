import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_secreta_barberia_0222'
    # Ajusta 'root' y 'password' según tu configuración de MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/bd_barberia'
    SQLALCHEMY_TRACK_MODIFICATIONS = False