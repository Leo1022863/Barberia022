from flask import Blueprint, render_template, redirect, url_for, request, flash
from Barberia0222.models import db, Usuario, Rol, Cita, Servicio
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from datetime import date

# Definición del Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth', __name__)

# ==========================================================================
# SECCIÓN 1: AUTENTICACIÓN (LOGIN, REGISTRO, LOGOUT)
# ==========================================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.id_rol == 1:
            return redirect(url_for('auth.admin_dashboard'))
        elif current_user.id_rol == 3:
            return redirect(url_for('auth.barbero_dashboard'))
        else:
            return redirect(url_for('auth.cliente_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.password_hash, password):
            login_user(usuario)
            flash(f'Bienvenido, {usuario.nombre}')
            
            if usuario.id_rol == 1:
                return redirect(url_for('auth.admin_dashboard'))
            elif usuario.id_rol == 3:
                return redirect(url_for('auth.barbero_dashboard'))
            else:
                return redirect(url_for('auth.cliente_dashboard'))
        
        flash('Correo o contraseña incorrectos.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        telefono = request.form.get('telefono')
        email = request.form.get('email')  
        password = request.form.get('password')
        
        user_exists = Usuario.query.filter_by(email=email).first()
        if user_exists:
            flash('El correo electrónico ya está registrado.', 'danger')
            return redirect(url_for('auth.registro'))

        rol_cliente = Rol.query.filter_by(nombre_rol='Cliente').first()

        if not rol_cliente:
            flash('Error técnico: Los roles no han sido inicializados.', 'danger')
            return redirect(url_for('auth.registro'))

        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            email=email,
            password_hash=generate_password_hash(password, method='scrypt'),
            id_rol=rol_cliente.id_rol
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar: {e}', 'danger')
            return redirect(url_for('auth.registro'))

    return render_template('registro.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/perfil')
@login_required
def perfil():
    servicios_disponibles = Servicio.query.filter_by(estado=True).all()
    barberos_disponibles = Usuario.query.filter_by(id_rol=3).all()
    mis_citas = Cita.query.filter_by(id_cliente=current_user.id_usuario).order_by(Cita.fecha_cita.desc()).all()
    
    return render_template(
        'perfil.html',
        servicios=servicios_disponibles, 
        barberos=barberos_disponibles,
        citas=mis_citas,
        fecha_minima=date.today().strftime('%Y-%m-%d')
    )

# ==========================================================================
# SECCIÓN 2: CONTROLADOR Y CRUD DE ADMINISTRACIÓN (id_rol == 1)
# ==========================================================================

@auth_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta sección.', 'danger')
        return redirect(url_for('auth.cliente_dashboard'))
    
    usuarios = Usuario.query.all()
    return render_template('admin/dashboard.html', usuarios=usuarios)


@auth_bp.route('/admin/cambiar_rol/<int:usuario_id>', methods=['POST'])
@login_required
def cambiar_rol(usuario_id):
    if current_user.id_rol != 1: 
        flash('No tienes autorización para realizar esta acción.', 'danger')
        return redirect(url_for('auth.cliente_dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    nuevo_rol = request.form.get('nuevo_rol')
    
    usuario.id_rol = nuevo_rol
    db.session.commit()
    
    flash(f'Rol de {usuario.nombre} actualizado correctamente.', 'success')
    return redirect(url_for('auth.admin_dashboard'))


@auth_bp.route('/admin/usuario/agregar', methods=['POST'])
@login_required
def agregar_usuario():
    if current_user.id_rol != 1:
        flash('No tienes autorización para realizar esta acción.', 'danger')
        return redirect(url_for('auth.cliente_dashboard'))
        
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    telefono = request.form.get('telefono')  
    email = request.form.get('email')
    password = request.form.get('password')
    id_rol = request.form.get('id_rol')
    
    user_exists = Usuario.query.filter_by(email=email).first()
    if user_exists:
        flash('El correo electrónico ya se encuentra registrado.', 'danger')
        return redirect(url_for('auth.admin_dashboard'))
        
    nuevo_usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        telefono=telefono,  
        email=email,
        password_hash=generate_password_hash(password, method='scrypt'),
        id_rol=id_rol
    )
    
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash(f'Usuario {nombre} registrado exitosamente desde el Panel.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear the usuario: {e}', 'danger')
        
    return redirect(url_for('auth.admin_dashboard'))


@auth_bp.route('/admin/usuario/eliminar/<int:usuario_id>', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    if current_user.id_rol != 1:
        flash('No tienes autorización para realizar esta acción.', 'danger')
        return redirect(url_for('auth.cliente_dashboard'))
        
    if current_user.id_usuario == usuario_id:
        flash('No puedes eliminar tu propia cuenta de administrador en uso.', 'warning')
        return redirect(url_for('auth.admin_dashboard'))
        
    usuario = Usuario.query.get_or_404(usuario_id)
    nombre_eliminado = f"{usuario.nombre} {usuario.apellido}"
    
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash(f'El usuario "{nombre_eliminado}" fue eliminado permanentemente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al intentar eliminar el usuario: {e}', 'danger')
        
    return redirect(url_for('auth.admin_dashboard'))


@auth_bp.route('/admin/usuario/editar/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario_view(usuario_id):
    if current_user.id_rol != 1:
        flash('No tienes autorización para realizar esta acción.', 'danger')
        return redirect(url_for('auth.cliente_dashboard'))
        
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        usuario.nombre = request.form.get('nombre')
        usuario.apellido = request.form.get('apellido')
        usuario.email = request.form.get('email')
        usuario.telefono = request.form.get('telefono') 
        
        nueva_password = request.form.get('password')
        if nueva_password:
            usuario.password_hash = generate_password_hash(nueva_password, method='scrypt')
            
        try:
            db.session.commit()
            flash(f'Datos de {usuario.nombre} actualizados con éxito.', 'success')
            return redirect(url_for('auth.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar los datos: {e}', 'danger')
            
    return render_template('admin/editar_usuario.html', usuario=usuario)


# ==========================================================================
# SECCIÓN 3: CONTROLADOR OPERATIVO DEL BARBERO (id_rol == 3)
# ==========================================================================

@auth_bp.route('/barbero/dashboard')
@login_required
def barbero_dashboard():
    if current_user.id_rol != 3:
        flash('No tienes permiso para acceder a la sección de barberos.', 'danger')
        return redirect(url_for('auth.cliente_dashboard'))
    
    hoy = date.today()
    
    citas_hoy = Cita.query.filter_by(id_barbero=current_user.id_usuario, fecha_cita=hoy).order_by(Cita.hora_cita.asc()).all()
    
    citas_futuras = Cita.query.filter(
        Cita.id_barbero == current_user.id_usuario,
        Cita.fecha_cita > hoy
    ).order_by(Cita.fecha_cita.asc(), Cita.hora_cita.asc()).all()
    
    pendientes = 0
    completadas = 0
    total_recaudado = 0.0
    porcentaje_comision = 0.50

    for cita in citas_hoy:
        if cita.estado in ['Pendiente', 'Confirmada']:
            pendientes += 1
        elif cita.estado == 'Completada':
            completadas += 1
            if cita.servicio:
                total_recaudado += float(cita.servicio.precio)
    
    mis_comisiones_hoy = total_recaudado * porcentaje_comision

    return render_template(
        'barbero/dashboard.html', 
        citas=citas_hoy,
        citas_posteriores=citas_futuras,
        pendientes=pendientes,
        completadas=completadas,
        comisiones=mis_comisiones_hoy,
        fecha_actual=hoy.strftime('%d/%m/%Y')
    )


@auth_bp.route('/barbero/cita/estado/<int:cita_id>', methods=['POST'])
@login_required
def actualizar_estado_cita(cita_id):
    if current_user.id_rol != 3:
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('auth.cliente_dashboard'))
        
    cita = Cita.query.get_or_404(cita_id)
    
    if cita.id_barbero != current_user.id_usuario:
        flash('No puedes modificar una cita que no te pertenece.', 'danger')
        return redirect(url_for('auth.barbero_dashboard'))
        
    nuevo_estado = request.form.get('nuevo_estado')
    if nuevo_estado in ['Pendiente', 'Confirmada', 'Completada', 'Cancelada']:
        cita.estado = nuevo_estado
        try:
            db.session.commit()
            flash(f'¡Cita #{cita_id} actualizada a "{nuevo_estado}" con éxito!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error interno al guardar el estado en la base de datos.', 'danger')
            
    return redirect(url_for('auth.barbero_dashboard'))


# ==========================================================================
# SECCIÓN 4: CONTROLADOR ENRIQUECIDO DEL CLIENTE (id_rol == 2)
# ==========================================================================

@auth_bp.route('/cliente/dashboard')
@login_required
def cliente_dashboard():
    if current_user.id_rol != 2:
        if current_user.id_rol == 1:
            return redirect(url_for('auth.admin_dashboard'))
        elif current_user.id_rol == 3:
            return redirect(url_for('auth.barbero_dashboard'))
    
    hoy = date.today()
    
    try:
        barberos_disponibles = Usuario.query.filter_by(id_rol=3).all()
        servicios_disponibles = Servicio.query.filter_by(estado=True).all()
    except Exception:
        barberos_disponibles = []
        servicios_disponibles = []

    try:
        mis_citas = Cita.query.filter_by(id_cliente=current_user.id_usuario).order_by(Cita.fecha_cita.desc()).all()
    except Exception:
        mis_citas = []
        
    return render_template(
        'cliente/dashboard.html',
        citas=mis_citas,
        barberos=barberos_disponibles,
        servicios=servicios_disponibles,
        fecha_actual=hoy.strftime('%d/%m/%Y'),
        fecha_minima=hoy.strftime('%Y-%m-%d')
    )


@auth_bp.route('/cliente/agendar-cita', methods=['POST'])
@login_required
def agendar_cita_cliente():
    if current_user.id_rol != 2:
        flash('Acción no autorizada.')
        return redirect(url_for('auth.cliente_dashboard'))
        
    id_servicio = request.form.get('id_servicio')
    id_barbero = request.form.get('id_barbero')
    fecha_str = request.form.get('fecha_cita')
    hora_str = request.form.get('hora_cita')
    
    if not (id_servicio and id_barbero and fecha_str and hora_str):
        flash('Todos los campos del formulario de reserva son obligatorios.', 'danger')
        return redirect(url_for('auth.cliente_dashboard'))
        
    try:
        from datetime import datetime
        fecha_objeto = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora_objeto = datetime.strptime(hora_str, '%H:%M').time()
        
        nueva_cita = Cita(
            id_cliente=current_user.id_usuario,
            id_barbero=int(id_barbero),
            id_servicio=int(id_servicio),
            fecha_cita=fecha_objeto,
            hora_cita=hora_objeto,
            estado='Pendiente'
        )
        
        db.session.add(nueva_cita)
        db.session.commit()
        flash('¡Tu turno ha sido reservado con éxito! Revisa su estado en tu panel.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la reserva del turno: {e}', 'danger')
        
    return redirect(url_for('auth.cliente_dashboard'))