import sqlite3

from functools import wraps
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
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contenido TEXT NOT NULL,
            fecha_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(post_id) REFERENCES posts(id)
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
    cursor.execute("SELECT id, username, email, nombre, fecha_registro, password FROM usuarios")
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


def crear_comentario(contenido, usuario_id, post_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO comentarios
            (contenido, usuario_id, post_id)
            VALUES (?, ?, ?)
            """,
            (contenido, usuario_id, post_id)
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def obtener_comentarios_por_post(post_id):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT comentarios.id,
               comentarios.contenido,
               comentarios.fecha_comentario,
               comentarios.usuario_id,
               comentarios.post_id,
               usuarios.username

        FROM comentarios

        JOIN usuarios
        ON usuarios.id = comentarios.usuario_id

        WHERE comentarios.post_id = ?

        ORDER BY comentarios.fecha_comentario ASC
        """,
        (post_id,)
    )

    comentarios = cursor.fetchall()

    conn.close()

    return comentarios


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


def obtener_post_por_id(post_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT posts.id,
               posts.contenido,
               posts.fecha_post,
               posts.imagen,
               posts.usuario_id,
               usuarios.username
        FROM posts
        JOIN usuarios ON usuarios.id = posts.usuario_id
        WHERE posts.id = ?
    """, (post_id,))

    post = cursor.fetchone()

    conn.close()

    return post


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


def login_requerido(f):

    @wraps(f)
    def funcion_decorada(*args, **kwargs):

        if "usuario_id" not in session:
            return redirect(url_for("login_route"))

        return f(*args, **kwargs)

    return funcion_decorada
    if "usuario_id" not in session:
        return False
    
    return True


def borrar_post(post_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM comentarios WHERE post_id = ?", (post_id,))
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))

    try:
        conn.commit()
    finally:
        conn.close()
 

def editar_post(post_id, contenido):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE posts SET contenido = ? WHERE id = ?",
        (contenido, post_id)
    )

    try:
        conn.commit()
    finally:    
        conn.close()

crear_db()

#------------RUTAS----------------

@app.route("/")
def index():
    usuario_id = session.get("usuario_id")

    if usuario_id:
        usuario = obtener_usuario_por_id(usuario_id)

        posts = listar_posts()

        posts_con_comentarios = []
        for post in posts:
            post = dict(post)
            post["comentarios"] = obtener_comentarios_por_post(post["id"])
            posts_con_comentarios.append(post)

        return render_template(
            "index.html",
            usuario=usuario,
            usuario_id=usuario_id,
            posts=posts_con_comentarios,
            pagina_actual="index"
        )
    else:
        return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():

    nombre = ""
    email = ""
    username = ""
    mensaje = ""

    if request.method == "POST":

        nombre = request.form["nombre"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        password_ok, error_password = password_valida(password)

        if not password_ok:
            return render_template(
                "registro.html",
                nombre=nombre,
                email=email,
                username=username,
                mensaje=error_password,
                registro_exitoso=False,
                pagina_actual="registro"
            )

        usuario_existente = username_existe(username)
        email_existente = email_existe(email)

        if usuario_existente and email_existente:
            mensaje = "El nombre de usuario y el email ya existen"

        elif usuario_existente:
            mensaje = "El nombre de usuario ya existe"

        elif email_existente:
            mensaje = "El email ya existe"

        else:

            password_hash = generate_password_hash(password)

            if crear_usuario(
                username,
                email,
                nombre,
                password_hash
            ):
                return redirect(url_for("login_route"))

            mensaje = "Error al registrar el usuario"

        return render_template(
            "registro.html",
            nombre=nombre,
            email=email,
            username=username,
            mensaje=mensaje,
            registro_exitoso=False,
            pagina_actual="registro"
        )

    return render_template(
        "registro.html",
        nombre=nombre,
        email=email,
        username=username,
        mensaje=mensaje,
        registro_exitoso=False,
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
@login_requerido
def listar_usuarios():

    usuarios = obtener_usuarios()
    return render_template("usuarios.html", usuarios=usuarios, pagina_actual="usuarios")


@app.route("/usuario/<int:usuario_id>")
@login_requerido
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
@login_requerido
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
@login_requerido
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
@login_requerido
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


@app.route("/crear_comentario", methods=["POST"])
@login_requerido
def crear_comentario_route():

    usuario_id = session.get("usuario_id")

    contenido = request.form["contenido"].strip()
    post_id = request.form["post_id"]

    crear_comentario(
        contenido=contenido,
        usuario_id=usuario_id,
        post_id=post_id
    )

    return redirect("/")


@app.route("/borrar_post/<int:post_id>", methods=["POST"])
@login_requerido
def borrar_post_post(post_id):

    post = obtener_post_por_id(post_id)

    if not post:
        return "Post no encontrado", 404

    if post["usuario_id"] != session["usuario_id"]:
        return "No tenés permiso para borrar este post", 403

    borrar_post(post_id)

    return redirect("/")


@app.route("/editar_post/<int:post_id>", methods=["GET"])
@login_requerido
def editar_post_get(post_id):

    post = obtener_post_por_id(post_id)

    if not post:
        return "Post no encontrado", 404

    if post["usuario_id"] != session["usuario_id"]:
        return "No tenés permiso para editar este post", 403

    return render_template("post/editar_post.html", post=post)

@app.route("/editar_post/<int:post_id>", methods=["POST"])
@login_requerido
def editar_post_route(post_id):
    post = obtener_post_por_id(post_id)

    if not post:
        return "Post no encontrado", 404

    if post["usuario_id"] != session["usuario_id"]:
        return "No tenés permiso para editar este post", 403

    contenido = request.form["contenido"].strip()

    if not contenido:
        return "El contenido no puede estar vacío", 400

    editar_post(post_id, contenido)

    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)