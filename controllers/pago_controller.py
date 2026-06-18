from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.conexion import conectar
from datetime import datetime, timedelta

pago_bp = Blueprint('pago', __name__, url_prefix='/pagos')


@pago_bp.route('/')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT p.id,
                              m.nombre || ' ' || m.apellido as miembro,
                              me.tipo                       as membresia,
                              p.monto,
                              p.fecha_pago,
                              p.fecha_vencimiento,
                              p.metodo_pago,
                              p.estado
                       FROM pagos p
                                JOIN miembros m ON p.miembro_id = m.id
                                JOIN membresias me ON p.membresia_id = me.id
                       WHERE p.activo = TRUE
                       ORDER BY p.fecha_pago DESC
                       """)

        pagos = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template('pagos.html', pagos=pagos)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('inicio'))


@pago_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    if request.method == 'POST':
        miembro_id = int(request.form['miembro_id'])
        membresia_id = int(request.form['membresia_id'])
        metodo_pago = request.form['metodo_pago']

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            # Obtener precio y duración de la membresía
            cursor.execute("SELECT precio, duracion_dias FROM membresias WHERE id = %s", (membresia_id,))
            membresia = cursor.fetchone()
            precio = membresia[0]
            duracion_dias = membresia[1]

            fecha_vencimiento = datetime.now().date() + timedelta(days=duracion_dias)

            cursor.execute("""
                           INSERT INTO pagos (miembro_id, membresia_id, monto, fecha_vencimiento,
                                              metodo_pago, creado_por)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           """, (miembro_id, membresia_id, precio, fecha_vencimiento, metodo_pago, session['username']))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash('Pago registrado exitosamente', 'success')
            return redirect(url_for('pago.listar'))

        except Exception as e:
            flash(f'Error al registrar pago: {e}', 'danger')

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT id, nombre || ' ' || apellido as nombre FROM miembros WHERE activo = TRUE")
        miembros = cursor.fetchall()

        cursor.execute("SELECT id, tipo, precio FROM membresias WHERE activo = TRUE")
        membresias = cursor.fetchall()

        cursor.close()
        conexion.close()

        return render_template('pago_form.html', miembros=miembros, membresias=membresias)

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('inicio'))


@pago_bp.route('/anular/<int:id>')
def anular(id):
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       UPDATE pagos
                       SET estado              = 'anulado',
                           activo              = FALSE,
                           actualizado_por     = %s,
                           fecha_actualizacion = CURRENT_TIMESTAMP
                       WHERE id = %s
                       """, (session['username'], id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Pago anulado exitosamente', 'success')

    except Exception as e:
        flash(f'Error al anular pago: {e}', 'danger')

    return redirect(url_for('pago.listar'))