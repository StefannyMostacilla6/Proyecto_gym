from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from database.conexion import conectar
from datetime import datetime

auditoria_bp = Blueprint('auditoria', __name__, url_prefix='/auditoria')


@auditoria_bp.route('/')
def index():
    """Página principal de auditoría con resumen"""
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado. Solo administradores.', 'danger')
        return redirect(url_for('inicio'))

    return render_template('auditoria_index.html')


# =====================================================
# AUDITORÍA DE MIEMBROS
# =====================================================
@auditoria_bp.route('/miembros')
def auditoria_miembros():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Ver todos los miembros incluyendo campos de auditoría
        cursor.execute("""
                       SELECT id,
                              nombre,
                              apellido,
                              email,
                              telefono,
                              direccion,
                              fecha_nacimiento,
                              fecha_registro,
                              estado,
                              activo,
                              creado_por,
                              fecha_creacion,
                              actualizado_por,
                              fecha_actualizacion,
                              eliminado_por,
                              fecha_eliminacion
                       FROM miembros
                       ORDER BY id DESC
                       """)

        miembros = cursor.fetchall()

        # Obtener columnas para mostrar
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=miembros,
                               columnas=columnas,
                               titulo="Auditoría de Miembros",
                               tabla="miembros")

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))


# =====================================================
# AUDITORÍA DE USUARIOS
# =====================================================
@auditoria_bp.route('/usuarios')
def auditoria_usuarios():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT u.id,
                              u.username,
                              u.email,
                              u.rol,
                              u.miembro_id,
                              m.nombre || ' ' || m.apellido as miembro_nombre,
                              u.activo,
                              u.creado_por,
                              u.fecha_creacion,
                              u.actualizado_por,
                              u.fecha_actualizacion,
                              u.eliminado_por,
                              u.fecha_eliminacion
                       FROM usuarios u
                                LEFT JOIN miembros m ON u.miembro_id = m.id
                       ORDER BY u.id DESC
                       """)

        datos = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=datos,
                               columnas=columnas,
                               titulo="Auditoría de Usuarios",
                               tabla="usuarios")

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))


# =====================================================
# AUDITORÍA DE MEMBRESÍAS
# =====================================================
@auditoria_bp.route('/membresias')
def auditoria_membresias():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

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
                              activo,
                              creado_por,
                              fecha_creacion,
                              actualizado_por,
                              fecha_actualizacion,
                              eliminado_por,
                              fecha_eliminacion
                       FROM membresias
                       ORDER BY id DESC
                       """)

        datos = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=datos,
                               columnas=columnas,
                               titulo="Auditoría de Membresías",
                               tabla="membresias")

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))


# =====================================================
# AUDITORÍA DE PAGOS
# =====================================================
@auditoria_bp.route('/pagos')
def auditoria_pagos():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT p.id,
                              p.miembro_id,
                              m.nombre || ' ' || m.apellido as miembro_nombre,
                              p.membresia_id,
                              me.tipo                       as membresia_tipo,
                              p.monto,
                              p.fecha_pago,
                              p.fecha_vencimiento,
                              p.metodo_pago,
                              p.comprobante,
                              p.estado,
                              p.activo,
                              p.creado_por,
                              p.fecha_creacion,
                              p.actualizado_por,
                              p.fecha_actualizacion,
                              p.eliminado_por,
                              p.fecha_eliminacion
                       FROM pagos p
                                LEFT JOIN miembros m ON p.miembro_id = m.id
                                LEFT JOIN membresias me ON p.membresia_id = me.id
                       ORDER BY p.id DESC
                       """)

        datos = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=datos,
                               columnas=columnas,
                               titulo="Auditoría de Pagos",
                               tabla="pagos")

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))


# =====================================================
# AUDITORÍA DE ENTRENADORES
# =====================================================
@auditoria_bp.route('/entrenadores')
def auditoria_entrenadores():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT id,
                              nombre,
                              apellido,
                              especialidad,
                              email,
                              telefono,
                              activo,
                              creado_por,
                              fecha_creacion,
                              actualizado_por,
                              fecha_actualizacion,
                              eliminado_por,
                              fecha_eliminacion
                       FROM entrenadores
                       ORDER BY id DESC
                       """)

        datos = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=datos,
                               columnas=columnas,
                               titulo="Auditoría de Entrenadores",
                               tabla="entrenadores")

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))


# =====================================================
# AUDITORÍA DE CLASES
# =====================================================
@auditoria_bp.route('/clases')
def auditoria_clases():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT id,
                              nombre,
                              descripcion,
                              cupo_maximo,
                              duracion_minutos,
                              activo,
                              creado_por,
                              fecha_creacion,
                              actualizado_por,
                              fecha_actualizacion,
                              eliminado_por,
                              fecha_eliminacion
                       FROM clases
                       ORDER BY id DESC
                       """)

        datos = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=datos,
                               columnas=columnas,
                               titulo="Auditoría de Clases",
                               tabla="clases")

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))


# =====================================================
# AUDITORÍA DE HORARIOS
# =====================================================
@auditoria_bp.route('/horarios')
def auditoria_horarios():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT h.id,
                              h.clase_id,
                              c.nombre                      as clase_nombre,
                              h.entrenador_id,
                              e.nombre || ' ' || e.apellido as entrenador_nombre,
                              h.dia_semana,
                              h.hora_inicio,
                              h.hora_fin,
                              h.sala,
                              h.activo,
                              h.creado_por,
                              h.fecha_creacion,
                              h.actualizado_por,
                              h.fecha_actualizacion,
                              h.eliminado_por,
                              h.fecha_eliminacion
                       FROM horarios h
                                LEFT JOIN clases c ON h.clase_id = c.id
                                LEFT JOIN entrenadores e ON h.entrenador_id = e.id
                       ORDER BY h.id DESC
                       """)

        datos = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=datos,
                               columnas=columnas,
                               titulo="Auditoría de Horarios",
                               tabla="horarios")

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))


# =====================================================
# AUDITORÍA DE RESERVAS
# =====================================================
@auditoria_bp.route('/reservas')
def auditoria_reservas():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT r.id,
                              r.miembro_id,
                              m.nombre || ' ' || m.apellido as miembro_nombre,
                              r.horario_id,
                              c.nombre                      as clase_nombre,
                              r.fecha_reserva,
                              r.fecha_clase,
                              r.estado,
                              r.activo,
                              r.creado_por,
                              r.fecha_creacion,
                              r.actualizado_por,
                              r.fecha_actualizacion,
                              r.eliminado_por,
                              r.fecha_eliminacion
                       FROM reservas r
                                LEFT JOIN miembros m ON r.miembro_id = m.id
                                LEFT JOIN horarios h ON r.horario_id = h.id
                                LEFT JOIN clases c ON h.clase_id = c.id
                       ORDER BY r.id DESC
                       """)

        datos = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=datos,
                               columnas=columnas,
                               titulo="Auditoría de Reservas",
                               tabla="reservas")

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))


# =====================================================
# AUDITORÍA DE ASISTENCIAS
# =====================================================
@auditoria_bp.route('/asistencias')
def auditoria_asistencias():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT a.id,
                              a.reserva_id,
                              m.nombre || ' ' || m.apellido as miembro_nombre,
                              c.nombre                      as clase_nombre,
                              a.fecha_checkin,
                              a.activo,
                              a.creado_por,
                              a.fecha_creacion,
                              a.actualizado_por,
                              a.fecha_actualizacion,
                              a.eliminado_por,
                              a.fecha_eliminacion
                       FROM asistencias a
                                LEFT JOIN reservas r ON a.reserva_id = r.id
                                LEFT JOIN miembros m ON r.miembro_id = m.id
                                LEFT JOIN horarios h ON r.horario_id = h.id
                                LEFT JOIN clases c ON h.clase_id = c.id
                       ORDER BY a.id DESC
                       """)

        datos = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=datos,
                               columnas=columnas,
                               titulo="Auditoría de Asistencias",
                               tabla="asistencias")

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))


# =====================================================
# AUDITORÍA DE CAMBIOS (Tabla especial de auditoría)
# =====================================================
@auditoria_bp.route('/cambios')
def auditoria_cambios():
    if 'user_id' not in session or session.get('rol') != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('inicio'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT id,
                              miembro_id,
                              nombre_completo,
                              email,
                              accion,
                              realizado_por,
                              fecha_accion,
                              datos_previos,
                              ip_origen
                       FROM auditoria_miembros
                       ORDER BY fecha_accion DESC LIMIT 200
                       """)

        datos = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        cursor.close()
        conexion.close()

        return render_template('auditoria_tabla.html',
                               datos=datos,
                               columnas=columnas,
                               titulo="Auditoría de Cambios - Registro de Eliminaciones",
                               tabla="auditoria_miembros",
                               es_auditoria=True)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('auditoria.index'))