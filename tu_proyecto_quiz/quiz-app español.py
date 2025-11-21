"""
RESPONDIDOS - APLICACIÓN DE PREGUNTAS Y RESPUESTAS - ESTILO KAHOOT
Versión sin clases - Enfoque procedural
Con temporizador, barra de tiempo y sistema de ayudas
"""

# IMPORTACIONES: traen librerías necesarias para el programa
import json  # Para leer/escribir archivos JSON
import random  # Para mezclar preguntas aleatoriamente
from tkinter import *  # Importa todos los widgets de tkinter para interfaz gráfica
from tkinter import messagebox  # Para mostrar ventanas emergentes de mensajes
from tkinter import ttk  # Para widgets más modernos (Combobox, Button mejorados)
import os  # Para manejo de rutas de archivos y directorios

# === SECCIÓN 1: CONFIGURACIÓN Y CARGA DE DATOS ===

# DICCIONARIO QUE MAPEA NOMBRES DE CATEGORÍAS CON SUS ARCHIVOS JSON
MAPA_ARCHIVOS = {
    "Peliculas y Series": "PeliSeries.json",  # Clave: nombre que verá el usuario | Valor: archivo JSON
    "Ciencia": "Ciencia.json",
    "Videojuegos": "Videojuegos.json",
    "Historia": "Historia.json",
    "Música": "Musica.json",
    "Futbol": "Futbol.json",
    "Star Wars": "StarWars.json",
    "Rainbow Six Siege": "RainbowSixSiege.json"
}

# VARIABLES GLOBALES: guardan el estado actual del juego (accesibles en toda la aplicación)
preguntas_actuales = []  # Lista de 10 preguntas de la categoría actual
indice_pregunta_actual = 0  # Índice de la pregunta que se está mostrando (0 = primera pregunta)
puntaje = 0  # Puntaje del jugador (contador de respuestas correctas)
categoria_actual = None  # Categoría seleccionada actualmente
datos_todas_preguntas = {}  # Diccionario con todas las preguntas: {"Cine": [...], "Música": [...], etc}
botones_actuales = []  # Lista de botones de opciones para poder modificarlos después
temporizador_activo = False  # Booleano: ¿está corriendo el temporizador?
tiempo_restante = 15  # Segundos restantes para responder la pregunta
id_temporizador = None  # ID del timer para poder detenerlo si es necesario
ayudas_restantes = 2  # Cantidad de ayudas disponibles en el quiz actual (máximo 2)
ayuda_usada_esta_pregunta = False  # Booleano: ¿ya usó ayuda en esta pregunta?

NUMERO_PREGUNTAS = 10  # Cantidad de preguntas por quiz (constante)

# DICCIONARIO DE COLORES: define los colores del diseño
PALETA_COLORES = {
    "FONDO_CLARO": "#d4d4d4",  # Color de fondo gris claro
    "TEXTO_PRINCIPAL": "#1f2937",  # Texto principal gris oscuro
    "TEXTO_SECUNDARIO": "#6b7280",  # Texto secundario gris medio
    "EXITO": "#10b981",  # Verde para respuestas correctas
    "ERROR": "#ef4444",  # Rojo para respuestas incorrectas
    "ADVERTENCIA": "#f59e0b",  # Amarillo para advertencias
    "AYUDA": "#8B5CF6"  # Morado para botón de ayuda
}

# DICCIONARIO DE COLORES POR CATEGORÍA: cada categoría tiene sus propios colores e icono
COLORES_CATEGORIAS = {
    "Peliculas y Series": {"bg": "#FFCC99", "hover": "#FFB880", "icon": "🎬", "fg": "#333"},  # Fondo naranja
    "Ciencia": {"bg": "#B3E0B3", "hover": "#99CC99", "icon": "🔬", "fg": "#333"},  # Fondo verde
    "Videojuegos": {"bg": "#FFA0A0", "hover": "#FF8080", "icon": "🎮", "fg": "#333"},  # Fondo rojo
    "Historia": {"bg": "#F3DFA2", "hover": "#EAC36E", "icon": "🏛️", "fg": "#2D2D2D"},  # Fondo amarillo
    "Música": {"bg": "#DDA0DD", "hover": "#CC88CC", "icon": "🎵", "fg": "#333"},  # Fondo magenta
    "Futbol": {"bg": "#99CC99", "hover": "#80B380", "icon": "⚽", "fg": "#333"},  # Fondo verde
    "Star Wars": {"bg": "#ADD8E6", "hover": "#87CEEB", "icon": "🌌", "fg": "#191970"},  # Fondo azul
    "Rainbow Six Siege": {"bg": "#C0C0C0", "hover": "#A9A9A9", "icon": "🎯", "fg": "#000000"},  # Fondo gris
}

# FUNCIÓN: obtiene la carpeta donde está guardado el programa
def directorio_script():
    return os.path.dirname(os.path.abspath(__file__))  # Devuelve la ruta de la carpeta actual

# FUNCIÓN: carga todas las preguntas desde los archivos JSON al iniciar
def cargar_preguntas(mapa_archivos):
    """
    Lee los archivos JSON de cada categoría y carga todas las preguntas en memoria.
    Devuelve un diccionario: {"Cine": [pregunta1, pregunta2...], "Música": [...], etc}
    """
    todos_datos = {}  # Diccionario vacío donde guardaremos todas las preguntas
    base = directorio_script()  # Obtiene la ruta base donde está el programa
    
    for nombre_categoria, nombre_archivo in mapa_archivos.items():  # Recorre cada categoría y su archivo
        ruta = os.path.join(base, nombre_archivo)  # Construye la ruta completa del archivo JSON
        try:
            with open(ruta, "r", encoding="utf-8") as f:  # Abre el archivo en modo lectura
                datos = json.load(f)  # Convierte el JSON a una lista de Python
                if isinstance(datos, list) and datos:  # Verifica que sea una lista no vacía
                    todos_datos[nombre_categoria] = datos  # Guarda las preguntas en el diccionario
                else:
                    todos_datos[nombre_categoria] = datos if isinstance(datos, list) else []  # Si no es lista, vacío
        except FileNotFoundError:  # Si el archivo no existe
            try:
                with open(ruta, "w", encoding="utf-8") as f:  # Crea el archivo vacío
                    json.dump([], f, ensure_ascii=False, indent=2)  # Escribe una lista vacía
                todos_datos[nombre_categoria] = []  # Añade categoría vacía al diccionario
            except Exception as e:  # Si hay error al crear el archivo
                print(f"No se pudo crear {nombre_archivo}: {e}")  # Imprime el error
        except json.JSONDecodeError:  # Si el JSON está mal formado
            print(f"JSON inválido en {nombre_archivo}.")  # Imprime el error
            todos_datos[nombre_categoria] = []  # Añade categoría vacía
        except Exception as e:  # Cualquier otro error
            print(f"Error cargando {nombre_archivo}: {e}")  # Imprime el error
            todos_datos[nombre_categoria] = []  # Añade categoría vacía
    return todos_datos  # Devuelve el diccionario completo de todas las preguntas

# FUNCIÓN: guarda una nueva pregunta en el archivo JSON de la categoría
def guardar_pregunta_en_json(categoria, nueva_pregunta):
    """
    Añade una pregunta nueva al final del archivo JSON de una categoría.
    La pregunta tiene: pregunta, opciones, respuestaCorrecta
    """
    base = directorio_script()  # Obtiene la ruta base
    if categoria not in MAPA_ARCHIVOS:  # Verifica que la categoría exista en MAPA_ARCHIVOS
        return False, "Categoría desconocida."  # Devuelve error si no existe
    
    ruta = os.path.join(base, MAPA_ARCHIVOS[categoria])  # Construye la ruta del archivo
    try:
        with open(ruta, "r", encoding="utf-8") as f:  # Abre el archivo para leer
            existentes = json.load(f)  # Carga las preguntas existentes
            if not isinstance(existentes, list):  # Si no es una lista
                existentes = []  # Inicia como lista vacía
    except Exception:
        existentes = []  # Si hay error, crea lista vacía
    
    existentes.append(nueva_pregunta)  # Añade la nueva pregunta a la lista
    try:
        with open(ruta, "w", encoding="utf-8") as f:  # Abre el archivo para escribir (sobrescribe)
            json.dump(existentes, f, ensure_ascii=False, indent=2)  # Convierte lista a JSON y guarda
        return True, None  # Devuelve éxito
    except Exception as e:  # Si hay error al guardar
        return False, str(e)  # Devuelve el error

# === SECCIÓN 2: LÓGICA DEL QUIZ ===

# FUNCIÓN: inicia un nuevo quiz con la categoría seleccionada
def iniciar_quiz(categoria):
    """
    Prepara el quiz: obtiene 10 preguntas al azar de la categoría,
    resetea puntaje, temporizador y otras variables de estado.
    """
    global preguntas_actuales, indice_pregunta_actual, puntaje, categoria_actual, tiempo_restante, ayudas_restantes, ayuda_usada_esta_pregunta
    
    # Verifica que la categoría tenga suficientes preguntas (mínimo 10)
    if categoria not in datos_todas_preguntas or not isinstance(datos_todas_preguntas[categoria], list) or not datos_todas_preguntas[categoria] or len(datos_todas_preguntas[categoria]) < NUMERO_PREGUNTAS:
        return False  # Devuelve False si no hay suficientes preguntas
    
    categoria_actual = categoria  # Guarda la categoría actual
    puntaje = 0  # Resetea el puntaje a 0
    indice_pregunta_actual = 0  # Empieza en la primera pregunta
    tiempo_restante = 15  # Inicializa el temporizador a 15 segundos
    ayudas_restantes = 2  # Permite 2 ayudas por quiz
    ayuda_usada_esta_pregunta = False  # Aún no usó ayuda en esta pregunta
    
    preguntas = list(datos_todas_preguntas[categoria])  # Copia la lista de preguntas
    random.shuffle(preguntas)  # Las mezcla aleatoriamente
    preguntas_actuales = preguntas[:NUMERO_PREGUNTAS]  # Toma solo las primeras 10
    return True  # Devuelve True indicando que el quiz comenzó

# FUNCIÓN: obtiene la pregunta que se está mostrando actualmente
def obtener_pregunta_actual():
    """
    Devuelve el diccionario de la pregunta actual (pregunta, opciones, respuestaCorrecta).
    Si no hay más preguntas, devuelve None.
    """
    if indice_pregunta_actual < len(preguntas_actuales):  # Verifica que el índice sea válido
        return preguntas_actuales[indice_pregunta_actual]  # Devuelve la pregunta actual
    return None  # Devuelve None si ya terminaron las preguntas

# FUNCIÓN: verifica si la respuesta seleccionada es correcta
def verificar_respuesta(indice_opcion_seleccionada):
    """
    Compara la opción seleccionada con la respuesta correcta.
    Si es correcta, suma 1 al puntaje.
    Devuelve True si es correcta, False si es incorrecta.
    """
    global puntaje  # Accede a la variable global puntaje
    
    q = obtener_pregunta_actual()  # Obtiene la pregunta actual
    if not q:  # Si no hay pregunta
        return False  # Devuelve False
    try:
        respuesta_correcta = q["respuestaCorrecta"]  # Obtiene la respuesta correcta (texto)
        indice_correcto = q["opciones"].index(respuesta_correcta)  # Obtiene el índice de esa respuesta
    except Exception:
        return False  # Devuelve False si hay error
    
    correcto = (indice_opcion_seleccionada == indice_correcto)  # Verifica si coinciden los índices
    if correcto:  # Si es correcta
        puntaje += 1  # Suma 1 al puntaje
    return correcto  # Devuelve True o False

# FUNCIÓN: avanza a la siguiente pregunta
def siguiente_pregunta():
    """
    Incrementa el índice de la pregunta actual y resetea el temporizador.
    Devuelve True si hay más preguntas, False si ya terminaron.
    """
    global indice_pregunta_actual, tiempo_restante, ayuda_usada_esta_pregunta
    indice_pregunta_actual += 1  # Incrementa el índice
    tiempo_restante = 15  # Resetea el temporizador
    ayuda_usada_esta_pregunta = False  # Permite usar ayuda nuevamente
    return indice_pregunta_actual < len(preguntas_actuales)  # Devuelve True si hay más preguntas

# FUNCIÓN: obtiene los resultados finales del quiz
def obtener_resultados():
    """
    Devuelve una tupla (puntaje_actual, total_preguntas) para calcular el porcentaje.
    """
    return puntaje, len(preguntas_actuales)  # Devuelve puntaje y total de preguntas

# === SECCIÓN 3: TEMPORIZADOR Y BARRA DE TIEMPO ===

# FUNCIÓN: inicia el temporizador de 15 segundos
def iniciar_temporizador():
    """
    Activa el temporizador, lo setea a 15 segundos y comienza a contar.
    """
    global temporizador_activo, tiempo_restante, id_temporizador
    temporizador_activo = True  # Marca que el temporizador está corriendo
    tiempo_restante = 15  # Inicializa a 15 segundos
    actualizar_visualizacion_temporizador()  # Actualiza la visualización en la interfaz
    actualizar_barra_tiempo()  # Actualiza la barra de tiempo
    id_temporizador = ventana_principal.after(1000, actualizar_temporizador)  # Llama a actualizar_temporizador en 1000ms (1 segundo)

# FUNCIÓN: detiene el temporizador
def detener_temporizador():
    """
    Detiene el temporizador. Se usa cuando se responde una pregunta o se vuelve al menú.
    """
    global temporizador_activo, id_temporizador
    temporizador_activo = False  # Marca que el temporizador está detenido
    if id_temporizador:  # Si hay un id_temporizador
        ventana_principal.after_cancel(id_temporizador)  # Cancela la ejecución programada
        id_temporizador = None  # Limpia el ID

# FUNCIÓN: actualiza el temporizador cada segundo
def actualizar_temporizador():
    """
    Se ejecuta cada segundo mientras temporizador_activo sea True.
    Decrementa tiempo_restante, actualiza la pantalla y llama a tiempo_agotado() si llegó a 0.
    """
    global tiempo_restante, temporizador_activo, id_temporizador
    
    if not temporizador_activo:  # Si el temporizador no está corriendo
        return  # Sale de la función
        
    tiempo_restante -= 1  # Resta 1 segundo
    actualizar_visualizacion_temporizador()  # Actualiza el texto del temporizador
    actualizar_barra_tiempo()  # Actualiza la barra de progreso
    
    if tiempo_restante <= 0:  # Si se acabó el tiempo
        detener_temporizador()  # Detiene el temporizador
        tiempo_agotado()  # Ejecuta la función de tiempo agotado
    else:
        id_temporizador = ventana_principal.after(1000, actualizar_temporizador)  # Programa la siguiente ejecución en 1 segundo

# FUNCIÓN: actualiza el texto que muestra los segundos restantes
def actualizar_visualizacion_temporizador():
    """
    Cambia el texto del label que muestra "⏱️ 15s", "⏱️ 14s", etc.
    Cambia el color a verde si hay > 5 segundos, rojo si hay <= 5 segundos.
    """
    if hasattr(actualizar_visualizacion_temporizador, 'etiqueta_temporizador') and actualizar_visualizacion_temporizador.etiqueta_temporizador:  # Verifica que exista el label
        color = PALETA_COLORES["EXITO"] if tiempo_restante > 5 else PALETA_COLORES["ERROR"]  # Verde si >5s, rojo si <=5s
        actualizar_visualizacion_temporizador.etiqueta_temporizador.config(text=f"⏱️ {tiempo_restante}s", fg=color)  # Actualiza el texto y color

# FUNCIÓN: actualiza la barra de tiempo horizontal
def actualizar_barra_tiempo():
    """
    Dibuja una barra que se va encogiendo de derecha a izquierda mientras pasan los segundos.
    Cambia de color: verde (>5s) → amarillo (>2s) → rojo (<=2s).
    """
    if hasattr(actualizar_barra_tiempo, 'canvas_barra_tiempo') and actualizar_barra_tiempo.canvas_barra_tiempo:  # Verifica que exista el canvas
        porcentaje = (tiempo_restante / 15) * 100  # Calcula qué porcentaje del tiempo queda (0-100%)
        
        # Elige color según el tiempo restante
        if tiempo_restante > 5:
            color = PALETA_COLORES["EXITO"]  # Verde si quedan > 5 segundos
        elif tiempo_restante > 2:
            color = PALETA_COLORES["ADVERTENCIA"]  # Amarillo si quedan entre 2 y 5 segundos
        else:
            color = PALETA_COLORES["ERROR"]  # Rojo si quedan <= 2 segundos
        
        ancho_barra = (porcentaje / 100) * 860  # Calcula el ancho de la barra (860 es el ancho total)
        inicio_x = 860 - ancho_barra  # Calcula desde dónde empezar la barra (de derecha a izquierda)
        actualizar_barra_tiempo.canvas_barra_tiempo.coords(actualizar_barra_tiempo.rectangulo_barra_tiempo, inicio_x, 0, 860, 10)  # Actualiza las coordenadas
        actualizar_barra_tiempo.canvas_barra_tiempo.itemconfig(actualizar_barra_tiempo.rectangulo_barra_tiempo, fill=color)  # Cambia el color

# FUNCIÓN: crea la barra de tiempo horizontal visual
def crear_barra_tiempo(padre):
    """
    Dibuja un canvas con una barra rectangular que representa el tiempo.
    Esta barra se va achicando a medida que pasan los segundos.
    """
    contenedor_barra_tiempo = Frame(padre, bg=PALETA_COLORES["FONDO_CLARO"], height=15)  # Frame contenedor
    contenedor_barra_tiempo.pack(fill="x", padx=20, pady=(0, 0))  # Lo empaqueta
    
    actualizar_barra_tiempo.canvas_barra_tiempo = Canvas(contenedor_barra_tiempo, height=10, bg="#e5e7eb", highlightthickness=0, width=860)  # Canvas para dibujar
    actualizar_barra_tiempo.canvas_barra_tiempo.pack(fill="x", padx=0)  # Lo empaqueta
    
    actualizar_barra_tiempo.rectangulo_barra_tiempo = actualizar_barra_tiempo.canvas_barra_tiempo.create_rectangle(0, 0, 860, 10, fill=PALETA_COLORES["EXITO"], outline="")  # Dibuja el rectángulo

# FUNCIÓN: maneja cuando se acaba el tiempo
def tiempo_agotado():
    """
    Cuando tiempo_restante llega a 0, deshabilita los botones, muestra la respuesta correcta,
    y avanza automáticamente a la siguiente pregunta después de 2 segundos.
    """
    global botones_actuales
    
    for b in botones_actuales:  # Recorre todos los botones de opciones
        b.config(state="disabled")  # Los deshabilita para que no se puedan presionar
    
    if hasattr(cargar_interfaz_pregunta, 'boton_ayuda'):  # Si existe el botón de ayuda
        cargar_interfaz_pregunta.boton_ayuda.config(state="disabled")  # Lo deshabilita
    
    q = obtener_pregunta_actual()  # Obtiene la pregunta actual
    if not q:
        return  # Si no hay pregunta, sale
        
    respuesta_correcta = q.get("respuestaCorrecta", "")  # Obtiene la respuesta correcta
    
    for b in botones_actuales:  # Recorre todos los botones
        texto = b.cget("text")  # Obtiene el texto del botón
        if texto == respuesta_correcta:
            b.config(bg=PALETA_COLORES["EXITO"], fg="white")  # Colorea la correcta de verde
        else:
            b.config(bg=PALETA_COLORES["ERROR"])  # Colorea las incorrectas de rojo
    
    if hasattr(cargar_interfaz_pregunta, 'etiqueta_pregunta'):  # Si existe el label de la pregunta
        cargar_interfaz_pregunta.etiqueta_pregunta.config(text="⏰ TIEMPO AGOTADO", bg=PALETA_COLORES["ERROR"])  # Muestra "TIEMPO AGOTADO"
    
    ventana_principal.after(2000, avanzar_despues_tiempo_agotado)  # Después de 2 segundos, avanza

# FUNCIÓN: avanza a la siguiente pregunta después de que se agote el tiempo
def avanzar_despues_tiempo_agotado():
    """
    Se ejecuta 2 segundos después de que tiempo_restante llegue a 0.
    Avanza a la siguiente pregunta o muestra los resultados si ya terminó.
    """
    if siguiente_pregunta():  # Si hay más preguntas
        cargar_interfaz_pregunta()  # Carga la siguiente pregunta
    else:
        mostrar_interfaz_resultados()  # Si no, muestra los resultados

# === SECCIÓN 4: SISTEMA DE AYUDAS ===

# FUNCIÓN: usa una ayuda para eliminar 2 opciones incorrectas
def usar_ayuda():
    """
    Elimina 2 opciones incorrectas aleatorias (mostradas en gris).
    Solo se puede usar 1 ayuda por pregunta y máximo 2 por quiz.
    """
    global ayudas_restantes, ayuda_usada_esta_pregunta, botones_actuales
    
    if ayudas_restantes <= 0 or ayuda_usada_esta_pregunta:  # Si no quedan ayudas o ya usó una en esta pregunta
        return  # Sale de la función
        
    ayudas_restantes -= 1  # Decrementa las ayudas disponibles
    ayuda_usada_esta_pregunta = True  # Marca que ya usó ayuda en esta pregunta
    
    if hasattr(cargar_interfaz_pregunta, 'boton_ayuda'):  # Si existe el botón de ayuda
        if ayudas_restantes > 0:
            cargar_interfaz_pregunta.boton_ayuda.config(text=f"❓ Ayuda ({ayudas_restantes} restantes)", state="normal")  # Actualiza el texto
        else:
            cargar_interfaz_pregunta.boton_ayuda.config(text="❓ Ayudas agotadas", state="disabled")  # Si no quedan, lo deshabilita
    
    q = obtener_pregunta_actual()  # Obtiene la pregunta actual
    if not q:
        return  # Si no hay pregunta, sale
        
    respuesta_correcta = q.get("respuestaCorrecta", "")  # Obtiene la respuesta correcta
    
    indices_incorrectos = []  # Lista para guardar los índices de respuestas incorrectas
    for i, boton in enumerate(botones_actuales):  # Recorre todos los botones
        if boton.cget("text") != respuesta_correcta and boton.cget("state") == "normal":  # Si es incorrecta y está habilitada
            indices_incorrectos.append(i)  # Añade su índice a la lista
    
    if len(indices_incorrectos) >= 2:  # Si hay 2 o más opciones incorrectas
        random.shuffle(indices_incorrectos)  # Las mezcla aleatoriamente
        a_eliminar = indices_incorrectos[:2]  # Toma las primeras 2
        
        for indice in a_eliminar:  # Recorre los índices a eliminar
            botones_actuales[indice].config(state="disabled", bg="#666666", fg="#999999", text="❌ Eliminada")  # Las deshabilita y cambia de color
    
    elif len(indices_incorrectos) == 1:  # Si solo hay 1 opción incorrecta
        botones_actuales[indices_incorrectos[0]].config(state="disabled", bg="#666666", fg="#999999", text="❌ Eliminada")  # La elimina

# === SECCIÓN 5: INTERFAZ GRÁFICA (TKINTER) ===

# VARIABLES GLOBALES para almacenar los frames (paneles) de la interfaz
marco_contenido_principal = None  # Frame principal que contiene todos los demás
marco_categorias = None  # Frame para mostrar las categorías disponibles
marco_quiz = None  # Frame para mostrar las preguntas del quiz
marco_resultados = None  # Frame para mostrar los resultados finales
marco_agregar_pregunta = None  # Frame para agregar nuevas preguntas

# CONSTANTES para tamaño de botones
RELLENO_BOTON_NORMAL = 20  # Padding de los botones en píxeles
ANCHO_BOTON_FIJO = 35  # Ancho fijo de los botones
ALTO_BOTON_FIJO = 4  # Altura fija de los botones
LONGITUD_SALTO_BOTON = 350  # Ancho máximo antes de saltar a la siguiente línea

# FUENTES: define los estilos de texto a usar en la interfaz
fuente_titulo = ("Inter", 28, "bold")  # Título grande y negrita
fuente_grande = ("Inter", 18, "bold")  # Texto grande y negrita
fuente_mediana = ("Inter", 12)  # Texto mediano normal
fuente_pequena = ("Inter", 10)  # Texto pequeño normal

# FUNCIÓN: limpia todos los frames (los oculta)
def limpiar_todos_los_frames():
    """
    Usa pack_forget() para ocultar todos los frames de contenido.
    Esto permite mostrar uno a la vez sin que se superpongan.
    """
    for f in [marco_categorias, marco_quiz, marco_resultados, marco_agregar_pregunta]:  # Recorre todos los frames
        if f:  # Si el frame existe
            f.pack_forget()  # Lo oculta

# FUNCIÓN: crea un tooltip (pequeña ventana de ayuda)
def crear_tooltip(widget, texto):
    """
    Cuando pasas el mouse sobre el widget, muestra un pequeño popup con texto de ayuda.
    Desaparece cuando sacas el mouse.
    """
    ventana_tooltip = None  # Variable para guardar la ventana del tooltip
    
    def entrar(event):  # Se ejecuta cuando el mouse entra al widget
        nonlocal ventana_tooltip  # Permite modificar ventana_tooltip
        x, y, _, _ = widget.bbox("insert")  # Obtiene la posición del widget
        x += widget.winfo_rootx() + 25  # Suma offset para el tooltip
        y += widget.winfo_rooty() + 25  # Suma offset para el tooltip
        ventana_tooltip = Toplevel(widget)  # Crea una ventana nueva
        ventana_tooltip.wm_overrideredirect(True)  # Ventana sin decoraciones
        ventana_tooltip.wm_geometry(f"+{x}+{y}")  # Posiciona la ventana
        Label(ventana_tooltip, text=texto, background="#ffffe0", relief="solid", borderwidth=1, font=("tahoma", "8", "normal")).pack()  # Añade el texto
    
    def salir(event):  # Se ejecuta cuando el mouse sale del widget
        nonlocal ventana_tooltip  # Permite modificar ventana_tooltip
        if ventana_tooltip:  # Si la ventana del tooltip existe
            ventana_tooltip.destroy()  # La elimina
            ventana_tooltip = None  # Resetea la variable
    
    widget.bind("<Enter>", entrar)  # Vincula evento "Enter" a la función entrar
    widget.bind("<Leave>", salir)  # Vincula evento "Leave" a la función salir

# FUNCIÓN: muestra la pantalla de selección de categorías
def mostrar_seleccion_categorias():
    """
    Limpia la interfaz y muestra los 8 botones de categorías.
    Cada botón tiene su color, icono y número de preguntas.
    """
    detener_temporizador()  # Detiene cualquier temporizador activo
    limpiar_todos_los_frames()  # Oculta todos los frames anteriores
    marco_categorias.pack(fill="both", expand=True)  # Muestra el frame de categorías

    Label(marco_categorias, text=f"Cada quiz tiene {NUMERO_PREGUNTAS} preguntas", font=fuente_mediana,
          bg=PALETA_COLORES["FONDO_CLARO"], fg=PALETA_COLORES["TEXTO_SECUNDARIO"]).pack(pady=4)  # Texto informativo

    grid = Frame(marco_categorias, bg=PALETA_COLORES["FONDO_CLARO"])  # Frame para el grid de categorías
    grid.pack(expand=True, fill="both", pady=10)  # Lo empaqueta

    categorias = list(dict.fromkeys(list(COLORES_CATEGORIAS.keys()) + list(datos_todas_preguntas.keys())))  # Obtiene lista de categorías sin duplicados

    for i, cat in enumerate(categorias):  # Recorre cada categoría con su índice
        colores = COLORES_CATEGORIAS.get(cat, {"bg": "#DDDDDD", "hover": "#CCCCCC", "icon": "❓", "fg": "#111"})  # Obtiene colores de la categoría
        num_p = len(datos_todas_preguntas.get(cat, []))  # Cuenta cuántas preguntas tiene
        tiene_preguntas = num_p >= NUMERO_PREGUNTAS  # Verifica si tiene suficientes preguntas

        estado_boton = "normal" if tiene_preguntas else "disabled"  # Estado del botón (habilitado o deshabilitado)
        texto_tooltip = ""
        if not tiene_preguntas:
             texto_tooltip = f"Faltan preguntas para el quiz ({num_p}/{NUMERO_PREGUNTAS})"  # Mensaje de tooltip

        btn = Button(grid, text=f"{colores['icon']}  {cat}", font=fuente_grande,  # Crea botón con icono y nombre
                     bg=colores["bg"], fg=colores["fg"], activebackground=colores["hover"],  # Colores del botón
                     relief="flat", bd=0, padx=30, pady=18, state=estado_boton,
                     command=lambda c=cat: iniciar_interfaz_quiz(c))  # Función al hacer clic
        btn.grid(row=i // 2, column=i % 2, padx=16, pady=16, sticky="nsew")  # Posiciona el botón en grid 2x4

        if not tiene_preguntas:
            crear_tooltip(btn, texto_tooltip)  # Crea tooltip si faltan preguntas

    for i in range(2):
        grid.grid_columnconfigure(i, weight=1)  # Configura las columnas para que se expandan

    Button(marco_categorias, text="➕ Agregar Pregunta", font=fuente_mediana,  # Botón para agregar pregunta
           bg="#4CAF50", fg="white", activebackground="#45a049", relief="flat", bd=0, padx=12, pady=10,
           command=mostrar_interfaz_agregar_pregunta).pack(pady=8)

# FUNCIÓN: inicia la interfaz del quiz
def iniciar_interfaz_quiz(categoria):
    """
    Verifica que haya suficientes preguntas, inicia el quiz y muestra la primera pregunta.
    """
    if iniciar_quiz(categoria):  # Si el quiz se inició correctamente
        limpiar_todos_los_frames()  # Oculta otros frames
        marco_quiz.pack(fill="both", expand=True)  # Muestra el frame del quiz
        cargar_interfaz_pregunta()  # Carga y muestra la primera pregunta
    else:
        messagebox.showerror("Error", f"No hay suficientes preguntas disponibles para esta categoría. Necesitas {NUMERO_PREGUNTAS}.")  # Muestra error

# FUNCIÓN: carga y muestra la pregunta actual
def cargar_interfaz_pregunta():
    """
    Borra la interfaz anterior y dibuja: encabezado, pregunta, 4 opciones, botón de ayuda y barra de tiempo.
    """
    global botones_actuales
    
    for w in marco_quiz.winfo_children():  # Recorre todos los widgets del frame
        w.destroy()  # Los elimina
    
    botones_actuales = []  # Reinicia la lista de botones
    detener_temporizador()  # Detiene el temporizador anterior

    pregunta = obtener_pregunta_actual()  # Obtiene la pregunta actual
    if not pregunta:  # Si no hay pregunta
        mostrar_interfaz_resultados()  # Muestra los resultados
        return

    info_cat = COLORES_CATEGORIAS.get(categoria_actual, {"hover": "#888", "icon": "?"})  # Obtiene colores de la categoría
    
    encabezado = Frame(marco_quiz, bg=PALETA_COLORES["FONDO_CLARO"])  # Frame del encabezado
    encabezado.pack(fill="x")
    
    Button(encabezado, text="← Categorías", command=mostrar_seleccion_categorias,  # Botón para volver a categorías
           relief="flat", bd=0, bg=PALETA_COLORES["FONDO_CLARO"]).pack(side=LEFT, padx=5)
    
    actualizar_visualizacion_temporizador.etiqueta_temporizador = Label(encabezado, text=f"⏱️ {tiempo_restante}s", font=fuente_mediana,  # Label del temporizador
                                            bg=PALETA_COLORES["FONDO_CLARO"], fg=PALETA_COLORES["EXITO"])
    actualizar_visualizacion_temporizador.etiqueta_temporizador.pack(side=RIGHT, padx=8)
    
    Label(encabezado, text=f"Puntaje: {puntaje}/{NUMERO_PREGUNTAS}", font=fuente_mediana,  # Label del puntaje
          bg=PALETA_COLORES["FONDO_CLARO"], fg=PALETA_COLORES["EXITO"]).pack(side=RIGHT, padx=8)
    
    Label(encabezado, text=f"{info_cat.get('icon','')}  {categoria_actual}", font=fuente_mediana,  # Label de la categoría
          bg=PALETA_COLORES["FONDO_CLARO"]).pack(side=RIGHT, padx=8)

    Label(marco_quiz, text=f"Pregunta {indice_pregunta_actual + 1} de {NUMERO_PREGUNTAS}",  # Contador de pregunta
          font=fuente_pequena, bg=PALETA_COLORES["FONDO_CLARO"], fg=PALETA_COLORES["TEXTO_SECUNDARIO"]).pack()

    contenedor_pregunta = Frame(marco_quiz, bg=info_cat["hover"], height=150)  # Frame para la pregunta
    contenedor_pregunta.pack(pady=12, fill="x", padx=20) 
    contenedor_pregunta.pack_propagate(False)  # Mantiene el tamaño fijo

    cargar_interfaz_pregunta.etiqueta_pregunta = Label(contenedor_pregunta, text=pregunta["pregunta"], font=fuente_grande,  # Label de la pregunta
          bg=info_cat["hover"], fg="white", wraplength=750, justify=CENTER)
    cargar_interfaz_pregunta.etiqueta_pregunta.pack(expand=True, padx=20, pady=20)

    crear_barra_tiempo(contenedor_pregunta)  # Crea la barra de tiempo

    marco_opciones = Frame(marco_quiz, bg=PALETA_COLORES["FONDO_CLARO"])  # Frame para las opciones
    marco_opciones.pack(fill="both", expand=False, pady=10)

    colores_kahoot = ["#E74C3C", "#3498DB", "#F1C40F", "#2ECC71"]  # Colores para las 4 opciones (rojo, azul, amarillo, verde)
    opciones_mezcladas = random.sample(pregunta["opciones"], len(pregunta["opciones"]))  # Mezcla las opciones aleatoriamente
    botones_actuales = []

    altura_pantalla = ventana_principal.winfo_screenheight() if ventana_principal else 900  # Obtiene la altura de la pantalla
    # Ajusta tamaño de botones según la altura de pantalla
    if altura_pantalla < 800:
        ancho_b = 26
        alto_b = 2
        salto_b = 250
        relleno_b = 8
    elif altura_pantalla < 1000:
        ancho_b = 30
        alto_b = 3
        salto_b = 300
        relleno_b = 12
    else:
        ancho_b = 35
        alto_b = 4
        salto_b = 350
        relleno_b = 20

    for i, texto_opcion in enumerate(opciones_mezcladas):  # Recorre cada opción
        try:
            indice_original = pregunta["opciones"].index(texto_opcion)  # Obtiene el índice original en el JSON
        except ValueError:
            indice_original = -1

        color_boton = colores_kahoot[i % len(colores_kahoot)]  # Asigna color a la opción

        btn = Button(marco_opciones, text=texto_opcion, font=("Inter", 14, "bold"),  # Crea botón de opción
                     bg=color_boton, fg="white", activeforeground="white",
                     wraplength=salto_b,
                     width=ancho_b,
                     height=alto_b,
                     relief="flat", bd=0,
                     padx=relleno_b, pady=relleno_b,
                     command=lambda idx=indice_original, opt=texto_opcion: manejar_respuesta(idx, opt))  # Al hacer clic, ejecuta manejar_respuesta

        btn.grid(row=i // 2, column=i % 2, padx=12, pady=12, sticky="nsew")  # Posiciona en grid 2x2

        botones_actuales.append(btn)  # Añade el botón a la lista global

    for col in range(2):
        marco_opciones.grid_columnconfigure(col, weight=1)  # Configura columnas

    marco_ayuda = Frame(marco_quiz, bg=PALETA_COLORES["FONDO_CLARO"])  # Frame para el botón de ayuda
    marco_ayuda.pack(pady=15)
    
    texto_boton_ayuda = f"❓ Ayuda ({ayudas_restantes} restantes)"
    cargar_interfaz_pregunta.boton_ayuda = Button(marco_ayuda, text=texto_boton_ayuda, font=("Inter", 14, "bold"),  # Botón de ayuda
                                         bg=PALETA_COLORES["AYUDA"], fg="white", 
                                         activebackground="#7C3AED", activeforeground="white",
                                         relief="flat", bd=0, padx=25, pady=15,
                                         command=usar_ayuda)
    cargar_interfaz_pregunta.boton_ayuda.pack()

    iniciar_temporizador()  # Inicia el temporizador de 15 segundos

# FUNCIÓN: maneja la selección de una respuesta
def manejar_respuesta(indice_opcion_seleccionada, texto_opcion_seleccionada):
    """
    Se ejecuta cuando el usuario hace clic en una opción.
    Detiene el temporizador, verifica si es correcta, colorea los botones y avanza.
    """
    global botones_actuales
    
    detener_temporizador()  # Detiene el temporizador
    
    for b in botones_actuales:  # Recorre todos los botones de opciones
        b.config(state="disabled")  # Los deshabilita para que no se puedan presionar más

    if hasattr(cargar_interfaz_pregunta, 'boton_ayuda'):  # Si existe el botón de ayuda
        cargar_interfaz_pregunta.boton_ayuda.config(state="disabled")  # Lo deshabilita

    q = obtener_pregunta_actual()  # Obtiene la pregunta actual
    respuesta_correcta = q.get("respuestaCorrecta", "")  # Obtiene la respuesta correcta
    es_correcta = verificar_respuesta(indice_opcion_seleccionada)  # Verifica si la respuesta es correcta

    if hasattr(cargar_interfaz_pregunta, 'etiqueta_pregunta'):  # Si existe el label de la pregunta
        if es_correcta:
            cargar_interfaz_pregunta.etiqueta_pregunta.config(text="✅ CORRECTO", bg=PALETA_COLORES["EXITO"])  # Muestra "CORRECTO" en verde
        else:
            cargar_interfaz_pregunta.etiqueta_pregunta.config(text="❌ INCORRECTO", bg=PALETA_COLORES["ERROR"])  # Muestra "INCORRECTO" en rojo

    for b in botones_actuales:  # Recorre todos los botones
        texto = b.cget("text")  # Obtiene el texto del botón
        
        if texto == respuesta_correcta:
            b.config(bg=PALETA_COLORES["EXITO"], fg="white")  # Colorea la correcta en verde
        elif texto == texto_opcion_seleccionada and not es_correcta:
            b.config(bg=PALETA_COLORES["ERROR"])  # Colorea la seleccionada incorrecta en rojo
        else:
            b.config(bg=PALETA_COLORES["ERROR"])  # Colorea las otras opciones en rojo

    ventana_principal.after(2000, avanzar_a_siguiente)  # Después de 2 segundos, avanza a la siguiente

# FUNCIÓN: avanza a la siguiente pregunta
def avanzar_a_siguiente():
    """
    Se ejecuta 2 segundos después de responder una pregunta.
    Si hay más preguntas, las carga; si no, muestra los resultados.
    """
    if siguiente_pregunta():  # Si hay más preguntas
        cargar_interfaz_pregunta()  # Carga la siguiente pregunta
    else:
        mostrar_interfaz_resultados()  # Si no, muestra los resultados

# FUNCIÓN: muestra la pantalla de resultados finales
def mostrar_interfaz_resultados():
    """
    Calcula el puntaje, porcentaje y muestra los resultados con botones
    para jugar de nuevo, volver al menú o agregar preguntas.
    """
    detener_temporizador()  # Detiene cualquier temporizador activo
    limpiar_todos_los_frames()  # Oculta otros frames
    marco_resultados.pack(fill="both", expand=True)  # Muestra el frame de resultados

    for w in marco_resultados.winfo_children():  # Recorre widgets anteriores
        w.destroy()  # Los elimina

    valor_puntaje, total = obtener_resultados()  # Obtiene el puntaje y total
    porcentaje = (valor_puntaje / total) * 100 if total > 0 else 0.0  # Calcula el porcentaje

    Label(marco_resultados, text="RESULTADOS", font=fuente_titulo,  # Título
          bg=PALETA_COLORES["FONDO_CLARO"]).pack(pady=10)
    
    Label(marco_resultados, text=f"{valor_puntaje}/{total} correctas - {porcentaje:.1f}%", font=fuente_grande,  # Resultado principal
          bg=PALETA_COLORES["FONDO_CLARO"]).pack(pady=8)

    ttk.Button(marco_resultados, text="🔄 Jugar de nuevo (misma categoría)",  # Botón para reintentar
               command=lambda: iniciar_interfaz_quiz(categoria_actual)).pack(pady=10)
    
    ttk.Button(marco_resultados, text="🏠 Volver al menú", command=mostrar_seleccion_categorias).pack(pady=6)  # Botón para volver al menú
    
    ttk.Button(marco_resultados, text="➕ Agregar Pregunta", command=mostrar_interfaz_agregar_pregunta).pack(pady=6)  # Botón para agregar pregunta

# VARIABLES GLOBALES para el formulario de agregar preguntas
variable_nueva_categoria = None  # Variable para guardar la categoría seleccionada
variable_texto_nueva_pregunta = None  # Variable para guardar el texto de la pregunta
variables_opciones = []  # Lista de variables para las 4 opciones
variable_correcta = None  # Variable para guardar cuál es la opción correcta

# FUNCIÓN: muestra la interfaz para agregar nuevas preguntas
def mostrar_interfaz_agregar_pregunta():
    """
    Muestra un formulario donde el usuario puede escribir una pregunta nueva,
    sus 4 opciones y seleccionar cuál es la correcta.
    """
    global variable_nueva_categoria, variable_texto_nueva_pregunta, variables_opciones, variable_correcta
    
    detener_temporizador()  # Detiene cualquier temporizador activo
    limpiar_todos_los_frames()  # Oculta otros frames
    marco_agregar_pregunta.pack(fill="both", expand=True)  # Muestra el frame de agregar preguntas

    encabezado = Frame(marco_agregar_pregunta, bg=PALETA_COLORES["FONDO_CLARO"])  # Frame del encabezado
    encabezado.pack(fill="x", pady=4)
    
    Button(encabezado, text="← Volver", command=mostrar_seleccion_categorias,  # Botón para volver
           relief="flat", bd=0, bg=PALETA_COLORES["FONDO_CLARO"]).pack(side=LEFT, padx=6)
    
    Label(encabezado, text="➕ Agregar Nueva Pregunta", font=fuente_grande,  # Título
          bg=PALETA_COLORES["FONDO_CLARO"]).pack(side=LEFT, padx=8)

    formulario = Frame(marco_agregar_pregunta, bg=PALETA_COLORES["FONDO_CLARO"])  # Frame del formulario
    formulario.pack(fill="both", expand=True, pady=12, padx=10)

    # CATEGORÍA: Combobox para seleccionar la categoría
    Label(formulario, text="Categoría:", font=fuente_mediana, bg=PALETA_COLORES["FONDO_CLARO"]).grid(row=0, column=0, sticky="w", pady=6)
    variable_nueva_categoria = StringVar()  # Variable para guardar la categoría
    categorias = list(datos_todas_preguntas.keys())  # Lista de categorías disponibles
    variable_nueva_categoria.set(categorias[0] if categorias else "Seleccionar")  # Selecciona la primera por defecto
    combo_categorias = ttk.Combobox(formulario, textvariable=variable_nueva_categoria, values=categorias, state="readonly", font=fuente_mediana)  # Dropdown
    combo_categorias.grid(row=0, column=1, sticky="ew", pady=6)

    # PREGUNTA: Text widget de varias líneas
    Label(formulario, text="Pregunta:", font=fuente_mediana, bg=PALETA_COLORES["FONDO_CLARO"]).grid(row=1, column=0, sticky="nw", pady=6)
    variable_texto_nueva_pregunta = Text(formulario, height=5, font=fuente_mediana, wrap=WORD)  # Caja de texto de 5 líneas
    variable_texto_nueva_pregunta.grid(row=1, column=1, sticky="ew", pady=6)

    # OPCIONES: 4 campos de texto para las opciones
    Label(formulario, text="Opciones (4):", font=fuente_mediana, bg=PALETA_COLORES["FONDO_CLARO"]).grid(row=2, column=0, sticky="nw", pady=6)
    marco_opciones_form = Frame(formulario, bg=PALETA_COLORES["FONDO_CLARO"])  # Frame para las opciones
    marco_opciones_form.grid(row=2, column=1, sticky="ew", pady=6)
    
    variables_opciones = []  # Lista para guardar las variables de las opciones
    for i in range(4):  # 4 opciones
        var = StringVar()  # Variable para esta opción
        Label(marco_opciones_form, text=f"Opción {i+1}:", bg=PALETA_COLORES["FONDO_CLARO"]).grid(row=i, column=0, sticky="w", padx=4, pady=4)
        Entry(marco_opciones_form, textvariable=var, font=fuente_mediana).grid(row=i, column=1, sticky="ew", padx=4, pady=4)  # Campo de texto
        marco_opciones_form.grid_columnconfigure(1, weight=1)
        variables_opciones.append(var)  # Añade la variable a la lista

    # RESPUESTA CORRECTA: Radiobuttons para seleccionar cuál opción es correcta
    Label(formulario, text="Respuesta correcta:", font=fuente_mediana, bg=PALETA_COLORES["FONDO_CLARO"]).grid(row=3, column=0, sticky="w", pady=6)
    variable_correcta = IntVar(value=0)  # Variable para guardar la opción correcta (0, 1, 2 o 3)
    marco_correcto = Frame(formulario, bg=PALETA_COLORES["FONDO_CLARO"])  # Frame para los radiobuttons
    marco_correcto.grid(row=3, column=1, sticky="w", pady=6)
    for i in range(4):  # 4 radiobuttons
        Radiobutton(marco_correcto, text=f"Opción {i+1}", variable=variable_correcta, value=i,  # Radiobutton
                    bg=PALETA_COLORES["FONDO_CLARO"], command=lambda i=i: variable_correcta.set(i)).pack(side=LEFT, padx=6)
        
    # GUARDAR: Botón para guardar la pregunta
    Button(formulario, text="💾 Guardar pregunta", bg="#4CAF50", fg="white",  # Botón
           relief="flat", bd=0, padx=14, pady=10,
           command=guardar_nueva_pregunta).grid(row=4, column=1, sticky="e", pady=12)

    formulario.grid_columnconfigure(1, weight=1)  # Configura la columna para que se expanda

# FUNCIÓN: guarda una nueva pregunta en el JSON
def guardar_nueva_pregunta():
    """
    Valida los datos del formulario, crea un diccionario de pregunta,
    lo guarda en el archivo JSON de la categoría y actualiza datos_todas_preguntas.
    """
    global datos_todas_preguntas
    
    categoria = variable_nueva_categoria.get()  # Obtiene la categoría seleccionada
    pregunta = variable_texto_nueva_pregunta.get("1.0", END).strip()  # Obtiene el texto de la pregunta
    if not pregunta:  # Si no escribió pregunta
        messagebox.showerror("Error", "La pregunta no puede estar vacía.")  # Muestra error
        return
    
    opciones = [v.get().strip() for v in variables_opciones]  # Obtiene todas las opciones
    if any(not o for o in opciones):  # Si falta completar una opción
        messagebox.showerror("Error", "Completá las 4 opciones.")  # Muestra error
        return
    
    if len(set(opciones)) != 4:  # Si hay opciones repetidas
        messagebox.showerror("Error", "Las opciones no pueden repetirse.")  # Muestra error
        return
    
    indice = variable_correcta.get()  # Obtiene el índice de la opción correcta
    
    if categoria not in MAPA_ARCHIVOS:  # Si la categoría no existe
        messagebox.showerror("Error", "Seleccioná una categoría válida.")  # Muestra error
        return
        
    if indice < 0 or indice > 3:  # Si el índice es inválido
        messagebox.showerror("Error", "Seleccioná la respuesta correcta.")  # Muestra error
        return
        
    nueva = {  # Crea diccionario con la nueva pregunta
        "pregunta": pregunta,
        "opciones": opciones,
        "respuestaCorrecta": opciones[indice]  # Usa el texto de la opción correcta
    }
    
    ok, err = guardar_pregunta_en_json(categoria, nueva)  # Guarda en el archivo JSON
    
    if ok:  # Si se guardó correctamente
        datos_todas_preguntas = cargar_preguntas(MAPA_ARCHIVOS)  # Recarga todas las preguntas
        messagebox.showinfo("Éxito", f"Pregunta agregada a '{categoria}'.")  # Muestra mensaje de éxito
        variable_texto_nueva_pregunta.delete("1.0", END)  # Limpia el campo de pregunta
        for v in variables_opciones:
            v.set("")  # Limpia los campos de opciones
        variable_correcta.set(0)  # Resetea la opción correcta
        mostrar_seleccion_categorias()  # Vuelve al menú de categorías
    else:
        messagebox.showerror("Error al guardar", f"No se pudo guardar: {err}")  # Muestra error

# FUNCIÓN: inicializa toda la aplicación
def inicializar_aplicacion():
    """
    Punto de entrada: carga todas las preguntas, crea la ventana principal,
    los frames para cada pantalla y muestra el menú de categorías.
    """
    global datos_todas_preguntas, ventana_principal
    global marco_contenido_principal, marco_categorias, marco_quiz, marco_resultados, marco_agregar_pregunta
    
    datos_todas_preguntas = cargar_preguntas(MAPA_ARCHIVOS)  # Carga todas las preguntas desde los JSON
    
    ventana_principal = Tk()  # Crea la ventana principal
    ventana_principal.title("🎯 Respondidos - Estilo Kahoot")  # Título de la ventana
    ventana_principal.geometry("900x720")  # Tamaño: 900x720 píxeles
    ventana_principal.config(bg=PALETA_COLORES["FONDO_CLARO"])  # Fondo gris claro

    etiqueta_titulo = Label(ventana_principal, text="🎯Respondidos🎯", font=fuente_titulo,  # Título permanente
                        bg=PALETA_COLORES["FONDO_CLARO"])
    etiqueta_titulo.pack(pady=8)
    
    marco_contenido_principal = Frame(ventana_principal, bg=PALETA_COLORES["FONDO_CLARO"])  # Frame principal
    marco_contenido_principal.pack(fill="both", expand=True)

    marco_categorias = Frame(marco_contenido_principal, bg=PALETA_COLORES["FONDO_CLARO"], padx=20, pady=20)  # Frame de categorías
    marco_quiz = Frame(marco_contenido_principal, bg=PALETA_COLORES["FONDO_CLARO"], padx=20, pady=20)  # Frame del quiz
    marco_resultados = Frame(marco_contenido_principal, bg=PALETA_COLORES["FONDO_CLARO"], padx=20, pady=20)  # Frame de resultados
    marco_agregar_pregunta = Frame(marco_contenido_principal, bg=PALETA_COLORES["FONDO_CLARO"], padx=20, pady=20)  # Frame de agregar preguntas
    
    mostrar_seleccion_categorias()  # Muestra el menú de selección de categorías
    
    ventana_principal.mainloop()  # Inicia el loop principal (mantiene la ventana abierta)

# === EJECUCIÓN ===

# Verifica que este archivo se ejecute como programa principal (no importado)
if __name__ == "__main__":
    inicializar_aplicacion()  # Ejecuta la función principal