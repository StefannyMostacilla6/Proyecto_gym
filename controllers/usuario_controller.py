# controllers/usuario_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.conexion import conectar

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuarios')

@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            # NOTA: En producción usar hash de contraseña, aquí es ejemplo
            cursor.execute("""
                SELECT id, username, rol
                FROM usuarios
                WHERE username = %s
                AND password_hash = %s
                AND activo = TRUE
            """, (username, password))

            usuario = cursor.fetchone()
            cursor.close()
            conexion.close()

            if usuario:
                session['user_id'] = usuario[0]
                session['username'] = usuario[1]
                session['rol'] = usuario[2]
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('inicio'))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')

        except Exception as e:
            flash(f'Error de login: {str(e)}', 'danger')

    return render_template('login.html')

@usuario_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('usuario.login'))

# Ruta de prueba para verificar que el blueprint funciona
@usuario_bp.route('/test')
def test():
    return "Usuario blueprint funciona correctamente"