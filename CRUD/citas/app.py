from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_conn
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

@app.route("/")
def index():
    return redirect(url_for("citas_list"))

@app.route("/citas")
def citas_list():
    q = request.args.get("q", "").strip()
    with get_conn() as conn:
        with conn.cursor() as cur:
            if q:
                cur.execute("""
                    SELECT c.id, c.fecha, c.hora, c.estado, cl.nombre AS cliente_nombre, i.ubicacion AS inmueble_ubicacion
                    FROM cita c
                    JOIN cliente cl ON c.cliente = cl.id
                    JOIN inmueble i ON c.inmueble = i.id
                    WHERE cl.nombre ILIKE %s OR i.ubicacion ILIKE %s OR c.estado ILIKE %s
                    ORDER BY c.id DESC
                """, (f"%{q}%", f"%{q}%", f"%{q}%"))
            else:
                cur.execute("""
                    SELECT c.id, c.fecha, c.hora, c.estado, cl.nombre AS cliente_nombre, i.ubicacion AS inmueble_ubicacion
                    FROM cita c
                    JOIN cliente cl ON c.cliente = cl.id
                    JOIN inmueble i ON c.inmueble = i.id
                    ORDER BY c.id DESC
                """)
            citas = cur.fetchall()
    return render_template("citas_list.html", citas=citas, q=q)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=bool(int(os.getenv("FLASK_DEBUG", "1"))))
