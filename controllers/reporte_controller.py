from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from database.conexion import conectar
from datetime import datetime
import io
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

reporte_bp = Blueprint('reporte', __name__, url_prefix='/reportes')


@reporte_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Total de miembros
        cursor.execute("SELECT COUNT(*) FROM miembros WHERE activo = TRUE")
        total_miembros = cursor.fetchone()[0]

        # Total de ingresos del mes actual
        cursor.execute("""
                       SELECT COALESCE(SUM(monto), 0)
                       FROM pagos
                       WHERE EXTRACT(MONTH FROM fecha_pago) = EXTRACT(MONTH FROM CURRENT_DATE)
                         AND estado = 'pagado'
                       """)
        ingresos_mes = cursor.fetchone()[0]

        # Clase más popular
        cursor.execute("""
                       SELECT c.nombre, COUNT(r.id) as total
                       FROM clases c
                                JOIN horarios h ON c.id = h.clase_id
                                JOIN reservas r ON h.id = r.horario_id
                       WHERE r.estado = 'confirmada'
                       GROUP BY c.id, c.nombre
                       ORDER BY total DESC LIMIT 1
                       """)
        clase_popular = cursor.fetchone()

        # Reservas hoy
        cursor.execute("""
                       SELECT COUNT(*)
                       FROM reservas
                       WHERE fecha_clase = CURRENT_DATE
                         AND estado = 'confirmada'
                       """)
        reservas_hoy = cursor.fetchone()[0]

        # Membresías por vencer (próximos 7 días)
        cursor.execute("""
                       SELECT COUNT(DISTINCT p.miembro_id)
                       FROM pagos p
                       WHERE p.fecha_vencimiento BETWEEN CURRENT_DATE AND CURRENT_DATE + 7
                         AND p.estado = 'pagado'
                       """)
        por_vencer = cursor.fetchone()[0]

        cursor.close()
        conexion.close()

        return render_template('reportes.html',
                               total_miembros=total_miembros,
                               ingresos_mes=float(ingresos_mes),
                               clase_popular=clase_popular[0] if clase_popular else 'N/A',
                               reservas_hoy=reservas_hoy,
                               por_vencer=por_vencer,
                               now=datetime.now())

    except Exception as e:
        flash(f'Error al cargar reportes: {e}', 'danger')
        return render_template('reportes.html',
                               total_miembros=0,
                               ingresos_mes=0,
                               clase_popular='N/A',
                               reservas_hoy=0,
                               por_vencer=0,
                               now=datetime.now())


@reporte_bp.route('/mensual', methods=['GET', 'POST'])
def reporte_mensual():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    anio = request.args.get('anio', datetime.now().year, type=int)
    mes = request.args.get('mes', datetime.now().month, type=int)

    if request.method == 'POST':
        anio = int(request.form['anio'])
        mes = int(request.form['mes'])
        return redirect(url_for('reporte.reporte_mensual', anio=anio, mes=mes))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Total de ingresos
        cursor.execute("""
                       SELECT COALESCE(SUM(monto), 0)
                       FROM pagos
                       WHERE EXTRACT(YEAR FROM fecha_pago) = %s
                         AND EXTRACT(MONTH FROM fecha_pago) = %s
                         AND estado = 'pagado'
                       """, (anio, mes))
        ingresos = cursor.fetchone()[0]

        # Total de transacciones
        cursor.execute("""
                       SELECT COUNT(*)
                       FROM pagos
                       WHERE EXTRACT(YEAR FROM fecha_pago) = %s
                         AND EXTRACT(MONTH FROM fecha_pago) = %s
                         AND estado = 'pagado'
                       """, (anio, mes))
        transacciones = cursor.fetchone()[0]

        # Miembros activos en el mes
        cursor.execute("""
                       SELECT COUNT(DISTINCT miembro_id)
                       FROM pagos
                       WHERE EXTRACT(YEAR FROM fecha_pago) = %s
                         AND EXTRACT(MONTH FROM fecha_pago) = %s
                         AND estado = 'pagado'
                       """, (anio, mes))
        miembros_activos = cursor.fetchone()[0]

        # Membresía más popular
        cursor.execute("""
                       SELECT me.tipo, COUNT(*) as total
                       FROM pagos p
                                JOIN membresias me ON p.membresia_id = me.id
                       WHERE EXTRACT(YEAR FROM p.fecha_pago) = %s
                         AND EXTRACT(MONTH FROM p.fecha_pago) = %s
                         AND p.estado = 'pagado'
                       GROUP BY me.tipo
                       ORDER BY total DESC LIMIT 1
                       """, (anio, mes))
        membresia_popular = cursor.fetchone()

        # Ticket promedio
        ticket_promedio = ingresos / transacciones if transacciones > 0 else 0

        cursor.close()
        conexion.close()

        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        reporte_data = [
            ('Período', f"{meses[mes - 1]} {anio}"),
            ('Total Ingresos', f"${ingresos:,.2f}"),
            ('Total Transacciones', str(transacciones)),
            ('Miembros Activos', str(miembros_activos)),
            ('Membresía Más Popular', membresia_popular[0] if membresia_popular else 'N/A'),
            ('Ticket Promedio', f"${ticket_promedio:,.2f}")
        ]

        return render_template('reporte_mensual.html',
                               reporte=reporte_data,
                               anio=anio,
                               mes=mes,
                               meses=meses)

    except Exception as e:
        flash(f'Error al generar reporte mensual: {e}', 'danger')
        return redirect(url_for('reporte.index'))


@reporte_bp.route('/pdf')
def generar_pdf():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Obtener datos para el PDF
        cursor.execute("""
                       SELECT m.nombre, m.apellido, m.email, me.tipo, p.monto, p.fecha_pago, p.fecha_vencimiento
                       FROM pagos p
                                JOIN miembros m ON p.miembro_id = m.id
                                JOIN membresias me ON p.membresia_id = me.id
                       WHERE p.estado = 'pagado'
                       ORDER BY p.fecha_pago DESC LIMIT 50
                       """)

        pagos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM miembros WHERE activo = TRUE")
        total_miembros = cursor.fetchone()[0]

        cursor.execute("""
                       SELECT COALESCE(SUM(monto), 0)
                       FROM pagos
                       WHERE EXTRACT(MONTH FROM fecha_pago) = EXTRACT(MONTH FROM CURRENT_DATE)
                       """)
        ingresos_mes = cursor.fetchone()[0]

        cursor.close()
        conexion.close()

        # Crear buffer para PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        # Estilo para título
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=30
        )

        elements = []

        # Título
        title = Paragraph("Reporte General del Gimnasio", title_style)
        elements.append(title)

        # Fecha
        fecha = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        elements.append(fecha)
        elements.append(Spacer(1, 20))

        # Resumen
        resumen_data = [
            ['Métrica', 'Valor'],
            ['Total Miembros Activos', str(total_miembros)],
            ['Ingresos del Mes', f"${ingresos_mes:,.2f}"]
        ]

        resumen_tabla = Table(resumen_data)
        resumen_tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(resumen_tabla)
        elements.append(Spacer(1, 20))

        # Tabla de pagos recientes
        if pagos:
            tabla_data = [['Miembro', 'Membresía', 'Monto', 'Fecha Pago', 'Vencimiento']]
            for p in pagos:
                tabla_data.append([
                    f"{p[0]} {p[1]}",
                    p[3],
                    f"${p[4]:,.2f}",
                    p[5].strftime('%d/%m/%Y') if p[5] else '-',
                    p[6].strftime('%d/%m/%Y') if p[6] else '-'
                ])

            tabla = Table(tabla_data)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements.append(tabla)

        doc.build(elements)
        buffer.seek(0)

        return send_file(buffer, as_attachment=True, download_name='reporte_gimnasio.pdf', mimetype='application/pdf')

    except Exception as e:
        flash(f'Error al generar PDF: {e}', 'danger')
        return redirect(url_for('reporte.index'))


@reporte_bp.route('/ingresos_pdf')
def ingresos_pdf():
    if 'user_id' not in session:
        return redirect(url_for('usuario.login'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT TO_CHAR(p.fecha_pago, 'YYYY-MM') as mes,
                              SUM(p.monto)                     as total
                       FROM pagos p
                       WHERE p.estado = 'pagado'
                       GROUP BY TO_CHAR(p.fecha_pago, 'YYYY-MM')
                       ORDER BY mes DESC LIMIT 12
                       """)

        ingresos = cursor.fetchall()
        cursor.close()
        conexion.close()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER,
                                     spaceAfter=30)

        elements = []
        elements.append(Paragraph("Reporte de Ingresos Mensuales", title_style))
        elements.append(Spacer(1, 20))

        if ingresos:
            data = [['Mes', 'Total Ingresos']]
            for i in ingresos:
                data.append([i[0], f"${i[1]:,.2f}"])

            tabla = Table(data)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(tabla)

        doc.build(elements)
        buffer.seek(0)

        return send_file(buffer, as_attachment=True, download_name='ingresos_mensuales.pdf', mimetype='application/pdf')

    except Exception as e:
        flash(f'Error al generar PDF de ingresos: {e}', 'danger')
        return redirect(url_for('reporte.index'))