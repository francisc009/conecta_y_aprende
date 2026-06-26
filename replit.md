# Conecta y Aprende

Plataforma digital de reintegración social para personas en rehabilitación por adicciones en Villa Victoria, Estado de México. Ofrece capacitación en mecánica automotriz a través de módulos educativos.

## Stack

- **Backend:** Python + Flask (API REST)
- **Base de datos:** MongoDB (`conecta_aprende`)
- **Frontend:** HTML5 estático servido por Flask
- **Estilos:** CSS3 / Sass (plantilla Hyperspace de HTML5 UP)

## Arquitectura

Un solo servidor Flask en `server.py` que:
- Sirve todos los archivos HTML estáticos desde la raíz del proyecto
- Expone la API REST para usuarios y administradores
- Corre en `0.0.0.0:5000`

## Páginas

| Archivo | Descripción |
|---|---|
| `inicio.html` | Página de registro de usuarios (entrada principal) |
| `index.html` | Página principal con módulos |
| `admin.html` | Login de administradores |
| `funciones_admin.html` | Panel CRUD de admins y usuarios |
| `modulo_1.html` … `modulo_4.html` | Contenido educativo |
| `quienes_somos.html` | Información del proyecto |

## API Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/registro` | Registrar nuevo usuario |
| POST | `/admin/login` | Login de administrador |
| POST | `/admin` | Crear administrador |
| GET | `/admins` | Listar administradores |
| PUT | `/admin/<id>` | Editar administrador |
| DELETE | `/admin/<id>` | Eliminar administrador |
| GET | `/usuarios` | Listar usuarios |
| PUT | `/usuario/<id>` | Editar usuario |
| DELETE | `/usuario/<id>` | Eliminar usuario |

## Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `MONGODB_URI` | URI de conexión MongoDB | `mongodb://localhost:27017/` |

## Ejecutar

```bash
python server.py
```

## User preferences

- Idioma del proyecto: Español
