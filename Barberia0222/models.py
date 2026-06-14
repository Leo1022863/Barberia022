from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

# Inicializamos la base de datos sin una app específica (App Factory)
db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = 'roles'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False)
    # Relación para obtener todos los usuarios de un rol específico
    usuarios = db.relationship('Usuario', backref='rol_info', lazy=True)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'))
    # Usamos timezone-aware objects para evitar advertencias de depreciación
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Requerido por Flask-Login para identificar al usuario de forma única
    def get_id(self):
        return str(self.id_usuario)

class Servicio(db.Model):
    __tablename__ = 'servicios'
    id_servicio = db.Column(db.Integer, primary_key=True)
    nombre_servicio = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    duracion_minutos = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.Boolean, default=True)

class Cita(db.Model):
    __tablename__ = 'citas'
    id_cita = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    id_barbero = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicios.id_servicio'))
    fecha_cita = db.Column(db.Date, nullable=False)
    hora_cita = db.Column(db.Time, nullable=False)
    # Definimos el Enum para mantener consistencia con MySQL
    estado = db.Column(db.Enum('Pendiente', 'Confirmada', 'Completada', 'Cancelada'), default='Pendiente')
    notas = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones para acceder a los objetos relacionados directamente
    cliente = db.relationship('Usuario', foreign_keys=[id_cliente], backref='citas_cliente')
    barbero = db.relationship('Usuario', foreign_keys=[id_barbero], backref='citas_barbero')
    servicio = db.relationship('Servicio', backref='citas_servicio')