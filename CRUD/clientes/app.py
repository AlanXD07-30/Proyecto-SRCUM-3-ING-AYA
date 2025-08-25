from flask import Flask, render_template, request, redirect, url_for, flash
import sys
import os

# Agrega la carpeta padre (CRUD/) al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_conn

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

@app.route("/")
def index():
    return redirect(url_for("clientes_list"))

# LISTAR
@app.route("/clientes")
def clientes_list():
    q = request.args.get("q", "").strip()
    with get_conn() as conn:
        with conn.cursor() as cur:
            if q:
                cur.execute("""
                    SELECT * FROM cliente
                    WHERE nombre ILIKE %s OR email ILIKE %s OR telefono ILIKE %s OR direccion ILIKE %s
                    ORDER BY id DESC
                """, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"))
            else:
                cur.execute("SELECT * FROM cliente ORDER BY id DESC")
            clientes = cur.fetchall()
    return render_template("clientes_list.html", clientes=clientes, q=q)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=bool(int(os.getenv("FLASK_DEBUG", "1"))))
