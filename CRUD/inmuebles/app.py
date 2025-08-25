from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_conn
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

@app.route("/")
def index():
    return redirect(url_for("inmuebles_list"))

# LISTAR
@app.route("/inmuebles")
def inmuebles_list():
    q = request.args.get("q", "").strip()
    with get_conn() as conn:
        with conn.cursor() as cur:
            if q:
                cur.execute("""
                    SELECT * FROM inmueble
                    WHERE ubicacion ILIKE %s OR estado ILIKE %s
                    ORDER BY id DESC
                """, (f"%{q}%", f"%{q}%"))
            else:
                cur.execute("SELECT * FROM inmueble ORDER BY id DESC")
            inmuebles = cur.fetchall()
    return render_template("inmuebles_list.html", inmuebles=inmuebles, q=q)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=bool(int(os.getenv("FLASK_DEBUG", "1"))))
