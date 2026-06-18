from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.conexion import conectar

clase_bp = Blueprint('clase', __name__, url_prefix='/clases')


@clase_bp.route('/')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT id, nombre, descripcion, cupo_maximo, duracion_minutos, activo
                       FROM clases
                       ORDER BY id
                       """)

        clases = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template('clases.html', clases=clases)

    except Exception as e:
        flash(f'Error al listar clases: {e}', 'danger')
        return redirect(url_for('inicio'))


@clase_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        cupo_maximo = int(request.form['cupo_maximo'])
        duracion_minutos = int(request.form['duracion_minutos'])

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           INSERT INTO clases (nombre, descripcion, cupo_maximo, duracion_minutos, creado_por)
                           VALUES (%s, %s, %s, %s, %s)
                           """, (nombre, descripcion, cupo_maximo, duracion_minutos, session['username']))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Clase creada exitosamente', 'success')
            return redirect(url_for('clase.listar'))

        except Exception as e:
            flash(f'Error al crear clase: {e}', 'danger')

    return render_template('clase_form.html')


@clase_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        cupo_maximo = int(request.form['cupo_maximo'])
        duracion_minutos = int(request.form['duracion_minutos'])
        activo = request.form.get('activo') == 'on'

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           UPDATE clases
                           SET nombre              = %s,
                               descripcion         = %s,
                               cupo_maximo         = %s,
                               duracion_minutos    = %s,
                               activo              = %s,
                               actualizado_por     = %s,
                               fecha_actualizacion = CURRENT_TIMESTAMP
                           WHERE id = %s
                           """, (nombre, descripcion, cupo_maximo, duracion_minutos, activo, session['username'], id))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Clase actualizada exitosamente', 'success')
            return redirect(url_for('clase.listar'))

        except Exception as e:
            flash(f'Error al actualizar clase: {e}', 'danger')

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id, nombre, descripcion, cupo_maximo, duracion_minutos, activo FROM clases WHERE id = %s", (id,))
        clase = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not clase:
            flash('Clase no encontrada', 'danger')
            return redirect(url_for('clase.listar'))

        return render_template('clase_form.html', clase=clase)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('clase.listar'))


@clase_bp.route('/eliminar/<int:id>')
def eliminar(id):
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Soft delete (borrado lógico)
        cursor.execute("""
                       UPDATE clases
                       SET activo            = FALSE,
                           eliminado_por     = %s,
                           fecha_eliminacion = CURRENT_TIMESTAMP
                       WHERE id = %s
                       """, (session['username'], id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Clase eliminada exitosamente', 'success')

    except Exception as e:
        flash(f'Error al eliminar clase: {e}', 'danger')

    return redirect(url_for('clase.listar'))