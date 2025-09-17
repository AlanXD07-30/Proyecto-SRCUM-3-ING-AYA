from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sys
import os
from io import BytesIO

# Agrega la carpeta padre (CRUD/) al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_conn

from dotenv import load_dotenv
import os

# Importaciones para la generación de PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

@app.route("/")
def index():
    return redirect(url_for("citas_list"))

# RUTA MODIFICADA: Ahora usa múltiples filtros
@app.route("/citas")
def citas_list():
    cliente_nombre = request.args.get("cliente_nombre", "").strip()
    inmueble_ubicacion = request.args.get("inmueble_ubicacion", "").strip()
    fecha = request.args.get("fecha", "").strip()
    estado = request.args.get("estado", "").strip()

    with get_conn() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT c.id, c.fecha, c.hora, c.estado, cl.nombre AS cliente_nombre, i.ubicacion AS inmueble_ubicacion
                FROM cita c
                JOIN cliente cl ON c.cliente = cl.id
                JOIN inmueble i ON c.inmueble = i.id
                WHERE 1=1
            """
            params = []

            if cliente_nombre:
                query += " AND cl.nombre ILIKE %s"
                params.append(f"%{cliente_nombre}%")
            if inmueble_ubicacion:
                query += " AND i.ubicacion ILIKE %s"
                params.append(f"%{inmueble_ubicacion}%")
            if fecha:
                query += " AND c.fecha = %s"
                params.append(fecha)
            if estado:
                query += " AND c.estado ILIKE %s"
                params.append(f"%{estado}%")

            query += " ORDER BY c.id DESC"

            cur.execute(query, params)
            citas = cur.fetchall()
            
    return render_template("citas_list.html", citas=citas, **request.args)

@app.route("/citas/new", methods=["GET"])
def citas_new_form():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre FROM cliente")
            clientes = cur.fetchall()
            cur.execute("SELECT id, ubicacion FROM inmueble")
            inmuebles = cur.fetchall()
    return render_template("citas_form.html", cita=None, action="create", clientes=clientes, inmuebles=inmuebles)

@app.route("/citas/new", methods=["POST"])
def citas_create():
    cliente = request.form.get("cliente")
    inmueble = request.form.get("inmueble")
    fecha = request.form.get("fecha")
    hora = request.form.get("hora")
    estado = request.form.get("estado", "").strip()

    if not cliente or not inmueble or not fecha or not hora:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for("citas_new_form"))

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO cita (cliente, inmueble, fecha, hora, estado)
                    VALUES (%s, %s, %s, %s, %s)
                """, (cliente, inmueble, fecha, hora, estado))
                conn.commit()
        flash("Cita creada correctamente.", "success")
        return redirect(url_for("citas_list"))
    except Exception as e:
        flash(f"Error al crear: {e}", "error")
        return redirect(url_for("citas_new_form"))

@app.route("/citas/<int:cita_id>/edit", methods=["GET"])
def citas_edit_form(cita_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cita WHERE id=%s", (cita_id,))
            cita = cur.fetchone()
            cur.execute("SELECT id, nombre FROM cliente")
            clientes = cur.fetchall()
            cur.execute("SELECT id, ubicacion FROM inmueble")
            inmuebles = cur.fetchall()
    return render_template("citas_form.html", cita=cita, action="edit", clientes=clientes, inmuebles=inmuebles)

@app.route("/citas/<int:cita_id>/edit", methods=["POST"])
def citas_edit(cita_id):
    cliente = request.form.get("cliente")
    inmueble = request.form.get("inmueble")
    fecha = request.form.get("fecha")
    hora = request.form.get("hora")
    estado = request.form.get("estado", "").strip()

    if not cliente or not inmueble or not fecha or not hora:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for("citas_edit_form", cita_id=cita_id))

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE cita SET cliente=%s, inmueble=%s, fecha=%s, hora=%s, estado=%s
                    WHERE id=%s
                """, (cliente, inmueble, fecha, hora, estado, cita_id))
                conn.commit()
        flash("Cita actualizada correctamente.", "success")
    except Exception as e:
        flash(f"Error al actualizar: {e}", "error")
    return redirect(url_for("citas_list"))

@app.route("/citas/<int:cita_id>/delete", methods=["POST"])
def citas_delete(cita_id):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM cita WHERE id=%s", (cita_id,))
                conn.commit()
        flash("Cita eliminada.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {e}", "error")
    return redirect(url_for("citas_list"))

# NUEVA RUTA PARA GENERAR EL REPORTE MULTICRITERIO
@app.route("/citas/reporte")
def citas_reporte():
    cliente_nombre = request.args.get("cliente_nombre", "").strip()
    inmueble_ubicacion = request.args.get("inmueble_ubicacion", "").strip()
    fecha = request.args.get("fecha", "").strip()
    estado = request.args.get("estado", "").strip()

    with get_conn() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT c.id, c.fecha, c.hora, c.estado, cl.nombre AS cliente_nombre, i.ubicacion AS inmueble_ubicacion
                FROM cita c
                JOIN cliente cl ON c.cliente = cl.id
                JOIN inmueble i ON c.inmueble = i.id
                WHERE 1=1
            """
            params = []

            if cliente_nombre:
                query += " AND cl.nombre ILIKE %s"
                params.append(f"%{cliente_nombre}%")
            if inmueble_ubicacion:
                query += " AND i.ubicacion ILIKE %s"
                params.append(f"%{inmueble_ubicacion}%")
            if fecha:
                query += " AND c.fecha = %s"
                params.append(fecha)
            if estado:
                query += " AND c.estado ILIKE %s"
                params.append(f"%{estado}%")
            
            query += " ORDER BY c.id DESC"
            
            cur.execute(query, params)
            citas = cur.fetchall()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    elements = []
    
    title = Paragraph("Reporte de Citas", styles['h1'])
    elements.append(title)
    
    filtros_aplicados = [f"Cliente: {cliente_nombre}" if cliente_nombre else None, f"Inmueble: {inmueble_ubicacion}" if inmueble_ubicacion else None, f"Fecha: {fecha}" if fecha else None, f"Estado: {estado}" if estado else None]
    filtros_aplicados = [f for f in filtros_aplicados if f]
    
    if filtros_aplicados:
        subtitle = Paragraph("Filtros Aplicados:<br/>" + "<br/>".join(filtros_aplicados), styles['Normal'])
        elements.append(subtitle)
    
    elements.append(Paragraph("<br/>", styles['Normal']))

    data = [["ID", "Cliente", "Inmueble", "Fecha", "Hora", "Estado"]]
    for cita in citas:
        data.append([str(cita['id']), cita['cliente_nombre'], cita['inmueble_ubicacion'], str(cita['fecha']), str(cita['hora']), cita['estado']])

    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return Response(buffer.getvalue(), mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=reporte_citas.pdf'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=bool(int(os.getenv("FLASK_DEBUG", "1"))))