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
    return redirect(url_for("inmuebles_list"))

# RUTA MODIFICADA: Ahora usa múltiples filtros
@app.route("/inmuebles")
def inmuebles_list():
    ubicacion = request.args.get("ubicacion", "").strip()
    area = request.args.get("area", "").strip()
    precio = request.args.get("precio", "").strip()
    estado = request.args.get("estado", "").strip()

    with get_conn() as conn:
        with conn.cursor() as cur:
            query = "SELECT * FROM inmueble WHERE 1=1"
            params = []
            
            if ubicacion:
                query += " AND ubicacion ILIKE %s"
                params.append(f"%{ubicacion}%")
            if area:
                query += " AND area = %s"
                params.append(area)
            if precio:
                query += " AND precio = %s"
                params.append(precio)
            if estado:
                query += " AND estado ILIKE %s"
                params.append(f"%{estado}%")
            
            query += " ORDER BY id DESC"
            
            cur.execute(query, params)
            inmuebles = cur.fetchall()
            
    return render_template("inmuebles_list.html", inmuebles=inmuebles, **request.args)

# FORM CREAR
@app.route("/inmuebles/new", methods=["GET"])
def inmuebles_new_form():
    return render_template("inmuebles_form.html", inmueble=None, action="create")

# CREAR
@app.route("/inmuebles/new", methods=["POST"])
def inmuebles_create():
    ubicacion = request.form.get("ubicacion", "").strip()
    area = request.form.get("area", "").strip()
    precio = request.form.get("precio", "").strip()
    estado = request.form.get("estado", "").strip()

    if not ubicacion or not precio:
        flash("Ubicación y Precio son obligatorios.", "error")
        return redirect(url_for("inmuebles_new_form"))

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO inmueble (ubicacion, area, precio, estado)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (ubicacion, area or None, precio, estado or None))
                _id = cur.fetchone()["id"]
                conn.commit()
        flash("Inmueble creado correctamente.", "success")
        return redirect(url_for("inmuebles_list"))
    except Exception as e:
        flash(f"Error al crear: {e}", "error")
        return redirect(url_for("inmuebles_new_form"))

# FORM EDITAR
@app.route("/inmuebles/<int:inmueble_id>/edit", methods=["GET"])
def inmuebles_edit_form(inmueble_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM inmueble WHERE id = %s", (inmueble_id,))
            inmueble = cur.fetchone()
    if not inmueble:
        flash("Inmueble no encontrado.", "error")
        return redirect(url_for("inmuebles_list"))
    return render_template("inmuebles_form.html", inmueble=inmueble, action="edit")

# EDITAR
@app.route("/inmuebles/<int:inmueble_id>/edit", methods=["POST"])
def inmuebles_edit(inmueble_id):
    ubicacion = request.form.get("ubicacion", "").strip()
    area = request.form.get("area", "").strip()
    precio = request.form.get("precio", "").strip()
    estado = request.form.get("estado", "").strip()

    if not ubicacion or not precio:
        flash("Ubicación y Precio son obligatorios.", "error")
        return redirect(url_for("inmuebles_edit_form", inmueble_id=inmueble_id))

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE inmueble
                    SET ubicacion=%s, area=%s, precio=%s, estado=%s
                    WHERE id=%s
                """, (ubicacion, area or None, precio, estado or None, inmueble_id))
                conn.commit()
        flash("Inmueble actualizado correctamente.", "success")
    except Exception as e:
        flash(f"Error al actualizar: {e}", "error")
    return redirect(url_for("inmuebles_list"))

# BORRAR
@app.route("/inmuebles/<int:inmueble_id>/delete", methods=["POST"])
def inmuebles_delete(inmueble_id):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM inmueble WHERE id=%s", (inmueble_id,))
                conn.commit()
        flash("Inmueble eliminado.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {e}", "error")
    return redirect(url_for("inmuebles_list"))

# NUEVA RUTA PARA GENERAR EL REPORTE MULTICRITERIO
@app.route("/inmuebles/reporte")
def inmuebles_reporte():
    ubicacion = request.args.get("ubicacion", "").strip()
    area = request.args.get("area", "").strip()
    precio = request.args.get("precio", "").strip()
    estado = request.args.get("estado", "").strip()

    with get_conn() as conn:
        with conn.cursor() as cur:
            query = "SELECT id, ubicacion, area, precio, estado FROM inmueble WHERE 1=1"
            params = []
            
            if ubicacion:
                query += " AND ubicacion ILIKE %s"
                params.append(f"%{ubicacion}%")
            if area:
                query += " AND area = %s"
                params.append(area)
            if precio:
                query += " AND precio = %s"
                params.append(precio)
            if estado:
                query += " AND estado ILIKE %s"
                params.append(f"%{estado}%")
            
            query += " ORDER BY id DESC"
            
            cur.execute(query, params)
            inmuebles = cur.fetchall()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    elements = []
    
    title = Paragraph("Reporte de Inmuebles", styles['h1'])
    elements.append(title)
    
    filtros_aplicados = [f"Ubicación: {ubicacion}" if ubicacion else None, f"Área: {area}" if area else None, f"Precio: {precio}" if precio else None, f"Estado: {estado}" if estado else None]
    filtros_aplicados = [f for f in filtros_aplicados if f]
    
    if filtros_aplicados:
        subtitle = Paragraph("Filtros Aplicados:<br/>" + "<br/>".join(filtros_aplicados), styles['Normal'])
        elements.append(subtitle)
    
    elements.append(Paragraph("<br/>", styles['Normal']))

    data = [["ID", "Ubicación", "Área", "Precio", "Estado"]]
    for inmueble in inmuebles:
        data.append([str(inmueble['id']), inmueble['ubicacion'], str(inmueble['area']), str(inmueble['precio']), inmueble['estado']])

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

    return Response(buffer.getvalue(), mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=reporte_inmuebles.pdf'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=bool(int(os.getenv("FLASK_DEBUG", "1"))))