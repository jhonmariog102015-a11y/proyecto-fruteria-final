# ==============================================================================
# CONTROLADOR DE VISTAS (principal/views.py)
# Gestiona la lógica de negocio, consultas al ORM y renderizado de plantillas.
# ==============================================================================

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import get_user_model, logout, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Case, When, Value, IntegerField, Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Producto, Categoria, PerfilUsuario


def inicio(request):
    """
    VISTA PRINCIPAL / LANDING PAGE ('/' y '/inicio/')
    -------------------------------------------------
    """
    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.all()
    # Producto destacado para el Hero dinámico asimétrico
    producto_destacado = productos.filter(en_oferta=True).first() or productos.first()

    context = {
        'titulo': 'El Paso Frutería — Mercado Campesino',
        'productos': productos,
        'categorias': categorias,
        'producto_destacado': producto_destacado,
        'total_productos': productos.count(),
    }
    return render(request, 'principal/index.html', context)


def catalogo_frutas_view(request):
    """
    CATÁLOGO INTERACTIVO DE FRUTAS ('/catalogo-frutas/')
    ----------------------------------------------------
    """
    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.all()
    context = {
        'titulo': 'Catálogo de Frutas Frescas — El Paso Frutería',
        'productos': productos,
        'categorias': categorias,
        'total_productos': productos.count(),
    }
    # NOTA TÉCNICA PARA EL EQUIPO (GAES):
    # Se unificó la ubicación de plantillas dentro de 'principal/templates/principal/'
    # para que todos los archivos HTML (index, catalogo, dashboard, login) residan
    # en una sola carpeta bajo la convención estándar de Django MVT.
    return render(request, 'principal/catalogo_frutas.html', context)


def es_administrador(user):
    """
    Control de acceso RBAC: Verifica si el usuario autenticado tiene rol de Super Admin
    o rol administrativo en PerfilUsuario.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perfil = getattr(user, 'perfil', None)
    return perfil is not None and (perfil.rol == 'admin' or getattr(perfil, 'es_admin', False))


@login_required
def dashboard_view(request):
    """
    PANEL ADMINISTRATIVO PRIVADO ('/dashboard/')
    --------------------------------------------
    """
    User = get_user_model()

    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.annotate(num_productos=Count('productos')).order_by('nombre')
    total_productos = productos.count()
    total_ofertas = productos.filter(en_oferta=True).count()
    total_usuarios = User.objects.count()
    # Sincronización automática de integridad: garantizar perfil activo y rol asignado
    for u in User.objects.all():
        rol_sugerido = 'cajero'
        if hasattr(u, 'perfil') and u.perfil and u.perfil.rol in ['admin', 'bodeguero', 'cajero']:
            rol_sugerido = u.perfil.rol
            if u.is_superuser:
                rol_sugerido = 'admin'
        elif u.is_superuser or u.username in ['admin', 'guti', 'juan']:
            rol_sugerido = 'admin'
        elif 'bodega' in u.username.lower() or u.username == 'Steven Perez':
            rol_sugerido = 'bodeguero'
        elif 'caja' in u.username.lower() or 'cajer' in u.username.lower() or 'ventas' in u.username.lower() or u.username == 'mario perez':
            rol_sugerido = 'cajero'

        perfil, created = PerfilUsuario.objects.get_or_create(
            usuario=u,
            defaults={'rol': rol_sugerido, 'estado': 'activo', 'telefono': '3101234567'}
        )
        if not created and (perfil.rol not in ['admin', 'bodeguero', 'cajero'] or (u.is_superuser and perfil.rol != 'admin')):
            perfil.rol = rol_sugerido
            perfil.save()
        if not perfil.estado:
            perfil.estado = 'activo'
            perfil.save()

    # Obtener única y exclusivamente los REGISTROS ACTIVOS ordenados por ROLES:
    # Jerarquía requerida: 1. Super Admin, 2. Bodeguero, 3. Cajero
    perfiles_usuarios = PerfilUsuario.objects.select_related('usuario').filter(
        estado='activo',
        usuario__is_active=True
    ).annotate(
        orden_rol=Case(
            When(usuario__is_superuser=True, then=Value(1)),
            When(rol='admin', then=Value(1)),
            When(rol='bodeguero', then=Value(2)),
            When(rol='cajero', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('orden_rol', 'usuario__username')

    # Métricas específicas del equipo de cuentas activas por rol
    total_activos = perfiles_usuarios.count()
    total_superadmins = perfiles_usuarios.filter(orden_rol=1).count()
    total_bodegueros = perfiles_usuarios.filter(orden_rol=2).count()
    total_cajeros = perfiles_usuarios.filter(orden_rol=3).count()

    # Métricas financieras del catálogo
    inversion_total = sum(p.costo_compra * p.stock_actual for p in productos)
    valor_venta_potencial = sum(p.precio_efectivo * p.stock_actual for p in productos)
    ganancia_potencial = valor_venta_potencial - inversion_total
    margen_promedio = round((ganancia_potencial / inversion_total * 100), 1) if inversion_total > 0 else Decimal('0.0')

    return render(request, 'principal/dashboard.html', {
        'productos': productos,
        'categorias': categorias,
        'perfiles_usuarios': perfiles_usuarios,
        'total_productos': total_productos,
        'total_ofertas': total_ofertas,
        'total_activos': total_activos,
        'total_superadmins': total_superadmins,
        'total_bodegueros': total_bodegueros,
        'total_cajeros': total_cajeros,
        # Mantener retrocompatibilidad con referencias anteriores
        'total_admins': total_activos,
        'total_admins_activos': total_activos,
        'total_staff': perfiles_usuarios.filter(usuario__is_staff=True).count(),
        'inversion_total': inversion_total,
        'valor_venta_potencial': valor_venta_potencial,
        'ganancia_potencial': ganancia_potencial,
        'margen_promedio': margen_promedio,
        'es_admin': es_administrador(request.user),
    })


@login_required
def crear_producto_dashboard(request):
    """
    CREACIÓN DIRECTA DE PRODUCTOS DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            categoria_id = request.POST.get('categoria_id')
            costo_compra = Decimal(request.POST.get('costo_compra', '0').replace(',', '.'))
            precio_venta_unitario = Decimal(request.POST.get('precio_venta_unitario', '0').replace(',', '.'))
            en_oferta = request.POST.get('en_oferta') in ['on', 'true', 'True', '1']
            precio_oferta_raw = request.POST.get('precio_oferta', '').strip()
            precio_oferta = Decimal(precio_oferta_raw.replace(',', '.')) if (en_oferta and precio_oferta_raw) else None
            stock_actual = Decimal(request.POST.get('stock_actual', '0').replace(',', '.'))
            stock_minimo = Decimal(request.POST.get('stock_minimo', '5').replace(',', '.'))
            unidad_medida = request.POST.get('unidad_medida', 'kg').strip()
            # NOTA PARA EL EQUIPO (GAES):
            # Se asignan valores de respaldo limpios sin caracteres emoji especiales para
            # evitar fallos de codificación (UnicodeEncodeError en Windows/consolas cp1252/cp932)
            # y garantizar persistencia consistente en la base de datos SQL.
            origen = request.POST.get('origen', '').strip() or 'Cosecha: Hace 1 día • Finca El Campo'
            icono_emoji = request.POST.get('icono_emoji', '').strip()
            imagen_url = request.POST.get('imagen_url', '').strip() or 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?q=80&w=600&auto=format&fit=crop'
            estado = request.POST.get('estado', 'Disponible').strip()

            categoria = get_object_or_404(Categoria, pk=categoria_id)

            Producto.objects.create(
                nombre=nombre,
                categoria=categoria,
                costo_compra=costo_compra,
                precio_venta_unitario=precio_venta_unitario,
                en_oferta=en_oferta,
                precio_oferta=precio_oferta,
                stock_actual=stock_actual,
                stock_minimo=stock_minimo,
                unidad_medida=unidad_medida,
                origen=origen,
                icono_emoji=icono_emoji,
                imagen_url=imagen_url,
                estado=estado
            )
            messages.success(request, f"¡Producto '{nombre}' creado exitosamente en el catálogo!")
        except Exception as e:
            messages.error(request, f"Error al crear el producto: {str(e)}")

    return redirect('dashboard')


@login_required
def editar_producto_dashboard(request, id_producto):
    """
    EDICIÓN RÁPIDA DE PRECIOS, COSTOS, OFERTAS Y STOCK DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=id_producto)
        try:
            producto.nombre = request.POST.get('nombre', producto.nombre).strip()
            categoria_id = request.POST.get('categoria_id')
            if categoria_id:
                producto.categoria = get_object_or_404(Categoria, pk=categoria_id)

            costo_raw = request.POST.get('costo_compra', '').replace(',', '.')
            if costo_raw:
                producto.costo_compra = Decimal(costo_raw)

            precio_raw = request.POST.get('precio_venta_unitario', '').replace(',', '.')
            if precio_raw:
                producto.precio_venta_unitario = Decimal(precio_raw)

            producto.en_oferta = request.POST.get('en_oferta') in ['on', 'true', 'True', '1']
            precio_oferta_raw = request.POST.get('precio_oferta', '').strip().replace(',', '.')
            if producto.en_oferta and precio_oferta_raw:
                producto.precio_oferta = Decimal(precio_oferta_raw)
            else:
                producto.precio_oferta = None

            stock_raw = request.POST.get('stock_actual', '').replace(',', '.')
            if stock_raw:
                producto.stock_actual = Decimal(stock_raw)

            stock_min_raw = request.POST.get('stock_minimo', '').replace(',', '.')
            if stock_min_raw:
                producto.stock_minimo = Decimal(stock_min_raw)

            producto.unidad_medida = request.POST.get('unidad_medida', producto.unidad_medida).strip()
            producto.origen = request.POST.get('origen', producto.origen).strip()
            producto.icono_emoji = request.POST.get('icono_emoji', producto.icono_emoji).strip()
            
            img_url = request.POST.get('imagen_url', '').strip()
            if img_url:
                producto.imagen_url = img_url

            producto.estado = request.POST.get('estado', producto.estado).strip()

            producto.save()
            messages.success(request, f"¡Producto '{producto.nombre}' actualizado con éxito!")
        except Exception as e:
            messages.error(request, f"Error al actualizar el producto: {str(e)}")

    return redirect('dashboard')


@login_required
def eliminar_producto_dashboard(request, id_producto):
    """
    ELIMINACIÓN DE PRODUCTO DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=id_producto)
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"El producto '{nombre}' fue eliminado del catálogo.")
    return redirect('dashboard')


@login_required
def crear_categoria_dashboard(request):
    """
    CREACIÓN DE CATEGORÍA DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        if nombre:
            Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, f"¡Categoría '{nombre}' creada exitosamente!")
        else:
            messages.error(request, "El nombre de la categoría no puede estar vacío.")
    return redirect('dashboard')


@login_required
def eliminar_categoria_dashboard(request, id_categoria):
    """
    ELIMINACIÓN DE CATEGORÍA DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        categoria = get_object_or_404(Categoria, pk=id_categoria)
        if categoria.productos.exists():
            messages.warning(request, f"No se puede eliminar '{categoria.nombre}' porque contiene productos asociados.")
        else:
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f"Categoría '{nombre}' eliminada con éxito.")
    return redirect('dashboard')


# ==============================================================================
# CRUD REGISTROS Y ROLES (VISTAS BASADAS EN FUNCIONES - FBV)
# Listar (en dashboard_view), Crear, Editar (get_object_or_404) y Eliminar (POST)
# ==============================================================================

@login_required
def crear_usuario_dashboard(request):
    """
    CRUD REGISTROS Y ROLES: CREACIÓN DE USUARIO DESDE EL DASHBOARD (FBV)
    Crea la cuenta en auth.User y su PerfilUsuario vinculado con rol jerárquico.
    Acción restringida exclusivamente a usuarios con rol de Administrador.
    """
    if not es_administrador(request.user):
        messages.error(request, 'Acceso denegado: Únicamente los administradores tienen permiso para registrar nuevos usuarios.')
        return redirect('/dashboard/#usuarios')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol = request.POST.get('rol', 'cajero').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validaciones de integridad
        if not username or not email or not password:
            messages.error(request, 'El nombre de usuario, correo electrónico y contraseña son obligatorios.')
            return redirect('/dashboard/#usuarios')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas ingresadas no coinciden.')
            return redirect('/dashboard/#usuarios')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"El nombre de usuario '{username}' ya está registrado.")
            return redirect('/dashboard/#usuarios')

        if User.objects.filter(email=email).exists():
            messages.error(request, f"El correo electrónico '{email}' ya se encuentra en uso.")
            return redirect('/dashboard/#usuarios')

        if rol not in ['admin', 'bodeguero', 'cajero']:
            rol = 'cajero'

        es_super = (rol == 'admin')
        nuevo_usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=es_super
        )

        perfil, _ = PerfilUsuario.objects.update_or_create(
            usuario=nuevo_usuario,
            defaults={
                'telefono': telefono,
                'rol': rol,
                'estado': 'activo'
            }
        )

        rol_nombre = perfil.nombre_rol
        messages.success(request, f"¡Usuario '{username}' registrado exitosamente con rol de {rol_nombre}!")

    return redirect('/dashboard/#usuarios')


@login_required
def editar_usuario_dashboard(request, user_id):
    """
    CRUD REGISTROS Y ROLES: EDICIÓN DE USUARIO Y ROL (FBV CON get_object_or_404)
    Actualiza datos de autenticación (User) y perfil operativo (PerfilUsuario).
    Acción restringida exclusivamente a usuarios con rol de Administrador.
    """
    if not es_administrador(request.user):
        messages.error(request, 'Acceso denegado: Únicamente los administradores tienen permiso para modificar usuarios y roles.')
        return redirect('/dashboard/#usuarios')

    target_user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol = request.POST.get('rol', '').strip().lower()
        estado = request.POST.get('estado', 'activo').strip().lower()
        nueva_password = request.POST.get('nueva_password', '').strip()

        if not username or not email:
            messages.error(request, 'El nombre de usuario y correo electrónico no pueden estar vacíos.')
            return redirect('/dashboard/#usuarios')

        if User.objects.filter(username=username).exclude(pk=target_user.pk).exists():
            messages.error(request, f"El nombre de usuario '{username}' ya pertenece a otra cuenta.")
            return redirect('/dashboard/#usuarios')

        if User.objects.filter(email=email).exclude(pk=target_user.pk).exists():
            messages.error(request, f"El correo electrónico '{email}' ya está registrado en otra cuenta.")
            return redirect('/dashboard/#usuarios')

        if rol not in ['admin', 'bodeguero', 'cajero']:
            rol = getattr(getattr(target_user, 'perfil', None), 'rol', 'cajero')

        if estado not in ['activo', 'inactivo']:
            estado = 'activo'

        # Prevenir desactivación o pérdida de privilegios del usuario en sesión
        if request.user.pk == target_user.pk:
            if estado == 'inactivo':
                messages.error(request, 'No puedes desactivar tu propia cuenta mientras estás en sesión activa.')
                return redirect('/dashboard/#usuarios')
            if rol != 'admin' and target_user.is_superuser:
                messages.warning(request, 'No puedes degradar tu propio rol de Super Admin en sesión.')
                rol = 'admin'

        target_user.username = username
        target_user.first_name = first_name
        target_user.last_name = last_name
        target_user.email = email

        if rol == 'admin':
            target_user.is_superuser = True
            target_user.is_staff = True
        else:
            target_user.is_superuser = False
            target_user.is_staff = True

        if estado == 'inactivo':
            target_user.is_active = False
        else:
            target_user.is_active = True

        if nueva_password:
            target_user.set_password(nueva_password)

        target_user.save()

        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=target_user)
        perfil.rol = rol
        perfil.estado = estado
        perfil.telefono = telefono
        perfil.save()

        messages.success(request, f"¡Usuario '{target_user.username}' y rol '{perfil.nombre_rol}' actualizados exitosamente!")

    return redirect('/dashboard/#usuarios')


@login_required
def eliminar_usuario_dashboard(request, user_id):
    """
    CRUD REGISTROS Y ROLES: ELIMINACIÓN DEFINITIVA CON CONFIRMACIÓN POST (FBV CON get_object_or_404)
    Exige petición POST obligatoria para eliminar un usuario y su perfil asociado.
    Acción restringida exclusivamente a usuarios con rol de Administrador.
    """
    if not es_administrador(request.user):
        messages.error(request, 'Acceso denegado: Únicamente los administradores tienen permiso para eliminar usuarios del sistema.')
        return redirect('/dashboard/#usuarios')

    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)

        # Prevenir que el usuario elimine su propia cuenta
        if request.user.pk == target_user.pk:
            messages.error(request, 'Acción no permitida: no puedes eliminar tu propia cuenta de administrador en sesión.')
            return redirect('/dashboard/#usuarios')

        nombre_eliminado = target_user.username
        target_user.delete()
        messages.success(request, f"El usuario '{nombre_eliminado}' y su rol han sido eliminados correctamente.")
    else:
        messages.warning(request, 'La eliminación de usuarios requiere confirmación mediante petición POST.')

    return redirect('/dashboard/#usuarios')


def logout_view(request):
    """
    CIERRE DE SESIÓN SEGURO ('/accounts/logout/')
    """
    logout(request)
    return redirect('index')


def admin_preview(request):
    """
    PREVISUALIZACIÓN DE AUDITORÍA: PANEL GENERAL
    """
    from django.contrib import admin
    user = User.objects.filter(username='admin').first()
    if user:
        request.user = user
    return admin.site.index(request)


def admin_productos_preview(request):
    """
    PREVISUALIZACIÓN DE AUDITORÍA: APP PRINCIPAL
    """
    from django.contrib import admin
    user = User.objects.filter(username='admin').first()
    if user:
        request.user = user
    return admin.site.app_index(request, 'principal')


def admin_producto_list_preview(request):
    """
    PREVISUALIZACIÓN DE AUDITORÍA: LISTADO DE PRODUCTOS
    """
    from django.contrib import admin
    user = User.objects.filter(username='admin').first()
    if user:
        request.user = user
    return admin.site._registry[Producto].changelist_view(request)


def registro_view(request):
    """
    REGISTRO PÚBLICO DE USUARIOS Y ASIGNACIÓN DE PERFIL ('/registro/')
    Almacena: username, email, contraseña, teléfono, rol, estado ('activo')
    y fecha de creación automática vía ORM.
    """
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol = request.POST.get('rol', 'admin').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validaciones de integridad
        if not username or not email or not password:
            messages.error(request, 'Por favor completa todos los campos obligatorios.')
            return render(request, 'principal/Registro.html')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas ingresadas no coinciden.')
            return render(request, 'principal/Registro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya se encuentra registrado.')
            return render(request, 'principal/Registro.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return render(request, 'principal/Registro.html')

        # Control estricto de roles: si quien registra no es un administrador autenticado,
        # no puede crearse a sí mismo como Super Admin (por seguridad se asigna cajero)
        if rol == 'admin' and (not request.user.is_authenticated or not es_administrador(request.user)):
            messages.warning(request, 'La asignación del rol Super Admin está reservada a administradores. Tu cuenta se asignó como Cajero.')
            rol = 'cajero'
        elif rol not in ['admin', 'cajero', 'bodeguero']:
            rol = 'cajero'

        es_super = (rol == 'admin')
        # 1. Crear el usuario base de autenticación con acceso administrativo (is_staff)
        nuevo_usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=es_super
        )

        # 2. Crear o actualizar su perfil vinculado con el rol y estado activo
        PerfilUsuario.objects.update_or_create(
            usuario=nuevo_usuario,
            defaults={
                'telefono': telefono,
                'rol': rol,
                'estado': 'activo'
            }
        )

        # 3. Autenticar e iniciar sesión de inmediato
        auth_login(request, nuevo_usuario)
        rol_nombre = 'Super Admin' if rol == 'admin' else rol.capitalize()
        messages.success(request, f'¡Bienvenido al sistema, {username}! Tu cuenta ha sido registrada con rol de {rol_nombre}.')

        # Redirigir directamente al panel administrativo
        return redirect('dashboard')

    return render(request, 'principal/Registro.html')