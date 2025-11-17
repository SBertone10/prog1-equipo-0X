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
FILE_MAP = {
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
current_questions = []  # Lista de 10 preguntas de la categoría actual
current_question_index = 0  # Índice de la pregunta que se está mostrando (0 = primera pregunta)
score = 0  # Puntaje del jugador (contador de respuestas correctas)
current_category = None  # Categoría seleccionada actualmente
all_questions_data = {}  # Diccionario con todas las preguntas: {"Cine": [...], "Música": [...], etc}
current_buttons = []  # Lista de botones de opciones para poder modificarlos después
timer_running = False  # Booleano: ¿está corriendo el temporizador?
time_left = 15  # Segundos restantes para responder la pregunta
timer_id = None  # ID del timer para poder detenerlo si es necesario
helps_remaining = 2  # Cantidad de ayudas disponibles en el quiz actual (máximo 2)
helps_used_this_question = False  # Booleano: ¿ya usó ayuda en esta pregunta?

NUM_QUESTIONS = 10  # Cantidad de preguntas por quiz (constante)

# DICCIONARIO DE COLORES: define los colores del diseño
COLOR_PALETTE = {
    "BACKGROUND_LIGHT": "#d4d4d4",  # Color de fondo gris claro
    "PRIMARY_TEXT": "#1f2937",  # Texto principal gris oscuro
    "SECONDARY_TEXT": "#6b7280",  # Texto secundario gris medio
    "SUCCESS": "#10b981",  # Verde para respuestas correctas
    "ERROR": "#ef4444",  # Rojo para respuestas incorrectas
    "WARNING": "#f59e0b",  # Amarillo para advertencias
    "HELP": "#8B5CF6"  # Morado para botón de ayuda
}

# DICCIONARIO DE COLORES POR CATEGORÍA: cada categoría tiene sus propios colores e icono
CATEGORY_COLORS = {
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
def script_dir():
    return os.path.dirname(os.path.abspath(__file__))  # Devuelve la ruta de la carpeta actual

# FUNCIÓN: carga todas las preguntas desde los archivos JSON al iniciar
def load_questions(file_map):
    """
    Lee los archivos JSON de cada categoría y carga todas las preguntas en memoria.
    Devuelve un diccionario: {"Cine": [pregunta1, pregunta2...], "Música": [...], etc}
    """
    all_data = {}  # Diccionario vacío donde guardaremos todas las preguntas
    base = script_dir()  # Obtiene la ruta base donde está el programa
    
    for category_name, file_name in file_map.items():  # Recorre cada categoría y su archivo
        path = os.path.join(base, file_name)  # Construye la ruta completa del archivo JSON
        try:
            with open(path, "r", encoding="utf-8") as f:  # Abre el archivo en modo lectura
                data = json.load(f)  # Convierte el JSON a una lista de Python
                if isinstance(data, list) and data:  # Verifica que sea una lista no vacía
                    all_data[category_name] = data  # Guarda las preguntas en el diccionario
                else:
                    all_data[category_name] = data if isinstance(data, list) else []  # Si no es lista, vacío
        except FileNotFoundError:  # Si el archivo no existe
            try:
                with open(path, "w", encoding="utf-8") as f:  # Crea el archivo vacío
                    json.dump([], f, ensure_ascii=False, indent=2)  # Escribe una lista vacía
                all_data[category_name] = []  # Añade categoría vacía al diccionario
            except Exception as e:  # Si hay error al crear el archivo
                print(f"No se pudo crear {file_name}: {e}")  # Imprime el error
        except json.JSONDecodeError:  # Si el JSON está mal formado
            print(f"JSON inválido en {file_name}.")  # Imprime el error
            all_data[category_name] = []  # Añade categoría vacía
        except Exception as e:  # Cualquier otro error
            print(f"Error cargando {file_name}: {e}")  # Imprime el error
            all_data[category_name] = []  # Añade categoría vacía
    return all_data  # Devuelve el diccionario completo de todas las preguntas

# FUNCIÓN: guarda una nueva pregunta en el archivo JSON de la categoría
def save_question_to_json(category, new_question):
    """
    Añade una pregunta nueva al final del archivo JSON de una categoría.
    La pregunta tiene: pregunta, opciones, respuestaCorrecta
    """
    base = script_dir()  # Obtiene la ruta base
    if category not in FILE_MAP:  # Verifica que la categoría exista en FILE_MAP
        return False, "Categoría desconocida."  # Devuelve error si no existe
    
    path = os.path.join(base, FILE_MAP[category])  # Construye la ruta del archivo
    try:
        with open(path, "r", encoding="utf-8") as f:  # Abre el archivo para leer
            existing = json.load(f)  # Carga las preguntas existentes
            if not isinstance(existing, list):  # Si no es una lista
                existing = []  # Inicia como lista vacía
    except Exception:
        existing = []  # Si hay error, crea lista vacía
    
    existing.append(new_question)  # Añade la nueva pregunta a la lista
    try:
        with open(path, "w", encoding="utf-8") as f:  # Abre el archivo para escribir (sobrescribe)
            json.dump(existing, f, ensure_ascii=False, indent=2)  # Convierte lista a JSON y guarda
        return True, None  # Devuelve éxito
    except Exception as e:  # Si hay error al guardar
        return False, str(e)  # Devuelve el error

# === SECCIÓN 2: LÓGICA DEL QUIZ ===

# FUNCIÓN: inicia un nuevo quiz con la categoría seleccionada
def start_quiz(category):
    """
    Prepara el quiz: obtiene 10 preguntas al azar de la categoría,
    resetea puntaje, temporizador y otras variables de estado.
    """
    global current_questions, current_question_index, score, current_category, time_left, helps_remaining, helps_used_this_question
    
    # Verifica que la categoría tenga suficientes preguntas (mínimo 10)
    if category not in all_questions_data or not isinstance(all_questions_data[category], list) or not all_questions_data[category] or len(all_questions_data[category]) < NUM_QUESTIONS:
        return False  # Devuelve False si no hay suficientes preguntas
    
    current_category = category  # Guarda la categoría actual
    score = 0  # Resetea el puntaje a 0
    current_question_index = 0  # Empieza en la primera pregunta
    time_left = 15  # Inicializa el temporizador a 15 segundos
    helps_remaining = 2  # Permite 2 ayudas por quiz
    helps_used_this_question = False  # Aún no usó ayuda en esta pregunta
    
    questions = list(all_questions_data[category])  # Copia la lista de preguntas
    random.shuffle(questions)  # Las mezcla aleatoriamente
    current_questions = questions[:NUM_QUESTIONS]  # Toma solo las primeras 10
    return True  # Devuelve True indicando que el quiz comenzó

# FUNCIÓN: obtiene la pregunta que se está mostrando actualmente
def get_current_question():
    """
    Devuelve el diccionario de la pregunta actual (pregunta, opciones, respuestaCorrecta).
    Si no hay más preguntas, devuelve None.
    """
    if current_question_index < len(current_questions):  # Verifica que el índice sea válido
        return current_questions[current_question_index]  # Devuelve la pregunta actual
    return None  # Devuelve None si ya terminaron las preguntas

# FUNCIÓN: verifica si la respuesta seleccionada es correcta
def check_answer(selected_option_index):
    """
    Compara la opción seleccionada con la respuesta correcta.
    Si es correcta, suma 1 al puntaje.
    Devuelve True si es correcta, False si es incorrecta.
    """
    global score  # Accede a la variable global score
    
    q = get_current_question()  # Obtiene la pregunta actual
    if not q:  # Si no hay pregunta
        return False  # Devuelve False
    try:
        correct_answer = q["respuestaCorrecta"]  # Obtiene la respuesta correcta (texto)
        correct_index = q["opciones"].index(correct_answer)  # Obtiene el índice de esa respuesta
    except Exception:
        return False  # Devuelve False si hay error
    
    correct = (selected_option_index == correct_index)  # Verifica si coinciden los índices
    if correct:  # Si es correcta
        score += 1  # Suma 1 al puntaje
    return correct  # Devuelve True o False

# FUNCIÓN: avanza a la siguiente pregunta
def next_question():
    """
    Incrementa el índice de la pregunta actual y resetea el temporizador.
    Devuelve True si hay más preguntas, False si ya terminaron.
    """
    global current_question_index, time_left, helps_used_this_question
    current_question_index += 1  # Incrementa el índice
    time_left = 15  # Resetea el temporizador
    helps_used_this_question = False  # Permite usar ayuda nuevamente
    return current_question_index < len(current_questions)  # Devuelve True si hay más preguntas

# FUNCIÓN: obtiene los resultados finales del quiz
def get_results():
    """
    Devuelve una tupla (puntaje_actual, total_preguntas) para calcular el porcentaje.
    """
    return score, len(current_questions)  # Devuelve puntaje y total de preguntas

# === SECCIÓN 3: TEMPORIZADOR Y BARRA DE TIEMPO ===

# FUNCIÓN: inicia el temporizador de 15 segundos
def start_timer():
    """
    Activa el temporizador, lo setea a 15 segundos y comienza a contar.
    """
    global timer_running, time_left, timer_id
    timer_running = True  # Marca que el temporizador está corriendo
    time_left = 15  # Inicializa a 15 segundos
    update_timer_display()  # Actualiza la visualización en la interfaz
    update_time_bar()  # Actualiza la barra de tiempo
    timer_id = master_window.after(1000, update_timer)  # Llama a update_timer en 1000ms (1 segundo)

# FUNCIÓN: detiene el temporizador
def stop_timer():
    """
    Detiene el temporizador. Se usa cuando se responde una pregunta o se vuelve al menú.
    """
    global timer_running, timer_id
    timer_running = False  # Marca que el temporizador está detenido
    if timer_id:  # Si hay un timer_id
        master_window.after_cancel(timer_id)  # Cancela la ejecución programada
        timer_id = None  # Limpia el ID

# FUNCIÓN: actualiza el temporizador cada segundo
def update_timer():
    """
    Se ejecuta cada segundo mientras timer_running sea True.
    Decrementa time_left, actualiza la pantalla y llama a time_up() si llegó a 0.
    """
    global time_left, timer_running, timer_id
    
    if not timer_running:  # Si el temporizador no está corriendo
        return  # Sale de la función
        
    time_left -= 1  # Resta 1 segundo
    update_timer_display()  # Actualiza el texto del temporizador
    update_time_bar()  # Actualiza la barra de progreso
    
    if time_left <= 0:  # Si se acabó el tiempo
        stop_timer()  # Detiene el temporizador
        time_up()  # Ejecuta la función de tiempo agotado
    else:
        timer_id = master_window.after(1000, update_timer)  # Programa la siguiente ejecución en 1 segundo

# FUNCIÓN: actualiza el texto que muestra los segundos restantes
def update_timer_display():
    """
    Cambia el texto del label que muestra "⏱️ 15s", "⏱️ 14s", etc.
    Cambia el color a verde si hay > 5 segundos, rojo si hay <= 5 segundos.
    """
    if hasattr(update_timer_display, 'timer_label') and update_timer_display.timer_label:  # Verifica que exista el label
        color = COLOR_PALETTE["SUCCESS"] if time_left > 5 else COLOR_PALETTE["ERROR"]  # Verde si >5s, rojo si <=5s
        update_timer_display.timer_label.config(text=f"⏱️ {time_left}s", fg=color)  # Actualiza el texto y color

# FUNCIÓN: actualiza la barra de tiempo horizontal
def update_time_bar():
    """
    Dibuja una barra que se va encogiendo de derecha a izquierda mientras pasan los segundos.
    Cambia de color: verde (>5s) → amarillo (>2s) → rojo (<=2s).
    """
    if hasattr(update_time_bar, 'time_bar_canvas') and update_time_bar.time_bar_canvas:  # Verifica que exista el canvas
        percentage = (time_left / 15) * 100  # Calcula qué porcentaje del tiempo queda (0-100%)
        
        # Elige color según el tiempo restante
        if time_left > 5:
            color = COLOR_PALETTE["SUCCESS"]  # Verde si quedan > 5 segundos
        elif time_left > 2:
            color = COLOR_PALETTE["WARNING"]  # Amarillo si quedan entre 2 y 5 segundos
        else:
            color = COLOR_PALETTE["ERROR"]  # Rojo si quedan <= 2 segundos
        
        bar_width = (percentage / 100) * 860  # Calcula el ancho de la barra (860 es el ancho total)
        x_start = 860 - bar_width  # Calcula desde dónde empezar la barra (de derecha a izquierda)
        update_time_bar.time_bar_canvas.coords(update_time_bar.time_bar_rect, x_start, 0, 860, 10)  # Actualiza las coordenadas
        update_time_bar.time_bar_canvas.itemconfig(update_time_bar.time_bar_rect, fill=color)  # Cambia el color

# FUNCIÓN: crea la barra de tiempo horizontal visual
def create_time_bar(parent):
    """
    Dibuja un canvas con una barra rectangular que representa el tiempo.
    Esta barra se va achicando a medida que pasan los segundos.
    """
    time_bar_container = Frame(parent, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], height=15)  # Frame contenedor
    time_bar_container.pack(fill="x", padx=20, pady=(0, 0))  # Lo empaqueta
    
    update_time_bar.time_bar_canvas = Canvas(time_bar_container, height=10, bg="#e5e7eb", highlightthickness=0, width=860)  # Canvas para dibujar
    update_time_bar.time_bar_canvas.pack(fill="x", padx=0)  # Lo empaqueta
    
    update_time_bar.time_bar_rect = update_time_bar.time_bar_canvas.create_rectangle(0, 0, 860, 10, fill=COLOR_PALETTE["SUCCESS"], outline="")  # Dibuja el rectángulo

# FUNCIÓN: maneja cuando se acaba el tiempo
def time_up():
    """
    Cuando time_left llega a 0, deshabilita los botones, muestra la respuesta correcta,
    y avanza automáticamente a la siguiente pregunta después de 2 segundos.
    """
    global current_buttons
    
    for b in current_buttons:  # Recorre todos los botones de opciones
        b.config(state="disabled")  # Los deshabilita para que no se puedan presionar
    
    if hasattr(load_question_ui, 'help_button'):  # Si existe el botón de ayuda
        load_question_ui.help_button.config(state="disabled")  # Lo deshabilita
    
    q = get_current_question()  # Obtiene la pregunta actual
    if not q:
        return  # Si no hay pregunta, sale
        
    correct_answer = q.get("respuestaCorrecta", "")  # Obtiene la respuesta correcta
    
    for b in current_buttons:  # Recorre todos los botones
        text = b.cget("text")  # Obtiene el texto del botón
        if text == correct_answer:
            b.config(bg=COLOR_PALETTE["SUCCESS"], fg="white")  # Colorea la correcta de verde
        else:
            b.config(bg=COLOR_PALETTE["ERROR"])  # Colorea las incorrectas de rojo
    
    if hasattr(load_question_ui, 'question_label'):  # Si existe el label de la pregunta
        load_question_ui.question_label.config(text="⏰ TIEMPO AGOTADO", bg=COLOR_PALETTE["ERROR"])  # Muestra "TIEMPO AGOTADO"
    
    master_window.after(2000, advance_after_timeout)  # Después de 2 segundos, avanza

# FUNCIÓN: avanza a la siguiente pregunta después de que se agote el tiempo
def advance_after_timeout():
    """
    Se ejecuta 2 segundos después de que time_left llegue a 0.
    Avanza a la siguiente pregunta o muestra los resultados si ya terminó.
    """
    if next_question():  # Si hay más preguntas
        load_question_ui()  # Carga la siguiente pregunta
    else:
        show_results_ui()  # Si no, muestra los resultados

# === SECCIÓN 4: SISTEMA DE AYUDAS ===

# FUNCIÓN: usa una ayuda para eliminar 2 opciones incorrectas
def use_help():
    """
    Elimina 2 opciones incorrectas aleatorias (mostradas en gris).
    Solo se puede usar 1 ayuda por pregunta y máximo 2 por quiz.
    """
    global helps_remaining, helps_used_this_question, current_buttons
    
    if helps_remaining <= 0 or helps_used_this_question:  # Si no quedan ayudas o ya usó una en esta pregunta
        return  # Sale de la función
        
    helps_remaining -= 1  # Decrementa las ayudas disponibles
    helps_used_this_question = True  # Marca que ya usó ayuda en esta pregunta
    
    if hasattr(load_question_ui, 'help_button'):  # Si existe el botón de ayuda
        if helps_remaining > 0:
            load_question_ui.help_button.config(text=f"❓ Ayuda ({helps_remaining} restantes)", state="normal")  # Actualiza el texto
        else:
            load_question_ui.help_button.config(text="❓ Ayudas agotadas", state="disabled")  # Si no quedan, lo deshabilita
    
    q = get_current_question()  # Obtiene la pregunta actual
    if not q:
        return  # Si no hay pregunta, sale
        
    correct_answer = q.get("respuestaCorrecta", "")  # Obtiene la respuesta correcta
    
    incorrect_indices = []  # Lista para guardar los índices de respuestas incorrectas
    for i, button in enumerate(current_buttons):  # Recorre todos los botones
        if button.cget("text") != correct_answer and button.cget("state") == "normal":  # Si es incorrecta y está habilitada
            incorrect_indices.append(i)  # Añade su índice a la lista
    
    if len(incorrect_indices) >= 2:  # Si hay 2 o más opciones incorrectas
        random.shuffle(incorrect_indices)  # Las mezcla aleatoriamente
        to_remove = incorrect_indices[:2]  # Toma las primeras 2
        
        for index in to_remove:  # Recorre los índices a eliminar
            current_buttons[index].config(state="disabled", bg="#666666", fg="#999999", text="❌ Eliminada")  # Las deshabilita y cambia de color
    
    elif len(incorrect_indices) == 1:  # Si solo hay 1 opción incorrecta
        current_buttons[incorrect_indices[0]].config(state="disabled", bg="#666666", fg="#999999", text="❌ Eliminada")  # La elimina

# === SECCIÓN 5: INTERFAZ GRÁFICA (TKINTER) ===

# VARIABLES GLOBALES para almacenar los frames (paneles) de la interfaz
main_content_frame = None  # Frame principal que contiene todos los demás
category_frame = None  # Frame para mostrar las categorías disponibles
quiz_frame = None  # Frame para mostrar las preguntas del quiz
results_frame = None  # Frame para mostrar los resultados finales
add_question_frame = None  # Frame para agregar nuevas preguntas

# CONSTANTES para tamaño de botones
BUTTON_PAD_NORMAL = 20  # Padding de los botones en píxeles
BUTTON_WIDTH_FIXED = 35  # Ancho fijo de los botones
BUTTON_HEIGHT_FIXED = 4  # Altura fija de los botones
BUTTON_WRAPLENGTH = 350  # Ancho máximo antes de saltar a la siguiente línea

# FUENTES: define los estilos de texto a usar en la interfaz
font_title = ("Inter", 28, "bold")  # Título grande y negrita
font_large = ("Inter", 18, "bold")  # Texto grande y negrita
font_medium = ("Inter", 12)  # Texto mediano normal
font_small = ("Inter", 10)  # Texto pequeño normal

# FUNCIÓN: limpia todos los frames (los oculta)
def clear_all_frames():
    """
    Usa pack_forget() para ocultar todos los frames de contenido.
    Esto permite mostrar uno a la vez sin que se superpongan.
    """
    for f in [category_frame, quiz_frame, results_frame, add_question_frame]:  # Recorre todos los frames
        if f:  # Si el frame existe
            f.pack_forget()  # Lo oculta

# FUNCIÓN: crea un tooltip (pequeña ventana de ayuda)
def create_tooltip(widget, text):
    """
    Cuando pasas el mouse sobre el widget, muestra un pequeño popup con texto de ayuda.
    Desaparece cuando sacas el mouse.
    """
    tooltip_window = None  # Variable para guardar la ventana del tooltip
    
    def enter(event):  # Se ejecuta cuando el mouse entra al widget
        nonlocal tooltip_window  # Permite modificar tooltip_window
        x, y, _, _ = widget.bbox("insert")  # Obtiene la posición del widget
        x += widget.winfo_rootx() + 25  # Suma offset para el tooltip
        y += widget.winfo_rooty() + 25  # Suma offset para el tooltip
        tooltip_window = Toplevel(widget)  # Crea una ventana nueva
        tooltip_window.wm_overrideredirect(True)  # Ventana sin decoraciones
        tooltip_window.wm_geometry(f"+{x}+{y}")  # Posiciona la ventana
        Label(tooltip_window, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("tahoma", "8", "normal")).pack()  # Añade el texto
    
    def leave(event):  # Se ejecuta cuando el mouse sale del widget
        nonlocal tooltip_window  # Permite modificar tooltip_window
        if tooltip_window:  # Si la ventana del tooltip existe
            tooltip_window.destroy()  # La elimina
            tooltip_window = None  # Resetea la variable
    
    widget.bind("<Enter>", enter)  # Vincula evento "Enter" a la función enter
    widget.bind("<Leave>", leave)  # Vincula evento "Leave" a la función leave

# FUNCIÓN: muestra la pantalla de selección de categorías
def show_category_selection():
    """
    Limpia la interfaz y muestra los 8 botones de categorías.
    Cada botón tiene su color, icono y número de preguntas.
    """
    stop_timer()  # Detiene cualquier temporizador activo
    clear_all_frames()  # Oculta todos los frames anteriores
    category_frame.pack(fill="both", expand=True)  # Muestra el frame de categorías

    Label(category_frame, text=f"Cada quiz tiene {NUM_QUESTIONS} preguntas", font=font_medium,
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SECONDARY_TEXT"]).pack(pady=4)  # Texto informativo

    grid = Frame(category_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Frame para el grid de categorías
    grid.pack(expand=True, fill="both", pady=10)  # Lo empaqueta

    cats = list(dict.fromkeys(list(CATEGORY_COLORS.keys()) + list(all_questions_data.keys())))  # Obtiene lista de categorías sin duplicados

    for i, cat in enumerate(cats):  # Recorre cada categoría con su índice
        colors = CATEGORY_COLORS.get(cat, {"bg": "#DDDDDD", "hover": "#CCCCCC", "icon": "❓", "fg": "#111"})  # Obtiene colores de la categoría
        num_q = len(all_questions_data.get(cat, []))  # Cuenta cuántas preguntas tiene
        has_questions = num_q >= NUM_QUESTIONS  # Verifica si tiene suficientes preguntas

        btn_state = "normal" if has_questions else "disabled"  # Estado del botón (habilitado o deshabilitado)
        tooltip_text = ""
        if not has_questions:
             tooltip_text = f"Faltan preguntas para el quiz ({num_q}/{NUM_QUESTIONS})"  # Mensaje de tooltip

        btn = Button(grid, text=f"{colors['icon']}  {cat}", font=font_large,  # Crea botón con icono y nombre
                     bg=colors["bg"], fg=colors["fg"], activebackground=colors["hover"],  # Colores del botón
                     relief="flat", bd=0, padx=30, pady=18, state=btn_state,
                     command=lambda c=cat: start_quiz_ui(c))  # Función al hacer clic
        btn.grid(row=i // 2, column=i % 2, padx=16, pady=16, sticky="nsew")  # Posiciona el botón en grid 2x4

        if not has_questions:
            create_tooltip(btn, tooltip_text)  # Crea tooltip si faltan preguntas

    for i in range(2):
        grid.grid_columnconfigure(i, weight=1)  # Configura las columnas para que se expandan

    Button(category_frame, text="➕ Agregar Pregunta", font=font_medium,  # Botón para agregar pregunta
           bg="#4CAF50", fg="white", activebackground="#45a049", relief="flat", bd=0, padx=12, pady=10,
           command=show_add_question_ui).pack(pady=8)

# FUNCIÓN: inicia la interfaz del quiz
def start_quiz_ui(category):
    """
    Verifica que haya suficientes preguntas, inicia el quiz y muestra la primera pregunta.
    """
    if start_quiz(category):  # Si el quiz se inició correctamente
        clear_all_frames()  # Oculta otros frames
        quiz_frame.pack(fill="both", expand=True)  # Muestra el frame del quiz
        load_question_ui()  # Carga y muestra la primera pregunta
    else:
        messagebox.showerror("Error", f"No hay suficientes preguntas disponibles para esta categoría. Necesitas {NUM_QUESTIONS}.")  # Muestra error

# FUNCIÓN: carga y muestra la pregunta actual
def load_question_ui():
    """
    Borra la interfaz anterior y dibuja: encabezado, pregunta, 4 opciones, botón de ayuda y barra de tiempo.
    """
    global current_buttons
    
    for w in quiz_frame.winfo_children():  # Recorre todos los widgets del frame
        w.destroy()  # Los elimina
    
    current_buttons = []  # Reinicia la lista de botones
    stop_timer()  # Detiene el temporizador anterior

    question = get_current_question()  # Obtiene la pregunta actual
    if not question:  # Si no hay pregunta
        show_results_ui()  # Muestra los resultados
        return

    cat_info = CATEGORY_COLORS.get(current_category, {"hover": "#888", "icon": "?"})  # Obtiene colores de la categoría
    
    header = Frame(quiz_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Frame del encabezado
    header.pack(fill="x")
    
    Button(header, text="← Categorías", command=show_category_selection,  # Botón para volver a categorías
           relief="flat", bd=0, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=5)
    
    update_timer_display.timer_label = Label(header, text=f"⏱️ {time_left}s", font=font_medium,  # Label del temporizador
                                            bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SUCCESS"])
    update_timer_display.timer_label.pack(side=RIGHT, padx=8)
    
    Label(header, text=f"Puntaje: {score}/{NUM_QUESTIONS}", font=font_medium,  # Label del puntaje
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SUCCESS"]).pack(side=RIGHT, padx=8)
    
    Label(header, text=f"{cat_info.get('icon','')}  {current_category}", font=font_medium,  # Label de la categoría
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=RIGHT, padx=8)

    Label(quiz_frame, text=f"Pregunta {current_question_index + 1} de {NUM_QUESTIONS}",  # Contador de pregunta
          font=font_small, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SECONDARY_TEXT"]).pack()

    question_container = Frame(quiz_frame, bg=cat_info["hover"], height=150)  # Frame para la pregunta
    question_container.pack(pady=12, fill="x", padx=20) 
    question_container.pack_propagate(False)  # Mantiene el tamaño fijo

    load_question_ui.question_label = Label(question_container, text=question["pregunta"], font=font_large,  # Label de la pregunta
          bg=cat_info["hover"], fg="white", wraplength=750, justify=CENTER)
    load_question_ui.question_label.pack(expand=True, padx=20, pady=20)

    create_time_bar(question_container)  # Crea la barra de tiempo

    options_frame = Frame(quiz_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Frame para las opciones
    options_frame.pack(fill="both", expand=False, pady=10)

    kahoot_colors = ["#E74C3C", "#3498DB", "#F1C40F", "#2ECC71"]  # Colores para las 4 opciones (rojo, azul, amarillo, verde)
    options_shuffled = random.sample(question["opciones"], len(question["opciones"]))  # Mezcla las opciones aleatoriamente
    current_buttons = []

    screen_height = master_window.winfo_screenheight() if master_window else 900  # Obtiene la altura de la pantalla
    # Ajusta tamaño de botones según la altura de pantalla
    if screen_height < 800:
        b_width = 26
        b_height = 2
        b_wrap = 250
        b_pad = 8
    elif screen_height < 1000:
        b_width = 30
        b_height = 3
        b_wrap = 300
        b_pad = 12
    else:
        b_width = 35
        b_height = 4
        b_wrap = 350
        b_pad = 20

    for i, opt_text in enumerate(options_shuffled):  # Recorre cada opción
        try:
            original_index = question["opciones"].index(opt_text)  # Obtiene el índice original en el JSON
        except ValueError:
            original_index = -1

        btn_color = kahoot_colors[i % len(kahoot_colors)]  # Asigna color a la opción

        btn = Button(options_frame, text=opt_text, font=("Inter", 14, "bold"),  # Crea botón de opción
                     bg=btn_color, fg="white", activeforeground="white",
                     wraplength=b_wrap,
                     width=b_width,
                     height=b_height,
                     relief="flat", bd=0,
                     padx=b_pad, pady=b_pad,
                     command=lambda idx=original_index, opt=opt_text: handle_answer(idx, opt))  # Al hacer clic, ejecuta handle_answer

        btn.grid(row=i // 2, column=i % 2, padx=12, pady=12, sticky="nsew")  # Posiciona en grid 2x2

        current_buttons.append(btn)  # Añade el botón a la lista global

    for col in range(2):
        options_frame.grid_columnconfigure(col, weight=1)  # Configura columnas

    help_frame = Frame(quiz_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Frame para el botón de ayuda
    help_frame.pack(pady=15)
    
    help_button_text = f"❓ Ayuda ({helps_remaining} restantes)"
    load_question_ui.help_button = Button(help_frame, text=help_button_text, font=("Inter", 14, "bold"),  # Botón de ayuda
                                         bg=COLOR_PALETTE["HELP"], fg="white", 
                                         activebackground="#7C3AED", activeforeground="white",
                                         relief="flat", bd=0, padx=25, pady=15,
                                         command=use_help)
    load_question_ui.help_button.pack()

    start_timer()  # Inicia el temporizador de 15 segundos

# FUNCIÓN: maneja la selección de una respuesta
def handle_answer(selected_option_index, selected_option_text):
    """
    Se ejecuta cuando el usuario hace clic en una opción.
    Detiene el temporizador, verifica si es correcta, colorea los botones y avanza.
    """
    global current_buttons
    
    stop_timer()  # Detiene el temporizador
    
    for b in current_buttons:  # Recorre todos los botones de opciones
        b.config(state="disabled")  # Los deshabilita para que no se puedan presionar más

    if hasattr(load_question_ui, 'help_button'):  # Si existe el botón de ayuda
        load_question_ui.help_button.config(state="disabled")  # Lo deshabilita

    q = get_current_question()  # Obtiene la pregunta actual
    correct_answer = q.get("respuestaCorrecta", "")  # Obtiene la respuesta correcta
    is_correct = check_answer(selected_option_index)  # Verifica si la respuesta es correcta

    if hasattr(load_question_ui, 'question_label'):  # Si existe el label de la pregunta
        if is_correct:
            load_question_ui.question_label.config(text="✅ CORRECTO", bg=COLOR_PALETTE["SUCCESS"])  # Muestra "CORRECTO" en verde
        else:
            load_question_ui.question_label.config(text="❌ INCORRECTO", bg=COLOR_PALETTE["ERROR"])  # Muestra "INCORRECTO" en rojo

    for b in current_buttons:  # Recorre todos los botones
        text = b.cget("text")  # Obtiene el texto del botón
        
        if text == correct_answer:
            b.config(bg=COLOR_PALETTE["SUCCESS"], fg="white")  # Colorea la correcta en verde
        elif text == selected_option_text and not is_correct:
            b.config(bg=COLOR_PALETTE["ERROR"])  # Colorea la seleccionada incorrecta en rojo
        else:
            b.config(bg=COLOR_PALETTE["ERROR"])  # Colorea las otras opciones en rojo

    master_window.after(2000, advance_to_next)  # Después de 2 segundos, avanza a la siguiente

# FUNCIÓN: avanza a la siguiente pregunta
def advance_to_next():
    """
    Se ejecuta 2 segundos después de responder una pregunta.
    Si hay más preguntas, las carga; si no, muestra los resultados.
    """
    if next_question():  # Si hay más preguntas
        load_question_ui()  # Carga la siguiente pregunta
    else:
        show_results_ui()  # Si no, muestra los resultados

# FUNCIÓN: muestra la pantalla de resultados finales
def show_results_ui():
    """
    Calcula el puntaje, porcentaje y muestra los resultados con botones
    para jugar de nuevo, volver al menú o agregar preguntas.
    """
    stop_timer()  # Detiene cualquier temporizador activo
    clear_all_frames()  # Oculta otros frames
    results_frame.pack(fill="both", expand=True)  # Muestra el frame de resultados

    for w in results_frame.winfo_children():  # Recorre widgets anteriores
        w.destroy()  # Los elimina

    score_val, total = get_results()  # Obtiene el puntaje y total
    pct = (score_val / total) * 100 if total > 0 else 0.0  # Calcula el porcentaje

    Label(results_frame, text="RESULTADOS", font=font_title,  # Título
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=10)
    
    Label(results_frame, text=f"{score_val}/{total} correctas - {pct:.1f}%", font=font_large,  # Resultado principal
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=8)

    ttk.Button(results_frame, text="🔄 Jugar de nuevo (misma categoría)",  # Botón para reintentar
               command=lambda: start_quiz_ui(current_category)).pack(pady=10)
    
    ttk.Button(results_frame, text="🏠 Volver al menú", command=show_category_selection).pack(pady=6)  # Botón para volver al menú
    
    ttk.Button(results_frame, text="➕ Agregar Pregunta", command=show_add_question_ui).pack(pady=6)  # Botón para agregar pregunta

# VARIABLES GLOBALES para el formulario de agregar preguntas
new_cat_var = None  # Variable para guardar la categoría seleccionada
new_question_text = None  # Variable para guardar el texto de la pregunta
new_option_vars = []  # Lista de variables para las 4 opciones
correct_var = None  # Variable para guardar cuál es la opción correcta

# FUNCIÓN: muestra la interfaz para agregar nuevas preguntas
def show_add_question_ui():
    """
    Muestra un formulario donde el usuario puede escribir una pregunta nueva,
    sus 4 opciones y seleccionar cuál es la correcta.
    """
    global new_cat_var, new_question_text, new_option_vars, correct_var
    
    stop_timer()  # Detiene cualquier temporizador activo
    clear_all_frames()  # Oculta otros frames
    add_question_frame.pack(fill="both", expand=True)  # Muestra el frame de agregar preguntas

    header = Frame(add_question_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Frame del encabezado
    header.pack(fill="x", pady=4)
    
    Button(header, text="← Volver", command=show_category_selection,  # Botón para volver
           relief="flat", bd=0, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=6)
    
    Label(header, text="➕ Agregar Nueva Pregunta", font=font_large,  # Título
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=8)

    form = Frame(add_question_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Frame del formulario
    form.pack(fill="both", expand=True, pady=12, padx=10)

    # CATEGORÍA: Combobox para seleccionar la categoría
    Label(form, text="Categoría:", font=font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=0, column=0, sticky="w", pady=6)
    new_cat_var = StringVar()  # Variable para guardar la categoría
    cats = list(all_questions_data.keys())  # Lista de categorías disponibles
    new_cat_var.set(cats[0] if cats else "Seleccionar")  # Selecciona la primera por defecto
    cat_combo = ttk.Combobox(form, textvariable=new_cat_var, values=cats, state="readonly", font=font_medium)  # Dropdown
    cat_combo.grid(row=0, column=1, sticky="ew", pady=6)

    # PREGUNTA: Text widget de varias líneas
    Label(form, text="Pregunta:", font=font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=1, column=0, sticky="nw", pady=6)
    new_question_text = Text(form, height=5, font=font_medium, wrap=WORD)  # Caja de texto de 5 líneas
    new_question_text.grid(row=1, column=1, sticky="ew", pady=6)

    # OPCIONES: 4 campos de texto para las opciones
    Label(form, text="Opciones (4):", font=font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=2, column=0, sticky="nw", pady=6)
    opts_frame = Frame(form, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Frame para las opciones
    opts_frame.grid(row=2, column=1, sticky="ew", pady=6)
    
    new_option_vars = []  # Lista para guardar las variables de las opciones
    for i in range(4):  # 4 opciones
        var = StringVar()  # Variable para esta opción
        Label(opts_frame, text=f"Opción {i+1}:", bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=i, column=0, sticky="w", padx=4, pady=4)
        Entry(opts_frame, textvariable=var, font=font_medium).grid(row=i, column=1, sticky="ew", padx=4, pady=4)  # Campo de texto
        opts_frame.grid_columnconfigure(1, weight=1)
        new_option_vars.append(var)  # Añade la variable a la lista

    # RESPUESTA CORRECTA: Radiobuttons para seleccionar cuál opción es correcta
    Label(form, text="Respuesta correcta:", font=font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=3, column=0, sticky="w", pady=6)
    correct_var = IntVar(value=0)  # Variable para guardar la opción correcta (0, 1, 2 o 3)
    correct_frame = Frame(form, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Frame para los radiobuttons
    correct_frame.grid(row=3, column=1, sticky="w", pady=6)
    for i in range(4):  # 4 radiobuttons
        Radiobutton(correct_frame, text=f"Opción {i+1}", variable=correct_var, value=i,  # Radiobutton
                    bg=COLOR_PALETTE["BACKGROUND_LIGHT"], command=lambda i=i: correct_var.set(i)).pack(side=LEFT, padx=6)
        
    # GUARDAR: Botón para guardar la pregunta
    Button(form, text="💾 Guardar pregunta", bg="#4CAF50", fg="white",  # Botón
           relief="flat", bd=0, padx=14, pady=10,
           command=save_new_question).grid(row=4, column=1, sticky="e", pady=12)

    form.grid_columnconfigure(1, weight=1)  # Configura la columna para que se expanda

# FUNCIÓN: guarda una nueva pregunta en el JSON
def save_new_question():
    """
    Valida los datos del formulario, crea un diccionario de pregunta,
    lo guarda en el archivo JSON de la categoría y actualiza all_questions_data.
    """
    global all_questions_data
    
    categoria = new_cat_var.get()  # Obtiene la categoría seleccionada
    pregunta = new_question_text.get("1.0", END).strip()  # Obtiene el texto de la pregunta
    if not pregunta:  # Si no escribió pregunta
        messagebox.showerror("Error", "La pregunta no puede estar vacía.")  # Muestra error
        return
    
    opciones = [v.get().strip() for v in new_option_vars]  # Obtiene todas las opciones
    if any(not o for o in opciones):  # Si falta completar una opción
        messagebox.showerror("Error", "Completá las 4 opciones.")  # Muestra error
        return
    
    if len(set(opciones)) != 4:  # Si hay opciones repetidas
        messagebox.showerror("Error", "Las opciones no pueden repetirse.")  # Muestra error
        return
    
    idx = correct_var.get()  # Obtiene el índice de la opción correcta
    
    if categoria not in FILE_MAP:  # Si la categoría no existe
        messagebox.showerror("Error", "Seleccioná una categoría válida.")  # Muestra error
        return
        
    if idx < 0 or idx > 3:  # Si el índice es inválido
        messagebox.showerror("Error", "Seleccioná la respuesta correcta.")  # Muestra error
        return
        
    nueva = {  # Crea diccionario con la nueva pregunta
        "pregunta": pregunta,
        "opciones": opciones,
        "respuestaCorrecta": opciones[idx]  # Usa el texto de la opción correcta
    }
    
    ok, err = save_question_to_json(categoria, nueva)  # Guarda en el archivo JSON
    
    if ok:  # Si se guardó correctamente
        all_questions_data = load_questions(FILE_MAP)  # Recarga todas las preguntas
        messagebox.showinfo("Éxito", f"Pregunta agregada a '{categoria}'.")  # Muestra mensaje de éxito
        new_question_text.delete("1.0", END)  # Limpia el campo de pregunta
        for v in new_option_vars:
            v.set("")  # Limpia los campos de opciones
        correct_var.set(0)  # Resetea la opción correcta
        show_category_selection()  # Vuelve al menú de categorías
    else:
        messagebox.showerror("Error al guardar", f"No se pudo guardar: {err}")  # Muestra error

# FUNCIÓN: inicializa toda la aplicación
def initialize_app():
    """
    Punto de entrada: carga todas las preguntas, crea la ventana principal,
    los frames para cada pantalla y muestra el menú de categorías.
    """
    global all_questions_data, master_window
    global main_content_frame, category_frame, quiz_frame, results_frame, add_question_frame
    
    all_questions_data = load_questions(FILE_MAP)  # Carga todas las preguntas desde los JSON
    
    master_window = Tk()  # Crea la ventana principal
    master_window.title("🎯 Respondidos - Estilo Kahoot")  # Título de la ventana
    master_window.geometry("900x720")  # Tamaño: 900x720 píxeles
    master_window.config(bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Fondo gris claro

    title_label = Label(master_window, text="🎯Respondidos🎯", font=font_title,  # Título permanente
                        bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    title_label.pack(pady=8)
    
    main_content_frame = Frame(master_window, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])  # Frame principal
    main_content_frame.pack(fill="both", expand=True)

    category_frame = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)  # Frame de categorías
    quiz_frame = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)  # Frame del quiz
    results_frame = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)  # Frame de resultados
    add_question_frame = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)  # Frame de agregar preguntas
    
    show_category_selection()  # Muestra el menú de selección de categorías
    
    master_window.mainloop()  # Inicia el loop principal (mantiene la ventana abierta)

# === EJECUCIÓN ===

# Verifica que este archivo se ejecute como programa principal (no importado)
if __name__ == "__main__":
    initialize_app()  # Ejecuta la función principal
