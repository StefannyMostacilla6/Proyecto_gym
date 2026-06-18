from flask import make_response, session, flash
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from database.conexion import conectar
from datetime import datetime


def generar_reporte_miembros_pdf():
    """Genera reporte PDF de todos los miembros activos"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Reporte de Miembros")

    # Obtener datos
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT id,
                              nombre,
                              apellido,
                              email,
                              telefono,
                              TO_CHAR(fecha_registro, 'DD/MM/YYYY') as fecha_registro,
                              estado
                       FROM miembros
                       WHERE activo = TRUE
                       ORDER BY id
                       """)

        miembros = cursor.fetchall()
        cursor.close()
        conexion.close()
    except Exception as e:
        miembros = []
        print(f"Error al obtener miembros: {e}")

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=30
    )

    # Elementos del PDF
    elements = []

    # Título
    title = Paragraph("REPORTE DE MIEMBROS DEL GIMNASIO", title_style)
    elements.append(title)

    # Fecha
    fecha = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal'])
    elements.append(fecha)
    elements.append(Spacer(1, 20))

    # Tabla de datos
    if miembros and len(miembros) > 0:
        # Encabezados
        data = [["ID", "Nombre", "Apellido", "Email", "Teléfono", "Registro", "Estado"]]

        for m in miembros:
            data.append([
                str(m[0]),
                m[1],
                m[2],
                m[3],
                m[4] or '-',
                m[5] if m[5] else '-',
                m[6] if m[6] else 'activo'
            ])

        # Crear tabla
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(table)

        # Totales
        elements.append(Spacer(1, 20))
        total = Paragraph(f"<b>Total de miembros activos: {len(miembros)}</b>", styles['Normal'])
        elements.append(total)
    else:
        no_data = Paragraph("No hay miembros registrados actualmente.", styles['Normal'])
        elements.append(no_data)

    # Construir PDF
    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_miembros.pdf'

    return response


def generar_reporte_ingresos_pdf():
    """Genera reporte PDF de ingresos por membresía"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), title="Reporte de Ingresos")

    # Obtener datos
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT me.tipo                          as membresia_tipo,
                              EXTRACT(YEAR FROM p.fecha_pago)  as año,
                              EXTRACT(MONTH FROM p.fecha_pago) as mes,
                              COUNT(p.id)                      as cantidad_pagos,
                              SUM(p.monto)                     as total_ingresos
                       FROM pagos p
                                JOIN membresias me ON p.membresia_id = me.id
                       WHERE p.estado = 'pagado'
                         AND p.activo = TRUE
                       GROUP BY me.tipo, EXTRACT(YEAR FROM p.fecha_pago), EXTRACT(MONTH FROM p.fecha_pago)
                       ORDER BY año DESC, mes DESC LIMIT 50
                       """)

        ingresos = cursor.fetchall()
        cursor.close()
        conexion.close()
    except Exception as e:
        ingresos = []
        print(f"Error al obtener ingresos: {e}")

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=30
    )

    elements = []

    # Título
    title = Paragraph("REPORTE DE INGRESOS DEL GIMNASIO", title_style)
    elements.append(title)

    fecha = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal'])
    elements.append(fecha)
    elements.append(Spacer(1, 20))

    if ingresos and len(ingresos) > 0:
        # Función para convertir número de mes a nombre
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        data = [["Membresía", "Año", "Mes", "Cantidad Pagos", "Total Ingresos"]]
        total_global = 0

        for i in ingresos:
            mes_num = int(i[2]) if i[2] else 1
            mes_nombre = meses[mes_num - 1] if 1 <= mes_num <= 12 else '-'
            total = float(i[4]) if i[4] else 0
            total_global += total

            data.append([
                i[0],
                str(int(i[1])) if i[1] else '-',
                mes_nombre,
                str(int(i[3])) if i[3] else '0',
                f"${total:,.2f}"
            ])

        # Agregar fila de total
        data.append(["", "", "", "TOTAL GENERAL", f"${total_global:,.2f}"])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-2, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('GRID', (0, -1), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
        ]))
        elements.append(table)
    else:
        no_data = Paragraph("No hay registros de ingresos disponibles.", styles['Normal'])
        elements.append(no_data)

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_ingresos.pdf'

    return response


def generar_reporte_clases_pdf():
    """Genera reporte PDF de estadísticas de clases"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Reporte de Clases")

    # Obtener datos
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
                       SELECT c.nombre             as clase,
                              c.cupo_maximo,
                              c.duracion_minutos,
                              COUNT(DISTINCT h.id) as total_horarios,
                              COUNT(DISTINCT r.id) as total_reservas
                       FROM clases c
                                LEFT JOIN horarios h ON c.id = h.clase_id AND h.activo = TRUE
                                LEFT JOIN reservas r ON h.id = r.horario_id AND r.estado IN ('confirmada', 'completada')
                       WHERE c.activo = TRUE
                       GROUP BY c.id, c.nombre, c.cupo_maximo, c.duracion_minutos
                       ORDER BY total_reservas DESC
                       """)

        clases = cursor.fetchall()
        cursor.close()
        conexion.close()
    except Exception as e:
        clases = []
        print(f"Error al obtener clases: {e}")

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=30
    )

    elements = []

    # Título
    title = Paragraph("REPORTE DE CLASES DEL GIMNASIO", title_style)
    elements.append(title)

    fecha = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal'])
    elements.append(fecha)
    elements.append(Spacer(1, 20))

    if clases and len(clases) > 0:
        data = [["Clase", "Cupo Máximo", "Duración (min)", "Horarios", "Reservas Totales"]]

        for c in clases:
            data.append([
                c[0],
                str(c[1]) if c[1] else 'N/A',
                str(c[2]) if c[2] else '60',
                str(int(c[3])) if c[3] else '0',
                str(int(c[4])) if c[4] else '0'
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(table)

        elements.append(Spacer(1, 20))
        total = Paragraph(f"<b>Total de clases activas: {len(clases)}</b>", styles['Normal'])
        elements.append(total)
    else:
        no_data = Paragraph("No hay clases registradas actualmente.", styles['Normal'])
        elements.append(no_data)

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_clases.pdf'

    return response