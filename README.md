# 🌿 El Paso Frutería — Sistema de Gestión Comercial y Tienda Virtual

[![Django](https://img.shields.io/badge/Django-6.1.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.2-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![SENA](https://img.shields.io/badge/SENA-ADSO_3321349-39A900?style=for-the-badge)](https://www.sena.edu.co/)

> **Proyecto Formativo Institucional**  
> **Servicio Nacional de Aprendizaje (SENA)** — Centro Minero, Regional Boyacá  
> **Programa:** Tecnólogo en Análisis y Desarrollo de Software (ADSO)  
> **Ficha de Caracterización:** 3321349  
> **Instructor Técnico:** Antony Reynel Botello Herrera  

---

## 👥 Equipo de Desarrollo (GAES)

* 👑 **Jhon Mario Guamanzar Sierra** — *Líder de Proyecto & Desarrollador Principal* ([@jhonmariog102015-a11y](https://github.com/jhonmariog102015-a11y))
* 💻 **Juan Carlos Merchán** — *Desarrollador Backend & Base de Datos* ([@juanc29mb-creator](https://github.com/juanc29mb-creator))
* 🎨 **Jhon Exander Gutiérrez Moreno** — *Desarrollador Frontend & UI* ([@jhonexander](https://github.com/))

---

## 🚀 Características Principales del Sistema

1. **Arquitectura MVT Desacoplada:**
   * Implementación de controladores basados en funciones (FBV) con inyección de diccionario de contexto y motor DTL (*Django Template Language*).
2. **Modelo Entidad-Relación (MER Guía G-03):**
   * Persistencia relacional mediante Django ORM con las entidades: `Categoria`, `Proveedor`, `Producto` y `Cliente`.
   * Integridad referencial protegida mediante relaciones foráneas (`models.CASCADE` / `models.PROTECT`).
3. **Tienda Virtual Campesina (Diseño 4: Mercado Multi):**
   * Página de aterrizaje (*Landing Page*) moderna y responsiva con banner principal, llamado a la acción y tablero de categorías agrícolas.
4. **Catálogo Interactivo con Filtrado Reactivo (`/catalogo-frutas/`):**
   * Explorador visual de productos frutícolas por categorías (Cítricas, Tropicales, Berries, Exóticas, Importadas) con búsqueda y actualización dinámica.
5. **Panel Administrativo Especializado (`/dashboard/`):**
   * Métricas en tiempo real (conteo de productos, usuarios activos, categorías) y tabla interactiva de inventario con precios y stock.
6. **Panel Administrativo Django Nativo (`/admin/`):**
   * Registro completo de modelos con `list_display`, filtros por categoría y edición rápida en línea (`list_editable`).

---

## 📂 Estructura del Proyecto

```text
ProyectoFinalSenaFruteria/
│
├── config/                     # Configuración central del proyecto Django
│   ├── settings.py             # Configuración regional (es-co), apps y BD
│   ├── urls.py                 # Enrutamiento maestro y namespaces
│   ├── wsgi.py / asgi.py       # Interfaces para servidores de producción
│
├── principal/                  # Módulo funcional de la frutería
│   ├── models.py               # Modelos relacionales: Categoria, Producto, etc.
│   ├── views.py                # Controladores: inicio, dashboard, catálogo
│   ├── admin.py                # Parametrización del panel de control
│   ├── templates/              # Plantillas HTML con motor DTL
│   │   ├── principal/          # index.html (Inicio), dashboard.html, login.html
│   │   └── fruteria/           # catalogo_frutas.html, tienda.html
│   └── static/                 # Estilos CSS (panel.css, index.css) y scripts JS
│
├── evidencia/                  # Entregables oficiales de la Guía G-03
│   ├── Informe_Tecnico_Modelo_Datos_Fruteria_APA7.pdf  # Informe oficial APA 7
│   ├── capturas/               # Evidencias gráficas de ejecución
│   └── tallerViernes.docx      # Documento técnico base
│
├── manage.py                   # Gestor de comandos de Django
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Documentación oficial del repositorio
```

---

## 🛠️ Instrucciones de Instalación y Ejecución Local

Para clonar y poner en marcha el proyecto en cualquier entorno de desarrollo:

### 1. Clonar el Repositorio
```bash
git clone https://github.com/jhonmariog102015-a11y/proyecto-fruteria-final.git
cd proyecto-fruteria-final
```

### 2. Crear y Activar el Entorno Virtual
```bash
# En Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Aplicar Migraciones de Base de Datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Iniciar el Servidor de Desarrollo
```bash
python manage.py runserver
```

El aplicativo estará disponible en: **`http://127.0.0.1:8000/`**

---

## 📌 Enlaces del Aplicativo en Ejecución

* **Página de Inicio:** `http://127.0.0.1:8000/`
* **Catálogo de Frutas:** `http://127.0.0.1:8000/catalogo-frutas/`
* **Dashboard Administrativo:** `http://127.0.0.1:8000/dashboard/`
* **Inicio de Sesión:** `http://127.0.0.1:8000/accounts/login/` *(Credenciales: `admin` / `admin123`)*
* **Django Admin:** `http://127.0.0.1:8000/admin/`

---

## 📄 Documentación Académica Oficial (Normas APA 7ma Edición)
El informe técnico completo de 19 páginas que soporta el cumplimiento de las actividades 3.1, 3.2, 3.3 y 3.4 de la Guía G-03 se encuentra en el repositorio:
* [`evidencia/Informe_Tecnico_Modelo_Datos_Fruteria_APA7.pdf`](evidencia/Informe_Tecnico_Modelo_Datos_Fruteria_APA7.pdf)
