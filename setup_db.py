from app import app
from Barberia0222.models import db, Rol

def inicializar():
    with app.app_context():
        print("Conectando a la base de datos...")
        # Crea las tablas
        db.create_all()
        print("Tablas creadas con éxito.")

        # Verifica si los roles ya existen para no duplicarlos
        if not Rol.query.filter_by(nombre_rol='Administrador').first():
            admin = Rol(nombre_rol='Administrador')
            cliente = Rol(nombre_rol='Cliente')
            barbero = Rol(nombre_rol='Barbero')
            db.session.add_all([admin, cliente, barbero])
            db.session.commit()
            print("Roles iniciales insertados.")
        else:
            print("Los roles ya existían.")

if __name__ == '__main__':
    try:
        inicializar()
        print("--- PROCESO COMPLETADO ---")
    except Exception as e:
        print(f"ERROR: {e}")