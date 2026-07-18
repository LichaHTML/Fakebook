# Fakebook

Fakebook es una aplicación web tipo red social desarrollada como proyecto de aprendizaje utilizando Python y Flask.

El objetivo del proyecto es replicar las funcionalidades principales de una red social mientras se aplican buenas prácticas de desarrollo backend, autenticación de usuarios, bases de datos y organización del código.

---

## Tecnologías utilizadas

- Python
- Flask
- SQLite
- HTML5
- CSS3
- Jinja2
- Git
- GitHub

---

## Funcionalidades implementadas

### Usuarios

- Registro de usuarios
- Inicio de sesión
- Cierre de sesión
- Contraseñas protegidas mediante hash
- Control de sesiones

### Publicaciones

- Crear publicaciones
- Editar publicaciones propias
- Eliminar publicaciones propias
- Mostrar publicaciones ordenadas por fecha

### Comentarios

- Crear comentarios
- Mostrar comentarios en cada publicación

### Seguridad

- Protección de rutas mediante login
- Validación de permisos para editar publicaciones
- Validación de permisos para eliminar publicaciones

---

## Estructura del proyecto

```
Fakebook/
│
├── app.py
├── fakebook.db
├── static/
│   ├── css/
│   └── img/
│
├── templates/
│   ├── base.html
│   ├── header.html
│   ├── login.html
│   ├── registro.html
│   ├── perfil.html
│   ├── usuarios.html
│   └── post/
│       ├── posts.html
│       └── editar_post.html
```

---

## Próximas funcionalidades

- Sistema de Likes
- Seguir usuarios
- Mejoras en perfiles
- Búsqueda de usuarios
- Paginación
- Migración a PostgreSQL
- Diseño con Bootstrap

---

## Estado del proyecto

Proyecto en desarrollo.

Actualmente continúa expandiéndose con nuevas funcionalidades y mejoras en arquitectura.

---

## Autor

Desarrollado por Lisandro como proyecto de portfolio para desarrollo web backend.