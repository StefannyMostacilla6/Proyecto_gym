from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.conexion import conectar

membresia_bp = Blueprint('membresia', __name__, url_prefix='/membresias')


@membresia_bp.route('/')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT id,
                              tipo,
                              descripcion,
                              precio,
                              duracion_dias,
                              max_clases_semana,
                              activo
                       FROM membresias
                       WHERE activo = TRUE
                       ORDER BY id
                       """)

        membresias = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template('membresias.html', membresias=membresias)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('inicio'))


@membresia_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        tipo = request.form['tipo']
        descripcion = request.form.get('descripcion', '')
        precio = float(request.form['precio'])
        duracion_dias = int(request.form['duracion_dias'])
        max_clases_semana = int(request.form.get('max_clases_semana', 3))

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           INSERT INTO membresias (tipo, descripcion, precio, duracion_dias,
                                                   max_clases_semana, creado_por)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           """, (tipo, descripcion, precio, duracion_dias, max_clases_semana, session['username']))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Membresía creada exitosamente', 'success')
            return redirect(url_for('membresia.listar'))

        except Exception as e:
            flash(f'Error al crear membresía: {e}', 'danger')

    return render_template('membresia_form.html')


@membresia_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        tipo = request.form['tipo']
        descripcion = request.form.get('descripcion', '')
        precio = float(request.form['precio'])
        duracion_dias = int(request.form['duracion_dias'])
        max_clases_semana = int(request.form.get('max_clases_semana', 3))
        activo = request.form.get('activo') == 'on'

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           UPDATE membresias
                           SET tipo                = %s,
                               descripcion         = %s,
                               precio              = %s,
                               duracion_dias       = %s,
                               max_clases_semana   = %s,
                               activo              = %s,
                               actualizado_por     = %s,
                               fecha_actualizacion = CURRENT_TIMESTAMP
                           WHERE id = %s
                           """, (tipo, descripcion, precio, duracion_dias, max_clases_semana,
                                 activo, session['username'], id))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Membresía actualizada exitosamente', 'success')
            return redirect(url_for('membresia.listar'))

        except Exception as e:
            flash(f'Error al actualizar membresía: {e}', 'danger')

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM membresias WHERE id = %s", (id,))
        membresia = cursor.fetchone()
        cursor.close()
        conexion.close()

        return render_template('membresia_form.html', membresia=membresia)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('membresia.listar'))


@membresia_bp.route('/eliminar/<int:id>')
def eliminar(id):
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       UPDATE membresias
                       SET activo            = FALSE,
                           eliminado_por     = %s,
                           fecha_eliminacion = CURRENT_TIMESTAMP
                       WHERE id = %s
                       """, (session['username'], id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Membresía eliminada exitosamente', 'success')

    except Exception as e:
        flash(f'Error al eliminar membresía: {e}', 'danger')

    return redirect(url_for('membresia.listar'))