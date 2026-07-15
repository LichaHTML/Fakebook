import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "database/fakebook.db"

from flask import Flask, redirect, render_template, request,  session, url_for

app = Flask(__name__)



from flask import session
app.secret_key = "clave_secreta_para_sesiones"

#-------------FUNCIONES DB-------------
import re

def crear_db():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            password VARCHAR(255) NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contenido TEXT NOT NULL,
            fecha_post TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            imagen VARCHAR(255),
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)
        conn.commit()
        conn.close()


def username_existe(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))

    usuario_existente = cursor.fetchone()
    conn.close()
    return usuario_existente


def email_existe(email):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))

    email_existente = cursor.fetchone()
    conn.close()
    return email_existente


def crear_usuario(username, email, nombre, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try: 
        cursor.execute(
            "INSERT INTO usuarios (username, email, nombre, password) VALUES (?, ?, ?, ?)",
            (username, email, nombre, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def obtener_usuarios():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, nombre, fecha_registro FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios


def obtener_usuario_por_id(usuario_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email, nombre, fecha_registro FROM usuarios WHERE id = ?", (usuario_id,))

    usuario = cursor.fetchone()
    conn.close()
    return usuario


def validar_login(username, password):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, password
        FROM usuarios
        WHERE username = ?
        """,
        (username,)
    )

    usuario = cursor.fetchone()

    conn.close()

    if usuario and check_password_hash(
        usuario["password"],
        password
    ):
        return usuario

    return None


def obtener_post_por_id(post_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()


    cursor.execute("SELECT id, contenido, fecha_post, imagen, usuario_id FROM posts WHERE id = ?", (post_id,))

    post = cursor.fetchone()
    conn.close()
    return post


def crear_post(contenido, imagen, usuario_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try: 
        cursor.execute(
            "INSERT INTO posts (contenido, imagen, usuario_id) VALUES (?, ?, ?)",
            (contenido, imagen, usuario_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def listar_posts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT posts.id, posts.contenido, posts.fecha_post, posts.imagen, posts.usuario_id, usuarios.username
        FROM posts
        JOIN usuarios ON usuarios.id = posts.usuario_id
        ORDER BY fecha_post DESC
    """)

    posts = cursor.fetchall()
    conn.close()
    return posts


def obtener_posts_por_usuario(usuario_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT posts.id, posts.contenido, posts.fecha_post, posts.imagen, posts.usuario_id, usuarios.username
        FROM posts
        JOIN usuarios ON usuarios.id = posts.usuario_id
        WHERE posts.usuario_id = ?
        ORDER BY fecha_post DESC
    """, (usuario_id,))

    posts = cursor.fetchall()
    conn.close()
    return posts


def password_valida(password):

    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    
    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un número"
    
    return True,""


crear_db()

#------------RUTAS----------------

@app.route("/")
def index():
    usuario_id = session.get("usuario_id")

    if usuario_id:
        usuario = obtener_usuario_por_id(usuario_id)
        posts = listar_posts()

        return render_template(
            "index.html",
            usuario=usuario,
            posts=posts,
            pagina_actual="index"
        )
    else:
        return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():

    nombre = ""
    email = ""
    username = ""
    password = ""
    mensaje = ""
    registro_exitoso = False

    if request.method == "POST":

        nombre = request.form["nombre"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        password_ok, error_password = password_valida(password)

        if not password_ok:
            mensaje = error_password

            return render_template(
                "registro.html",
                nombre=nombre,
                email=email,
                username=username,
                mensaje=mensaje,
                registro_exitoso=False,
                pagina_actual="registro"
            )

        usuario_existente = username_existe(username)
        email_existente = email_existe(email)

        if usuario_existente and email_existente:
            mensaje = "El nombre de usuario y el email ya existen"

            return render_template(
                "registro.html",
                nombre=nombre,
                email=email,
                username=username,
                mensaje=mensaje,
                registro_exitoso=False,
                pagina_actual="registro"
            )

        elif usuario_existente:
            mensaje = "El nombre de usuario ya existe"

            return render_template(
                "registro.html",
                nombre=nombre,
                email=email,
                username=username,
                mensaje=mensaje,
                registro_exitoso=False,
                pagina_actual="registro"
            )

        elif email_existente:
            mensaje = "El email ya existe"

            return render_template(
                "registro.html",
                nombre=nombre,
                email=email,
                username=username,
                mensaje=mensaje,
                registro_exitoso=False,
                pagina_actual="registro"
            )

        password_hash = generate_password_hash(password)

        if crear_usuario(username, email, nombre, password_hash):
            mensaje = "Registro exitoso"
            registro_exitoso = True

            return redirect(url_for("login_route"))

        else:
            mensaje = "Error al registrar el usuario"
            registro_exitoso = False

    return render_template(
        "registro.html",
        nombre=nombre,
        email=email,
        username=username,
        mensaje=mensaje,
        registro_exitoso=registro_exitoso,
        pagina_actual="registro"
    )

    nombre = ""
    email = ""
    username = ""
    password = ""
    mensaje = ""
    registro_exitoso = False

    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        usuario_repetido = username_existe(username)
        email_repetido = email_existe(email)
        
        password_ok, error_password = password_valida(password)

        if not password_ok:
            mensaje = error_password
        
            return render_template("registro.html",
                                    nombre=nombre,
                                    email=email,
                                    username=username, 
                                    password=password, 
                                    mensaje=mensaje, 
                                    registro_exitoso=False,
                                    pagina_actual="registro")

        if crear_usuario(username, email, nombre, password):
            mensaje = "Registro exitoso"
            registro_exitoso = True
            return redirect(url_for("login_route"))
        else:
            mensaje = "El nombre de usuario ya existe"
            registro_exitoso = False

    return render_template("registro.html", nombre=nombre, email=email, username=username, password=password, mensaje=mensaje, registro_exitoso=registro_exitoso, pagina_actual="registro")


@app.route("/usuarios")
def listar_usuarios():
    usuarios = obtener_usuarios()
    return render_template("usuarios.html", usuarios=usuarios, pagina_actual="usuarios")


@app.route("/usuario/<int:usuario_id>")
def perfil(usuario_id):
    posts = obtener_posts_por_usuario(usuario_id)
    usuario = obtener_usuario_por_id(usuario_id)
    
    if usuario:
        return render_template("perfil.html", usuario=usuario, pagina_actual="perfil", posts=posts)
    else:
        return "Usuario no encontrado", 404


@app.route("/login", methods=["GET", "POST"])
def login_route():

    username = ""
    password = ""
    usuario = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        usuario = validar_login(username, password)
        if usuario:
            session["usuario_id"] = usuario["id"]
            return redirect("/")
        else:
            return "Credenciales inválidas", 401
    return render_template("login.html", username=username, password=password, usuario=usuario, pagina_actual="login")


@app.route("/perfil")
def ver_perfil():
    usuario_id = session.get("usuario_id")
    if usuario_id:
        return redirect(f"/usuario/{usuario_id}")
    else:
        return "No estás logueado"


@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    return redirect("/login")


@app.route("/crear_post", methods=["POST"])
def crear_post_route():

    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return redirect("/login")

    contenido = request.form["contenido"].strip()

    crear_post(
        contenido=contenido,
        imagen=None,
        usuario_id=usuario_id
    )

    return redirect("/")
  

@app.route("/borrar_usuarios")
def borrar_usuarios():

    conexion = sqlite3.connect(DB_PATH)

    cursor = conexion.cursor()

    cursor.execute("DELETE FROM posts")

    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name='posts'
    """)

    cursor.execute("DELETE FROM usuarios")

    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name='usuarios'
    """)

    conexion.commit()

    conexion.close()

    return "Base de datos limpiada"


if __name__ == "__main__":
    app.run(debug=True)