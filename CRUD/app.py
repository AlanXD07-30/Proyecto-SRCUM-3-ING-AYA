# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, session 
import psycopg2
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/logout')
def logout():
    return redirect("http://127.0.0.1:5500/PAGINA%20PRINCIPAL%20INMUEBLES%20ING%20AYA/Index.html")

# ---------------- Rutas paneles existentes ----------------
@app.route("/admin")
def admin():
    return render_template("panel administrador.html")

@app.route("/empleado")
def empleado():
    return render_template("panel empleado.html")

@app.route("/secretaria")
def secretaria():
    return render_template("panel secretaria.html")

# ---------------- Conexión PostgreSQL ----------------
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="ingaya",
        user="postgres",
        password="123456789"
    )
    return conn

# ---------------- GESTIÓN DE USUARIOS ----------------
@app.route("/admin/usuarios", methods=["GET"])
def admin_usuarios():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id_usuario, u.email, u.estado, u.fecha_creacion, array_agg(r.nombre_rol) AS roles
        FROM USUARIO u
        LEFT JOIN USUARIO_ROL ur ON u.id_usuario = ur.id_usuario
        LEFT JOIN ROL r ON ur.id_rol = r.id_rol
        GROUP BY u.id_usuario
        ORDER BY u.id_usuario
    """)
    usuarios = []
    for row in cur.fetchall():
        # row[4] viene de array_agg, puede ser None o [None]
        roles_arr = row[4] if row[4] is not None else []
        if isinstance(roles_arr, (list, tuple)) and len(roles_arr) > 0 and roles_arr[0] is None:
            roles_arr = []
        usuarios.append({
            "id_usuario": row[0],
            "email": row[1],
            "estado": row[2],
            "fecha_creacion": row[3],
            "roles": roles_arr
        })
    cur.close()
    conn.close()
    return render_template("AdminOpciones/Gestion_Usuarios.html", usuarios=usuarios)

# ---------------- AGREGAR USUARIO ----------------
@app.route("/admin/usuarios/agregar", methods=["POST"])
def agregar_usuario():
    email = request.form.get("email")
    contrasena = request.form.get("contrasena")
    rol = request.form.get("rol")  # Solo "Empleado" o "Secretaria"

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Insertar en USUARIO
    cur.execute("INSERT INTO USUARIO (email, contrasena) VALUES (%s, %s) RETURNING id_usuario",
                (email, contrasena))
    id_usuario_row = cur.fetchone()
    id_usuario = id_usuario_row[0] if id_usuario_row else None
    if id_usuario is None:
        conn.rollback()
        cur.close()
        conn.close()
        return "Error al crear usuario", 500

    # Obtener id del rol
    cur.execute("SELECT id_rol FROM ROL WHERE nombre_rol = %s", (rol,))
    role_row = cur.fetchone()
    if role_row is None:
        conn.rollback()
        cur.close()
        conn.close()
        return "Rol no encontrado", 400
    id_rol = role_row[0]

    # Insertar en USUARIO_ROL
    try:
        cur.execute("INSERT INTO USUARIO_ROL (id_usuario, id_rol) VALUES (%s, %s)", (id_usuario, id_rol))

        # Si el rol corresponde a un empleado, guardar también en la tabla EMPLEADO
        employee_roles = ('EMPLEADO', 'SECRETARIA', 'AGENTE_INMOBILIARIO')
        if rol in employee_roles:
            nombre_empleado = request.form.get('nombre_empleado')
            identificacion_empleado = request.form.get('identificacion_empleado')
            telefono_empleado = request.form.get('telefono_empleado')
            tipo_empleado = request.form.get('tipo_empleado')

            # Validación mínima: nombre y identificación son obligatorios para empleados
            if not nombre_empleado or not identificacion_empleado:
                conn.rollback()
                cur.close()
                conn.close()
                return "Faltan datos obligatorios para empleado (nombre/identificación)", 400

            cur.execute(
                "INSERT INTO EMPLEADO (nombre, identificacion, telefono, tipo_empleado, id_usuario) VALUES (%s, %s, %s, %s, %s)",
                (nombre_empleado, identificacion_empleado, telefono_empleado, tipo_empleado, id_usuario)
            )

        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return f"Error al crear usuario: {e}", 500

    cur.close()
    conn.close()
    return redirect("/admin/usuarios")


# ---------------- EDITAR USUARIO ----------------
@app.route("/admin/usuarios/editar/<int:id_usuario>", methods=["GET", "POST"])
def editar_usuario(id_usuario):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "GET":
        # Obtener datos del usuario
        cur.execute("SELECT id_usuario, email, estado, fecha_creacion FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return redirect("/admin/usuarios")

        usuario = {
            "id_usuario": row[0],
            "email": row[1],
            "estado": row[2],
            "fecha_creacion": row[3]
        }

        # Roles disponibles
        cur.execute("SELECT nombre_rol FROM ROL ORDER BY id_rol")
        roles = [r[0] for r in cur.fetchall()]

        # Rol actual del usuario (si existe)
        cur.execute("SELECT r.nombre_rol FROM ROL r JOIN USUARIO_ROL ur ON r.id_rol = ur.id_rol WHERE ur.id_usuario = %s", (id_usuario,))
        role_row = cur.fetchone()
        current_role = role_row[0] if role_row else None

        cur.close()
        conn.close()
        return render_template("AdminOpciones/editar_usuario.html", usuario=usuario, roles=roles, current_role=current_role)

    # POST -> actualizar usuario
    email = request.form.get("email")
    contrasena = request.form.get("contrasena")
    rol = request.form.get("rol")

    # Actualizar email y opcionalmente contraseña
    if contrasena:
        cur.execute("UPDATE USUARIO SET email = %s, contrasena = %s WHERE id_usuario = %s", (email, contrasena, id_usuario))
    else:
        cur.execute("UPDATE USUARIO SET email = %s WHERE id_usuario = %s", (email, id_usuario))

    # Actualizar rol: buscar id_rol
    cur.execute("SELECT id_rol FROM ROL WHERE nombre_rol = %s", (rol,))
    role_row = cur.fetchone()
    if role_row is None:
        conn.rollback()
        cur.close()
        conn.close()
        return "Rol no encontrado", 400
    id_rol = role_row[0]

    # Reemplazar asignaciones de rol (mantener simple: un rol por usuario en UI)
    cur.execute("DELETE FROM USUARIO_ROL WHERE id_usuario = %s", (id_usuario,))
    cur.execute("INSERT INTO USUARIO_ROL (id_usuario, id_rol) VALUES (%s, %s)", (id_usuario, id_rol))

    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin/usuarios")


# ---------------- ELIMINAR USUARIO (confirmación + POST) ----------------
@app.route("/admin/usuarios/eliminar/<int:id_usuario>", methods=["GET", "POST"])
def eliminar_usuario(id_usuario):
    conn = get_db_connection()
    cur = conn.cursor()

    # Obtener usuario para mostrar en confirmación
    cur.execute("SELECT id_usuario, email FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return redirect('/admin/usuarios')

    usuario = {"id_usuario": row[0], "email": row[1]}

    if request.method == 'GET':
        cur.close()
        conn.close()
        return render_template('AdminOpciones/confirmar_eliminar.html', usuario=usuario)

    # POST: realizar eliminación
    cur.execute("DELETE FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin/usuarios')


#AGREGAR INMUEBLES PARA QUE SE VEAN EN EL PANEL DE ADMINISTRADOR-------------------------------------------------------------------------------------------------
#----------------- AGREGAR INMUEBLE ----------------
@app.route("/admin/inmuebles")
def gestion_inmuebles():
    conn = get_db_connection() # Usa tu función de conexión
    cur = conn.cursor()
    
    # Consulta completa: Datos del inmueble + Nombre del Tipo + Imagen Principal
    cur.execute("""
        SELECT 
            i.id_inmueble, 
            i.direccion, 
            i.barrio, 
            i.ciudad, 
            i.precio, 
            i.metraje, 
            t.nombre_tipo, 
            i.tipo_operacion, 
            i.estado,
            img.url_imagen
        FROM INMUEBLE i
        JOIN TIPO_INMUEBLE t ON i.id_tipo = t.id_tipo
        LEFT JOIN IMAGEN_INMUEBLE img ON i.id_inmueble = img.id_inmueble AND img.es_principal = TRUE
        ORDER BY i.id_inmueble DESC
    """)
    inmuebles = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # IMPORTANTE: Coincidiendo con tu estructura de carpetas
    return render_template("AdminOpciones/Gestion_Inmuebles.html", inmuebles=inmuebles)

@app.route("/admin/inmuebles/agregar", methods=["POST"])
def agregar_inmueble():
    # 1. Capturar datos del formulario
    direccion = request.form['direccion']
    barrio = request.form['barrio']
    ciudad = request.form['ciudad']
    precio = request.form['precio']
    metraje = request.form['metraje']
    id_tipo = request.form['id_tipo']
    tipo_operacion = request.form['tipo_operacion']
    estado = request.form.get('estado', 'DISPONIBLE')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 2. Insertar en tabla INMUEBLE
        cur.execute("""
            INSERT INTO INMUEBLE (direccion, barrio, ciudad, precio, metraje, id_tipo, tipo_operacion, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_inmueble
        """, (direccion, barrio, ciudad, precio, metraje, id_tipo, tipo_operacion, estado))
        
        id_nuevo = cur.fetchone()[0]

        # 3. Manejo de la Imagen Real
        if 'imagen_principal' in request.files:
            file = request.files['imagen_principal']
            if file and file.filename != '' and allowed_file(file.filename):
                # Nombre seguro para evitar errores en el servidor
                filename = secure_filename(f"inmueble_{id_nuevo}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Insertar en tabla IMAGEN_INMUEBLE
                cur.execute("""
                    INSERT INTO IMAGEN_INMUEBLE (url_imagen, es_principal, id_inmueble)
                    VALUES (%s, %s, %s)
                """, (filename, True, id_nuevo))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al registrar inmueble: {e}")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('gestion_inmuebles'))










#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------

# ---------------- EJECUTAR APP ----------------
if __name__ == "__main__":
    app.run(debug=True)