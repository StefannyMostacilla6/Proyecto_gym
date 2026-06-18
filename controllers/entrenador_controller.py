from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.conexion import conectar

entrenador_bp = Blueprint('entrenador', __name__, url_prefix='/entrenadores')


@entrenador_bp.route('/')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT id, nombre, apellido, especialidad, email, telefono
                       FROM entrenadores
                       WHERE activo = TRUE
                       ORDER BY id
                       """)

        entrenadores = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template('entrenadores.html', entrenadores=entrenadores)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('inicio'))


@entrenador_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        especialidad = request.form.get('especialidad', '')
        email = request.form['email']
        telefono = request.form.get('telefono', '')

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           INSERT INTO entrenadores (nombre, apellido, especialidad, email, telefono, creado_por)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           """, (nombre, apellido, especialidad, email, telefono, session['username']))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Entrenador registrado exitosamente', 'success')
            return redirect(url_for('entrenador.listar'))

        except Exception as e:
            flash(f'Error al registrar entrenador: {e}', 'danger')

    return render_template('entrenador_form.html')


@entrenador_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        especialidad = request.form.get('especialidad', '')
        email = request.form['email']
        telefono = request.form.get('telefono', '')
        activo = request.form.get('activo') == 'on'

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           UPDATE entrenadores
                           SET nombre              = %s,
                               apellido            = %s,
                               especialidad        = %s,
                               email               = %s,
                               telefono            = %s,
                               activo              = %s,
                               actualizado_por     = %s,
                               fecha_actualizacion = CURRENT_TIMESTAMP
                           WHERE id = %s
                           """, (nombre, apellido, especialidad, email, telefono, activo, session['username'], id))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Entrenador actualizado exitosamente', 'success')
            return redirect(url_for('entrenador.listar'))

        except Exception as e:
            flash(f'Error al actualizar entrenador: {e}', 'danger')

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM entrenadores WHERE id = %s", (id,))
        entrenador = cursor.fetchone()
        cursor.close()
        conexion.close()

        return render_template('entrenador_form.html', entrenador=entrenador)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('entrenador.listar'))


@entrenador_bp.route('/eliminar/<int:id>')
def eliminar(id):
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       UPDATE entrenadores
                       SET activo            = FALSE,
                           eliminado_por     = %s,
                           fecha_eliminacion = CURRENT_TIMESTAMP
                       WHERE id = %s
                       """, (session['username'], id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Entrenador eliminado exitosamente', 'success')

    except Exception as e:
        flash(f'Error al eliminar entrenador: {e}', 'danger')

    return redirect(url_for('entrenador.listar'))