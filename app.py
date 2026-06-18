from flask import Flask, render_template, session, redirect, url_for  # ✅ Agregar redirect y url_for
from database.conexion import conectar
import traceback

# Importar blueprints
from controllers.usuario_controller import usuario_bp
from controllers.miembro_controller import miembro_bp
from controllers.membresia_controller import membresia_bp
from controllers.pago_controller import pago_bp
from controllers.entrenador_controller import entrenador_bp
from controllers.clase_controller import clase_bp
from controllers.horario_controller import horario_bp
from controllers.reserva_controller import reserva_bp
from controllers.asistencia_controller import asistencia_bp
from controllers.reporte_controller import reporte_bp
from controllers.auditoria_controller import auditoria_bp

app = Flask(__name__)
app.secret_key = "gym2026"
app.debug = True

# Registrar blueprints
app.register_blueprint(usuario_bp)
app.register_blueprint(miembro_bp)
app.register_blueprint(membresia_bp)
app.register_blueprint(pago_bp)
app.register_blueprint(entrenador_bp)
app.register_blueprint(clase_bp)
app.register_blueprint(horario_bp)
app.register_blueprint(reserva_bp)
app.register_blueprint(asistencia_bp)
app.register_blueprint(reporte_bp)
# app.py - Agregar esta línea con los otros imports


# Registrar blueprint
app.register_blueprint(auditoria_bp)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('inicio'))
    return redirect(url_for('usuario.login'))


@app.route('/inicio')
def inicio():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT COUNT(*) FROM miembros WHERE activo = TRUE")
        total_miembros = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM clases WHERE activo = TRUE")
        total_clases = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reservas WHERE fecha_clase = CURRENT_DATE AND estado = 'confirmada'")
        reservas_hoy = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COALESCE(SUM(monto), 0) FROM pagos WHERE EXTRACT(MONTH FROM fecha_pago) = EXTRACT(MONTH FROM CURRENT_DATE) AND estado = 'pagado'")
        ingresos_mes = cursor.fetchone()[0]

        cursor.close()
        conexion.close()

        return render_template('inicio.html',
                               total_miembros=total_miembros,
                               total_clases=total_clases,
                               reservas_hoy=reservas_hoy,
                               ingresos_mes=float(ingresos_mes))
    except Exception as e:
        error_msg = f"Error en inicio: {str(e)}\n\n{traceback.format_exc()}"
        return f"<pre>{error_msg}</pre>", 500


if __name__ == '__main__':
    app.run(debug=True)