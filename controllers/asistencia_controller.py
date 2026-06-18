from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.conexion import conectar
from datetime import datetime

asistencia_bp = Blueprint('asistencia', __name__, url_prefix='/asistencias')


@asistencia_bp.route('/')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT a.id,
                              m.nombre || ' ' || m.apellido as miembro,
                              c.nombre                      as clase,
                              a.fecha_checkin
                       FROM asistencias a
                                JOIN reservas r ON a.reserva_id = r.id
                                JOIN miembros m ON r.miembro_id = m.id
                                JOIN horarios h ON r.horario_id = h.id
                                JOIN clases c ON h.clase_id = c.id
                       WHERE a.activo = TRUE
                       ORDER BY a.fecha_checkin DESC
                       """)

        asistencias = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template('asistencias.html', asistencias=asistencias)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('inicio'))


@asistencia_bp.route('/registrar/<int:reserva_id>')
def registrar(reserva_id):
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar que la reserva existe y está confirmada
        cursor.execute("""
                       SELECT estado
                       FROM reservas
                       WHERE id = %s
                         AND activo = TRUE
                       """, (reserva_id,))
        reserva = cursor.fetchone()

        if not reserva:
            flash('Reserva no encontrada', 'danger')
            return redirect(url_for('reserva.listar'))

        if reserva[0] != 'confirmada':
            flash('Solo se puede registrar asistencia para reservas confirmadas', 'warning')
            return redirect(url_for('reserva.listar'))

        # Registrar asistencia
        cursor.execute("""
                       INSERT INTO asistencias (reserva_id, creado_por)
                       VALUES (%s, %s)
                       """, (reserva_id, session['username']))

        # Actualizar estado de reserva a completada
        cursor.execute("""
                       UPDATE reservas
                       SET estado              = 'completada',
                           actualizado_por     = %s,
                           fecha_actualizacion = CURRENT_TIMESTAMP
                       WHERE id = %s
                       """, (session['username'], reserva_id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Asistencia registrada exitosamente', 'success')

    except Exception as e:
        flash(f'Error al registrar asistencia: {e}', 'danger')

    return redirect(url_for('reserva.listar'))


@asistencia_bp.route('/por_clase')
def por_clase():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT c.nombre                                                                 as clase,
                              COUNT(DISTINCT a.id)                                                     as total_asistencias,
                              COUNT(DISTINCT r.id)                                                     as total_reservas,
                              ROUND(COUNT(DISTINCT a.id) * 100.0 / NULLIF(COUNT(DISTINCT r.id), 0), 2) as porcentaje
                       FROM clases c
                                LEFT JOIN horarios h ON c.id = h.clase_id
                                LEFT JOIN reservas r ON h.id = r.horario_id AND r.estado IN ('confirmada', 'completada')
                                LEFT JOIN asistencias a ON r.id = a.reserva_id
                       WHERE c.activo = TRUE
                       GROUP BY c.id, c.nombre
                       ORDER BY porcentaje DESC
                       """)

        estadisticas = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template('asistencias_estadisticas.html', estadisticas=estadisticas)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('inicio'))


# =====================================================
# REGISTRAR ASISTENCIA USANDO PROCEDIMIENTO
# =====================================================
@asistencia_bp.route('/registrar_con_procedimiento/<int:reserva_id>')
def registrar_con_procedimiento(reserva_id):
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("CALL registrar_asistencia(%s)", (reserva_id,))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Asistencia registrada exitosamente (vía procedimiento almacenado)', 'success')

    except Exception as e:
        flash(f'Error al registrar asistencia: {e}', 'danger')

    return redirect(url_for('reserva.listar'))
