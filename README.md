# Ureview — Taller 2 (Django + Bootstrap)

## Cómo correr el proyecto localmente (Windows / PowerShell)

Ejecutar desde la carpeta `Talleres-MiguelColorado`.

```powershell
# 1. Activar el entorno virtual
venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Migraciones
python manage.py migrate

# 4. Cargar datos (orden: movies, luego news)
python manage.py add_movies_db
python manage.py seed_movies
python manage.py add_news_db

# 5. Crear superusuario (para /admin/)
python manage.py createsuperuser

# 6. Levantar el servidor
python manage.py runserver
```

Si PowerShell bloquea `Activate.ps1`: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

URLs clave: `/` (home), `/movies/`, `/series/`, `/news/`, `/statistics/`, `/signup/`, `/admin/`.

Guía completa de ejecución y pruebas (incluye tests unitarios): [GUIA_EJECUCION_Y_PRUEBAS.md](GUIA_EJECUCION_Y_PRUEBAS.md).

## Entregable Taller 2

1. **Repositorio / rama**: https://github.com/migueCOLORADO/PupiGo/tree/Miguel-Colorado-Talleres

2. **≥10 películas en Cards de Bootstrap (genre y year visibles) + navbar con imagen**
   ![Catálogo con Cards Bootstrap](capturas/Taller%202/punto1.png)
   ![Catálogo con Cards Bootstrap (cont.)](capturas/Taller%202/punto1.1.png)
   ![Catálogo con Cards Bootstrap (cont.)](capturas/Taller%202/punto1.2.png)
   ![Catálogo con Cards Bootstrap (cont.)](capturas/Taller%202/punto1.3.png)

3. **Mismo listado en ventana angosta (responsive)**
   ![Catálogo responsive](capturas/Taller%202/punto2.png)

4. **News en Horizontal Cards**
   ![News horizontal cards](capturas/Taller%202/punto3.png)

5. **Gráfica de películas por año**
   ![Gráfica por año](capturas/Taller%202/punto4.png)

6. **Gráfica de películas por género**
   ![Gráfica por género](capturas/Taller%202/punto5.png)
