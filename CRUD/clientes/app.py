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
    return redirect(url_for("clientes_list"))

# RUTA MODIFICADA: Ahora usa múltiples filtros
@app.route("/clientes")
def clientes_list():
    nombre = request.args.get("nombre", "").strip()
    email = request.args.get("email", "").strip()
    telefono = request.args.get("telefono", "").strip()
    direccion = request.args.get("direccion", "").strip()
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            criterios = []
            params = []
            if nombre:
                criterios.append("nombre ILIKE %s")
                params.append(f"%{nombre}%")
            if email:
                criterios.append("email ILIKE %s")
                params.append(f"%{email}%")
            if telefono:
                criterios.append("telefono ILIKE %s")
                params.append(f"%{telefono}%")
            if direccion:
                criterios.append("direccion ILIKE %s")
                params.append(f"%{direccion}%")
            if criterios:
                query = "SELECT * FROM cliente WHERE (" + " OR ".join(criterios) + ") ORDER BY id DESC"
            else:
                query = "SELECT * FROM cliente ORDER BY id DESC"
            cur.execute(query, params)
            clientes = cur.fetchall()
            
    # Pasamos todos los parámetros a la plantilla para que los campos del formulario mantengan su valor
    return render_template("clientes_list.html", clientes=clientes, **request.args)

# FORM CREAR
@app.route("/clientes/new", methods=["GET"])
def clientes_new_form():
    return render_template("clientes_form.html", cliente=None, action="create")

# CREAR
@app.route("/clientes/new", methods=["POST"])
def clientes_create():
    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()

    if not nombre or not email:
        flash("Nombre y Email son obligatorios.", "error")
        return redirect(url_for("clientes_new_form"))

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO cliente (nombre, email, telefono, direccion)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (nombre, email, telefono, direccion))
                _id = cur.fetchone()["id"]
                conn.commit()
        flash("Cliente creado correctamente.", "success")
        return redirect(url_for("clientes_list"))
    except Exception as e:
        flash(f"Error al crear: {e}", "error")
        return redirect(url_for("clientes_new_form"))

# FORM EDITAR
@app.route("/clientes/<int:cliente_id>/edit", methods=["GET"])
def clientes_edit_form(cliente_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cliente WHERE id = %s", (cliente_id,))
            cliente = cur.fetchone()
    if not cliente:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for("clientes_list"))
    return render_template("clientes_form.html", cliente=cliente, action="edit")

# EDITAR
@app.route("/clientes/<int:cliente_id>/edit", methods=["POST"])
def clientes_edit(cliente_id):
    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()

    if not nombre or not email:
        flash("Nombre y Email son obligatorios.", "error")
        return redirect(url_for("clientes_edit_form", cliente_id=cliente_id))

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE cliente
                    SET nombre=%s, email=%s, telefono=%s, direccion=%s
                    WHERE id=%s
                """, (nombre, email, telefono, direccion, cliente_id))
                conn.commit()
        flash("Cliente actualizado correctamente.", "success")
    except Exception as e:
        flash(f"Error al actualizar: {e}", "error")
    return redirect(url_for("clientes_list"))

# BORRAR
@app.route("/clientes/<int:cliente_id>/delete", methods=["POST"])
def clientes_delete(cliente_id):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM cliente WHERE id=%s", (cliente_id,))
                conn.commit()
        flash("Cliente eliminado.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {e}", "error")
    return redirect(url_for("clientes_list"))

# NUEVA RUTA PARA GENERAR EL REPORTE MULTICRITERIO
@app.route("/clientes/reporte")
def clientes_reporte():
    nombre = request.args.get("nombre", "").strip()
    email = request.args.get("email", "").strip()
    telefono = request.args.get("telefono", "").strip()
    direccion = request.args.get("direccion", "").strip()

    with get_conn() as conn:
        with conn.cursor() as cur:
            criterios = []
            params = []
            if nombre:
                criterios.append("nombre ILIKE %s")
                params.append(f"%{nombre}%")
            if email:
                criterios.append("email ILIKE %s")
                params.append(f"%{email}%")
            if telefono:
                criterios.append("telefono ILIKE %s")
                params.append(f"%{telefono}%")
            if direccion:
                criterios.append("direccion ILIKE %s")
                params.append(f"%{direccion}%")
            if criterios:
                query = "SELECT id, nombre, email, telefono, direccion FROM cliente WHERE (" + " OR ".join(criterios) + ") ORDER BY id DESC"
            else:
                query = "SELECT id, nombre, email, telefono, direccion FROM cliente ORDER BY id DESC"
            cur.execute(query, params)
            clientes = cur.fetchall()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    elements = []
    
    title = Paragraph("Reporte de Clientes", styles['h1'])
    elements.append(title)
    
    filtros_aplicados = [f"Nombre: {nombre}" if nombre else None, f"Email: {email}" if email else None, f"Teléfono: {telefono}" if telefono else None, f"Dirección: {direccion}" if direccion else None]
    filtros_aplicados = [f for f in filtros_aplicados if f]
    
    if filtros_aplicados:
        subtitle = Paragraph("Filtros Aplicados:<br/>" + "<br/>".join(filtros_aplicados), styles['Normal'])
        elements.append(subtitle)
    
    elements.append(Paragraph("<br/>", styles['Normal']))

    data = [["ID", "Nombre", "Email", "Teléfono", "Dirección"]]
    for cliente in clientes:
        data.append([str(cliente['id']), cliente['nombre'], cliente['email'], cliente['telefono'], cliente['direccion']])

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

    return Response(buffer.getvalue(), mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=reporte_clientes.pdf'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=bool(int(os.getenv("FLASK_DEBUG", "1"))))