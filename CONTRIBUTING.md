# Guía de Contribución y Flujo de Trabajo Git (GAES)

Bienvenidos al proyecto formativo **El Paso Frutería**. Para garantizar la calidad del software, la trazabilidad del código y evitar conflictos entre ramas, todo el equipo del GAES seguirá este estándar técnico de ingeniería.

---

## 🌿 1. Modelo de Ramas (Git Flow Simplificado)

* **`main` (Producción / Entrega Estable):**
  * Solo contiene código probado, funcional y documentado.
  * Ningún integrante debe realizar commits directos con código experimental.
* **`feature/<nombre-funcionalidad>` (Ramas de Tarea):**
  * Cada nueva funcionalidad o módulo debe desarrollarse en su propia rama que nace de `main`.
  * Ejemplos: `feature/modulo-ventas`, `feature/reportes-pdf`, `feature/login-jwt`.
* **`fix/<nombre-error>` (Corrección de Errores):**
  * Ramas destinadas a corregir bugs específicos encontrados en pruebas.

---

## 🔄 2. Ciclo de Trabajo Paso a Paso

1. **Antes de empezar a programar:**
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Crear una rama para la tarea:**
   ```bash
   git checkout -b feature/nombre-tarea
   ```
3. **Realizar cambios y commits atómicos:**
   ```bash
   git add .
   git commit -m "feat(modulo): descripcion clara del cambio"
   ```
4. **Publicar la rama en GitHub:**
   ```bash
   git push -u origin feature/nombre-tarea
   ```
5. **Crear un Pull Request en GitHub:**
   * Solicitar revisión al Líder del Proyecto (`@jhonmariog102015-a11y`).
   * Una vez revisado y validado, se fusiona a `main`.

---

## 📝 3. Convención de Mensajes de Commit (Conventional Commits)

Utilizar prefijos descriptivos en minúsculas:
* `feat:` Nueva funcionalidad para el usuario.
* `fix:` Corrección de un fallo o error en el sistema.
* `docs:` Cambios o adiciones en documentación (README, PDF, comentarios).
* `style:` Ajustes estéticos, CSS, diseño visual o formato sin alterar lógica.
* `refactor:` Reestructuración interna de código sin cambiar funcionalidad.
* `test:` Adición o modificación de pruebas automáticas o verificaciones.

---

## 🐍 4. Buenas Prácticas de Desarrollo en Django

1. **Aislamiento de Entorno:** Siempre trabajar con el entorno virtual activado (`.venv`).
2. **Persistencia y Modelos:** Si se modifica `models.py`, ejecutar inmediatamente:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. **Archivos Binarios:** Nunca subir la base de datos local `db.sqlite3` ni archivos temporales `__pycache__/` a Git.
4. **Comprobación del Sistema:** Antes de hacer commit, verificar que Django no reporte advertencias:
   ```bash
   python manage.py check
   ```
