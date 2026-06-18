from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.conexion import conectar
from datetime import datetime

reserva_bp = Blueprint('reserva', __name__, url_prefix='/reservas')


@reserva_bp.route('/')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT r.id,
                              m.nombre || ' ' || m.apellido          as miembro,
                              c.nombre                               as clase,
                              TO_CHAR(r.fecha_clase, 'DD/MM/YYYY')   as fecha_clase,
                              r.estado,
                              TO_CHAR(r.fecha_reserva, 'DD/MM/YYYY') as fecha_reserva,
                              TO_CHAR(h.hora_inicio, 'HH24:MI')      as hora_inicio,
                              CASE
                                  WHEN r.estado = 'confirmada' THEN 'success'
                                  WHEN r.estado = 'cancelada' THEN 'danger'
                                  WHEN r.estado = 'lista_espera' THEN 'warning'
                                  WHEN r.estado = 'completada' THEN 'info'
                                  ELSE 'secondary'
                                  END                                as color_estado
                       FROM reservas r
                                JOIN miembros m ON r.miembro_id = m.id
                                JOIN horarios h ON r.horario_id = h.id
                                JOIN clases c ON h.clase_id = c.id
                       WHERE r.activo = TRUE
                       ORDER BY r.fecha_clase DESC, h.hora_inicio ASC
                       """)

        reservas = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template('reservas.html', reservas=reservas)

    except Exception as e:
        flash(f'Error al listar reservas: {e}', 'danger')
        return redirect(url_for('inicio'))


@reserva_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    if request.method == 'POST':
        miembro_id = int(request.form['miembro_id'])
        horario_id = int(request.form['horario_id'])
        fecha_clase = request.form['fecha_clase']

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            # Verificar cupo disponible
            cursor.execute("""
                           SELECT c.cupo_maximo, COUNT(r.id)
                           FROM horarios h
                                    JOIN clases c ON h.clase_id = c.id
                                    LEFT JOIN reservas r ON r.horario_id = h.id
                               AND r.fecha_clase = %s
                               AND r.estado IN ('confirmada', 'lista_espera')
                               AND r.activo = TRUE
                           WHERE h.id = %s
                           GROUP BY c.cupo_maximo
                           """, (fecha_clase, horario_id))

            resultado = cursor.fetchone()
            cupo_maximo = resultado[0] if resultado else 0
            reservas_actuales = resultado[1] if resultado else 0

            estado = 'confirmada'
            if reservas_actuales >= cupo_maximo:
                estado = 'lista_espera'
                flash('Cupo lleno. Se agregó a lista de espera.', 'warning')

            cursor.execute("""
                           INSERT INTO reservas (miembro_id, horario_id, fecha_clase, estado, creado_por)
                           VALUES (%s, %s, %s, %s, %s) RETURNING id
                           """, (miembro_id, horario_id, fecha_clase, estado, session['username']))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Reserva registrada exitosamente', 'success')
            return redirect(url_for('reserva.listar'))

        except Exception as e:
            flash(f'Error al registrar reserva: {e}', 'danger')

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id, nombre || ' ' || apellido as nombre FROM miembros WHERE activo = TRUE ORDER BY nombre")
        miembros = cursor.fetchall()

        # Consulta corregida - ORDER BY directo sobre el ENUM
        cursor.execute("""
                       SELECT h.id,
                              c.nombre                          as clase,
                              e.nombre || ' ' || e.apellido     as entrenador,
                              h.dia_semana,
                              TO_CHAR(h.hora_inicio, 'HH24:MI') as hora_inicio,
                              TO_CHAR(h.hora_fin, 'HH24:MI')    as hora_fin,
                              h.sala,
                              c.cupo_maximo
                       FROM horarios h
                                JOIN clases c ON h.clase_id = c.id
                                JOIN entrenadores e ON h.entrenador_id = e.id
                       WHERE h.activo = TRUE
                       ORDER BY h.dia_semana, h.hora_inicio
                       """)
        horarios = cursor.fetchall()

        cursor.close()
        conexion.close()

        hoy = datetime.now().strftime('%Y-%m-%d')

        return render_template('reserva_form.html',
                               miembros=miembros,
                               horarios=horarios,
                               hoy=hoy)

    except Exception as e:
        flash(f'Error al cargar formulario: {e}', 'danger')
        return redirect(url_for('inicio'))


@reserva_bp.route('/cancelar/<int:id>')
def cancelar(id):
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       UPDATE reservas
                       SET estado              = 'cancelada',
                           activo              = FALSE,
                           actualizado_por     = %s,
                           fecha_actualizacion = CURRENT_TIMESTAMP
                       WHERE id = %s
                         AND estado != 'completada'
                       """, (session['username'], id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Reserva cancelada exitosamente', 'success')

    except Exception as e:
        flash(f'Error al cancelar reserva: {e}', 'danger')

    return redirect(url_for('reserva.listar'))


@reserva_bp.route('/confirmar/<int:id>')
def confirmar(id):
    if 'user_id' not in session or session.get('rol') not in ['admin', 'recepcionista']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       UPDATE reservas
                       SET estado              = 'confirmada',
                           actualizado_por     = %s,
                           fecha_actualizacion = CURRENT_TIMESTAMP
                       WHERE id = %s
                       """, (session['username'], id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Reserva confirmada exitosamente', 'success')

    except Exception as e:
        flash(f'Error al confirmar reserva: {e}', 'danger')

    return redirect(url_for('reserva.listar'))


# =====================================================
# CANCELAR RESERVA CON PENALIZACIÓN USANDO PROCEDIMIENTO
# =====================================================
@reserva_bp.route('/cancelar_con_penalizacion/<int:id>', methods=['GET', 'POST'])
def cancelar_con_penalizacion(id):
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    if request.method == 'POST':
        motivo = request.form.get('motivo', 'Cancelación voluntaria')

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                CALL cancelar_reserva_con_penalizacion(%s, %s, %s)
            """, (id, motivo, session['username']))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Reserva cancelada exitosamente', 'success')
            return redirect(url_for('reserva.listar'))

        except Exception as e:
            flash(f'Error al cancelar reserva: {e}', 'danger')

    # Obtener datos de la reserva para mostrar confirmación
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT r.id,
                              m.nombre || ' ' || m.apellido        as miembro,
                              c.nombre                             as clase,
                              TO_CHAR(r.fecha_clase, 'DD/MM/YYYY') as fecha_clase,
                              TO_CHAR(h.hora_inicio, 'HH24:MI')    as hora_inicio
                       FROM reservas r
                                JOIN miembros m ON r.miembro_id = m.id
                                JOIN horarios h ON r.horario_id = h.id
                                JOIN clases c ON h.clase_id = c.id
                       WHERE r.id = %s
                       """, (id,))
        reserva = cursor.fetchone()
        cursor.close()
        conexion.close()
    except:
        reserva = None

    return render_template('cancelar_reserva.html', reserva=reserva)


# =====================================================
# OBTENER HORARIOS DISPONIBLES (API para AJAX)
# =====================================================
@reserva_bp.route('/horarios_disponibles')
def horarios_disponibles():
    """API para obtener horarios disponibles por fecha (para uso con AJAX)"""
    if 'user_id' not in session:
        return {'error': 'No autorizado'}, 401

    fecha = request.args.get('fecha')
    if not fecha:
        return {'error': 'Fecha requerida'}, 400

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT h.id,
                              c.nombre                          as clase,
                              e.nombre || ' ' || e.apellido     as entrenador,
                              h.dia_semana,
                              TO_CHAR(h.hora_inicio, 'HH24:MI') as hora_inicio,
                              TO_CHAR(h.hora_fin, 'HH24:MI')    as hora_fin,
                              h.sala,
                              c.cupo_maximo,
                              (c.cupo_maximo - COUNT(r.id))     as cupo_disponible
                       FROM horarios h
                                JOIN clases c ON h.clase_id = c.id
                                JOIN entrenadores e ON h.entrenador_id = e.id
                                LEFT JOIN reservas r ON r.horario_id = h.id
                           AND r.fecha_clase = %s
                           AND r.estado IN ('confirmada', 'lista_espera')
                           AND r.activo = TRUE
                       WHERE h.activo = TRUE
                         AND EXTRACT(DOW FROM %s::date) =
                             CASE h.dia_semana
                                 WHEN 'Lunes' THEN 1
                                 WHEN 'Martes' THEN 2
                                 WHEN 'Miércoles' THEN 3
                                 WHEN 'Jueves' THEN 4
                                 WHEN 'Viernes' THEN 5
                                 WHEN 'Sábado' THEN 6
                                 WHEN 'Domingo' THEN 0
                                 END
                       GROUP BY h.id, c.nombre, c.cupo_maximo, e.nombre, e.apellido,
                                h.dia_semana, h.hora_inicio, h.hora_fin, h.sala
                       HAVING (c.cupo_maximo - COUNT(r.id)) > 0
                       ORDER BY h.hora_inicio
                       """, (fecha, fecha))

        horarios = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Convertir a lista de diccionarios
        resultados = []
        for h in horarios:
            resultados.append({
                'id': h[0],
                'clase': h[1],
                'entrenador': h[2],
                'dia': h[3],
                'hora_inicio': h[4],
                'hora_fin': h[5],
                'sala': h[6],
                'cupo_maximo': h[7],
                'cupo_disponible': h[8]
            })

        return {'horarios': resultados}

    except Exception as e:
        return {'error': str(e)}, 500