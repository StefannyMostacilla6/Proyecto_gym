from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.conexion import conectar

horario_bp = Blueprint('horario', __name__, url_prefix='/horarios')


@horario_bp.route('/')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # ✅ CORREGIDO: Sin CASE, ordenando directamente por el ENUM
        cursor.execute("""
                       SELECT h.id,
                              c.nombre                          as clase,
                              e.nombre || ' ' || e.apellido     as entrenador,
                              h.dia_semana,
                              TO_CHAR(h.hora_inicio, 'HH24:MI') as hora_inicio,
                              TO_CHAR(h.hora_fin, 'HH24:MI')    as hora_fin,
                              h.sala,
                              h.activo
                       FROM horarios h
                                JOIN clases c ON h.clase_id = c.id
                                JOIN entrenadores e ON h.entrenador_id = e.id
                       WHERE h.activo = TRUE
                       ORDER BY h.dia_semana, h.hora_inicio
                       """)

        horarios = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template('horarios.html', horarios=horarios)

    except Exception as e:
        flash(f'Error al listar horarios: {e}', 'danger')
        return redirect(url_for('inicio'))


@horario_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        clase_id = int(request.form['clase_id'])
        entrenador_id = int(request.form['entrenador_id'])
        dia_semana = request.form['dia_semana']
        hora_inicio = request.form['hora_inicio']
        hora_fin = request.form['hora_fin']
        sala = request.form.get('sala', '')

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           INSERT INTO horarios (clase_id, entrenador_id, dia_semana,
                                                 hora_inicio, hora_fin, sala, creado_por)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           """, (clase_id, entrenador_id, dia_semana, hora_inicio, hora_fin, sala, session['username']))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Horario creado exitosamente', 'success')
            return redirect(url_for('horario.listar'))

        except Exception as e:
            flash(f'Error al crear horario: {e}', 'danger')

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT id, nombre FROM clases WHERE activo = TRUE")
        clases = cursor.fetchall()

        cursor.execute("SELECT id, nombre || ' ' || apellido as nombre FROM entrenadores WHERE activo = TRUE")
        entrenadores = cursor.fetchall()

        cursor.close()
        conexion.close()

        return render_template('horario_form.html', clases=clases, entrenadores=entrenadores)

    except Exception as e:
        flash(f'Error al cargar formulario: {e}', 'danger')
        return redirect(url_for('horario.listar'))


@horario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        clase_id = int(request.form['clase_id'])
        entrenador_id = int(request.form['entrenador_id'])
        dia_semana = request.form['dia_semana']
        hora_inicio = request.form['hora_inicio']
        hora_fin = request.form['hora_fin']
        sala = request.form.get('sala', '')
        activo = request.form.get('activo') == 'on'

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           UPDATE horarios
                           SET clase_id            = %s,
                               entrenador_id       = %s,
                               dia_semana          = %s,
                               hora_inicio         = %s,
                               hora_fin            = %s,
                               sala                = %s,
                               activo              = %s,
                               actualizado_por     = %s,
                               fecha_actualizacion = CURRENT_TIMESTAMP
                           WHERE id = %s
                           """, (clase_id, entrenador_id, dia_semana, hora_inicio, hora_fin,
                                 sala, activo, session['username'], id))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Horario actualizado exitosamente', 'success')
            return redirect(url_for('horario.listar'))

        except Exception as e:
            flash(f'Error al actualizar horario: {e}', 'danger')

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT h.id,
                              h.clase_id,
                              h.entrenador_id,
                              h.dia_semana,
                              h.hora_inicio,
                              h.hora_fin,
                              h.sala,
                              h.activo
                       FROM horarios h
                       WHERE h.id = %s
                       """, (id,))
        horario = cursor.fetchone()

        cursor.execute("SELECT id, nombre FROM clases WHERE activo = TRUE")
        clases = cursor.fetchall()

        cursor.execute("SELECT id, nombre || ' ' || apellido as nombre FROM entrenadores WHERE activo = TRUE")
        entrenadores = cursor.fetchall()

        cursor.close()
        conexion.close()

        if not horario:
            flash('Horario no encontrado', 'danger')
            return redirect(url_for('horario.listar'))

        return render_template('horario_form.html', horario=horario, clases=clases, entrenadores=entrenadores)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('horario.listar'))


@horario_bp.route('/eliminar/<int:id>')
def eliminar(id):
    if 'user_id' not in session or session.get('rol') not in ['admin']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       UPDATE horarios
                       SET activo            = FALSE,
                           eliminado_por     = %s,
                           fecha_eliminacion = CURRENT_TIMESTAMP
                       WHERE id = %s
                       """, (session['username'], id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Horario eliminado exitosamente', 'success')

    except Exception as e:
        flash(f'Error al eliminar horario: {e}', 'danger')

    return redirect(url_for('horario.listar'))