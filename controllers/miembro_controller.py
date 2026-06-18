from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.conexion import conectar

miembro_bp = Blueprint('miembro', __name__, url_prefix='/miembros')


@miembro_bp.route('/')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT id,
                              nombre,
                              apellido,
                              email,
                              telefono,
                              fecha_registro,
                              estado
                       FROM miembros
                       WHERE activo = TRUE
                       ORDER BY id DESC
                       """)

        miembros = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template('miembros.html', miembros=miembros)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('inicio'))


@miembro_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        telefono = request.form.get('telefono', '')
        direccion = request.form.get('direccion', '')
        fecha_nacimiento = request.form.get('fecha_nacimiento') or None

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           INSERT INTO miembros (nombre, apellido, email, telefono, direccion,
                                                 fecha_nacimiento, creado_por)
                           VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                           """, (nombre, apellido, email, telefono, direccion, fecha_nacimiento, session['username']))

            miembro_id = cursor.fetchone()[0]
            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Miembro registrado exitosamente', 'success')

            # Opcional: crear usuario automáticamente
            if request.form.get('crear_usuario') == 'on':
                try:
                    conexion2 = conectar()
                    cursor2 = conexion2.cursor()
                    username = email.split('@')[0]
                    # Contraseña temporal: cambiar en producción
                    cursor2.execute("""
                                    INSERT INTO usuarios (username, email, password_hash, rol, miembro_id, creado_por)
                                    VALUES (%s, %s, %s, 'socio', %s, %s)
                                    """, (username, email, 'temp123', miembro_id, session['username']))
                    conexion2.commit()
                    cursor2.close()
                    conexion2.close()
                    flash('Usuario socio creado automáticamente (contraseña: temp123)', 'info')
                except:
                    pass

            return redirect(url_for('miembro.listar'))

        except Exception as e:
            flash(f'Error al registrar miembro: {e}', 'danger')

    return render_template('miembro_form.html')


@miembro_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        telefono = request.form.get('telefono', '')
        direccion = request.form.get('direccion', '')
        fecha_nacimiento = request.form.get('fecha_nacimiento') or None
        estado = request.form['estado']

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                           UPDATE miembros
                           SET nombre              = %s,
                               apellido            = %s,
                               email               = %s,
                               telefono            = %s,
                               direccion           = %s,
                               fecha_nacimiento    = %s,
                               estado              = %s,
                               actualizado_por     = %s,
                               fecha_actualizacion = CURRENT_TIMESTAMP
                           WHERE id = %s
                           """, (nombre, apellido, email, telefono, direccion, fecha_nacimiento,
                                 estado, session['username'], id))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Miembro actualizado exitosamente', 'success')
            return redirect(url_for('miembro.listar'))

        except Exception as e:
            flash(f'Error al actualizar miembro: {e}', 'danger')

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM miembros WHERE id = %s", (id,))
        miembro = cursor.fetchone()
        cursor.close()
        conexion.close()

        return render_template('miembro_form.html', miembro=miembro)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('miembro.listar'))


@miembro_bp.route('/eliminar/<int:id>')
def eliminar(id):
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       UPDATE miembros
                       SET activo            = FALSE,
                           eliminado_por     = %s,
                           fecha_eliminacion = CURRENT_TIMESTAMP
                       WHERE id = %s
                       """, (session['username'], id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Miembro eliminado exitosamente', 'success')

    except Exception as e:
        flash(f'Error al eliminar miembro: {e}', 'danger')

    return redirect(url_for('miembro.listar'))


@miembro_bp.route('/ver/<int:id>')
def ver(id):
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT m.*,
                              (SELECT COUNT(*) FROM pagos WHERE miembro_id = m.id AND estado = 'pagado')   as total_pagos,
                              (SELECT SUM(monto)
                               FROM pagos
                               WHERE miembro_id = m.id
                                 AND estado = 'pagado')                                                    as total_gastado
                       FROM miembros m
                       WHERE m.id = %s
                         AND m.activo = TRUE
                       """, (id,))

        miembro = cursor.fetchone()
        cursor.close()
        conexion.close()

        return render_template('miembro_ver.html', miembro=miembro)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('miembro.listar'))


# =====================================================
# NUEVO MÉTODO: Registrar miembro completo usando PROCEDIMIENTO
# =====================================================
@miembro_bp.route('/registro_completo', methods=['GET', 'POST'])
def registro_completo():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    if request.method == 'POST':
        try:
            conexion = conectar()
            cursor = conexion.cursor()

            # Ejecutar el procedimiento almacenado
            cursor.execute("""
                CALL registrar_miembro_completo(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                request.form['nombre'],
                request.form['apellido'],
                request.form['email'],
                request.form.get('telefono', ''),
                request.form.get('direccion', ''),
                request.form.get('fecha_nacimiento') or None,
                request.form['username'],
                request.form['password'],
                int(request.form['membresia_id']),
                request.form.get('metodo_pago', 'efectivo')
            ))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('¡Miembro registrado exitosamente con todo el proceso completo!', 'success')
            return redirect(url_for('miembro.listar'))

        except Exception as e:
            flash(f'Error al registrar miembro: {e}', 'danger')

    # Obtener membresías para el select
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, tipo, precio FROM membresias WHERE activo = TRUE")
        membresias = cursor.fetchall()
        cursor.close()
        conexion.close()
    except:
        membresias = []

    return render_template('miembro_registro_completo.html', membresias=membresias)


# =====================================================
# NUEVO MÉTODO: Renovar membresía usando PROCEDIMIENTO
# =====================================================
@miembro_bp.route('/renovar_membresia/<int:miembro_id>', methods=['GET', 'POST'])
def renovar_membresia(miembro_id):
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    if request.method == 'POST':
        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                CALL renovar_membresia(%s, %s, %s, %s)
            """, (
                miembro_id,
                int(request.form['membresia_id']),
                request.form.get('metodo_pago', 'efectivo'),
                session['username']
            ))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('¡Membresía renovada exitosamente!', 'success')
            return redirect(url_for('miembro.listar'))

        except Exception as e:
            flash(f'Error al renovar membresía: {e}', 'danger')

    # Obtener datos del miembro y membresías disponibles
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT id, nombre, apellido FROM miembros WHERE id = %s", (miembro_id,))
        miembro = cursor.fetchone()

        cursor.execute("SELECT id, tipo, precio FROM membresias WHERE activo = TRUE")
        membresias = cursor.fetchall()

        cursor.close()
        conexion.close()
    except:
        miembro = None
        membresias = []

    return render_template('renovar_membresia.html', miembro=miembro, membresias=membresias)