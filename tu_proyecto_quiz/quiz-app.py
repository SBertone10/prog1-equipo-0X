"""
RESPONDIDOS - APLICACIÓN DE PREGUNTAS Y RESPUESTAS - ESTILO KAHOOT
Versión sin clases - Enfoque procedural
Con temporizador, barra de tiempo y sistema de ayudas
"""

import json
import random
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os

# ==============================
# 1️⃣  CONFIGURACIÓN Y CARGA DE DATOS
# ==============================
# --- 1. CONFIGURACIÓN Y CARGA DE DATOS ---

FILE_MAP = {
    "Peliculas y Series": "PeliSeries.json",
    "Ciencia": "Ciencia.json",
    "Videojuegos": "Videojuegos.json",
    "Historia": "Historia.json",
    "Música": "Musica.json",
    "Futbol": "Futbol.json",
    "Star Wars": "StarWars.json",
    "Rainbow Six Siege": "RainbowSixSiege.json"
}

# Variables globales para el estado del juego
current_questions = []
current_question_index = 0
score = 0
current_category = None
all_questions_data = {}
current_buttons = []
timer_running = False
time_left = 15
timer_id = None
helps_remaining = 2  # Ayudas disponibles por juego
helps_used_this_question = False  # Para evitar usar más de una ayuda por pregunta

NUM_QUESTIONS = 10

COLOR_PALETTE = {
    "BACKGROUND_LIGHT": "#d4d4d4",
    "PRIMARY_TEXT": "#1f2937",
    "SECONDARY_TEXT": "#6b7280",
    "SUCCESS": "#10b981",
    "ERROR": "#ef4444",
    "WARNING": "#f59e0b",
    "HELP": "#8B5CF6"
}

CATEGORY_COLORS = {
    "Peliculas y Series": {"bg": "#FFCC99", "hover": "#FFB880", "icon": "🎬", "fg": "#333"},
    "Ciencia": {"bg": "#B3E0B3", "hover": "#99CC99", "icon": "🔬", "fg": "#333"},
    "Videojuegos": {"bg": "#FFA0A0", "hover": "#FF8080", "icon": "🎮", "fg": "#333"},
    "Historia": {"bg": "#F3DFA2", "hover": "#EAC36E", "icon": "🏛️", "fg": "#2D2D2D"},
    "Música": {"bg": "#DDA0DD", "hover": "#CC88CC", "icon": "🎵", "fg": "#333"},
    "Futbol": {"bg": "#99CC99", "hover": "#80B380", "icon": "⚽", "fg": "#333"},
    "Star Wars": {"bg": "#ADD8E6", "hover": "#87CEEB", "icon": "🌌", "fg": "#191970"},
    "Rainbow Six Siege": {"bg": "#C0C0C0", "hover": "#A9A9A9", "icon": "🎯", "fg": "#000000"},
}


# --- Función: script_dir ---
# Devuelve la ruta del script actual.
def script_dir():
    return os.path.dirname(os.path.abspath(__file__))


# --- Función: load_questions ---
# Carga o muestra preguntas en la interfaz.
def load_questions(file_map):
    """Carga todas las preguntas desde los archivos JSON. Devuelve dict por categoría."""
    all_data = {}
    base = script_dir()
    for category_name, file_name in file_map.items():
        path = os.path.join(base, file_name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    all_data[category_name] = data
                else:
                    all_data[category_name] = data if isinstance(data, list) else []
        except FileNotFoundError:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                all_data[category_name] = []
            except Exception as e:
                print(f"No se pudo crear {file_name}: {e}")
        except json.JSONDecodeError:
            print(f"JSON inválido en {file_name}.")
            all_data[category_name] = []
        except Exception as e:
            print(f"Error cargando {file_name}: {e}")
            all_data[category_name] = []
    return all_data


# --- Función: save_question_to_json ---
# Guarda una nueva pregunta en el archivo JSON.
def save_question_to_json(category, new_question):
    """Agrega una nueva pregunta al JSON de la categoría."""
    base = script_dir()
    if category not in FILE_MAP:
        return False, "Categoría desconocida."
    path = os.path.join(base, FILE_MAP[category])
    try:
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
    except Exception:
        existing = []
    existing.append(new_question)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return True, None
    except Exception as e:
        return False, str(e)

# ==============================
# 2️⃣  LÓGICA DEL QUIZ (funciones principales del juego)
# ==============================
# --- 2. LÓGICA DEL QUIZ ---


# --- Función: start_quiz ---
# Inicia una nueva partida del quiz.
def start_quiz(category):
    """Inicia un nuevo quiz para la categoría seleccionada"""
    global current_questions, current_question_index, score, current_category, time_left, helps_remaining, helps_used_this_question
    
    if category not in all_questions_data or not isinstance(all_questions_data[category], list) or not all_questions_data[category] or len(all_questions_data[category]) < NUM_QUESTIONS:
        return False
    
    current_category = category
    score = 0
    current_question_index = 0
    time_left = 15
    helps_remaining = 2
    helps_used_this_question = False
    questions = list(all_questions_data[category])
    random.shuffle(questions)
    current_questions = questions[:NUM_QUESTIONS]
    return True


# --- Función: get_current_question ---
# Obtiene datos del estado actual (pregunta, resultado, etc.).
def get_current_question():
    """Obtiene la pregunta actual"""
    if current_question_index < len(current_questions):
        return current_questions[current_question_index]
    return None


# --- Función: check_answer ---
# Verifica si la respuesta seleccionada es correcta.
def check_answer(selected_option_index):
    """Verifica si la respuesta es correcta"""
    global score
    
    q = get_current_question()
    if not q:
        return False
    try:
        correct_answer = q["respuestaCorrecta"]
        correct_index = q["opciones"].index(correct_answer)
    except Exception:
        return False
    correct = (selected_option_index == correct_index)
    if correct:
        score += 1
    return correct


# --- Función: next_question ---
# Avanza a la siguiente pregunta o pantalla.
def next_question():
    """Avanza a la siguiente pregunta"""
    global current_question_index, time_left, helps_used_this_question
    current_question_index += 1
    time_left = 15
    helps_used_this_question = False
    return current_question_index < len(current_questions)


# --- Función: get_results ---
# Muestra o calcula los resultados finales.
def get_results():
    """Obtiene los resultados del quiz"""
    return score, len(current_questions)

# ==============================
# 3️⃣  TEMPORIZADOR Y BARRA DE TIEMPO
# ==============================
# --- 3. TEMPORIZADOR Y BARRA DE TIEMPO ---


# --- Función: start_timer ---
# Controla el temporizador o la barra de tiempo.
def start_timer():
    """Inicia el temporizador para la pregunta actual"""
    global timer_running, time_left, timer_id
    timer_running = True
    time_left = 15
    update_timer_display()
    update_time_bar()
    timer_id = master_window.after(1000, update_timer)


# --- Función: stop_timer ---
# Controla el temporizador o la barra de tiempo.
def stop_timer():
    """Detiene el temporizador"""
    global timer_running, timer_id
    timer_running = False
    if timer_id:
        master_window.after_cancel(timer_id)
        timer_id = None


# --- Función: update_timer ---
# Controla el temporizador o la barra de tiempo.
def update_timer():
    """Actualiza el temporizador cada segundo"""
    global time_left, timer_running, timer_id
    
    if not timer_running:
        return
        
    time_left -= 1
    update_timer_display()
    update_time_bar()
    
    if time_left <= 0:
        # Tiempo agotado
        stop_timer()
        time_up()
    else:
        timer_id = master_window.after(1000, update_timer)


# --- Función: update_timer_display ---
# Controla el temporizador o la barra de tiempo.
def update_timer_display():
    """Actualiza la visualización del temporizador en la interfaz"""
    if hasattr(update_timer_display, 'timer_label') and update_timer_display.timer_label:
        color = COLOR_PALETTE["SUCCESS"] if time_left > 5 else COLOR_PALETTE["ERROR"]
        update_timer_display.timer_label.config(text=f"⏱️ {time_left}s", fg=color)


# --- Función: update_time_bar ---
# Controla el temporizador o la barra de tiempo.
def update_time_bar():
    """Actualiza la barra de tiempo horizontal"""
    if hasattr(update_time_bar, 'time_bar_canvas') and update_time_bar.time_bar_canvas:
        # Obtener el ancho actual del canvas
        canvas_width = update_time_bar.time_bar_canvas.winfo_width()
        if canvas_width <= 1:  # Si aún no se ha renderizado, usar ancho por defecto
            canvas_width = 860
        
        # Calcular el porcentaje de tiempo restante
        percentage = (time_left / 15) * 100
        
        # Cambiar color según el tiempo restante
        if time_left > 5:
            color = COLOR_PALETTE["SUCCESS"]
        elif time_left > 2:
            color = COLOR_PALETTE["WARNING"]
        else:
            color = COLOR_PALETTE["ERROR"]
        
        # Actualizar ancho de la barra (de derecha a izquierda)
        bar_width = (percentage / 100) * canvas_width
        x_start = canvas_width - bar_width  # Comenzar desde la derecha
        update_time_bar.time_bar_canvas.coords(update_time_bar.time_bar_rect, x_start, 0, canvas_width, 10)
        update_time_bar.time_bar_canvas.itemconfig(update_time_bar.time_bar_rect, fill=color)


# --- Función: create_time_bar ---
# Controla el temporizador o la barra de tiempo.
def create_time_bar(parent):
    """Crea la barra de tiempo horizontal dentro de la caja de pregunta"""
    # Frame para contener la barra de tiempo (mismo ancho que la caja de pregunta)
    time_bar_container = Frame(parent, bg=cat_info["hover"], height=15)
    time_bar_container.pack(fill="x", padx=0, pady=(0, 0))
    time_bar_container.pack_propagate(False)
    
    # Canvas para la barra de tiempo con ancho completo
    update_time_bar.time_bar_canvas = Canvas(time_bar_container, height=10, bg=cat_info["hover"], highlightthickness=0)
    update_time_bar.time_bar_canvas.pack(fill="x", padx=0)
    
    # Crear la barra de tiempo (inicialmente llena, desde la derecha)
    # El ancho se actualizará automáticamente cuando el canvas se renderice
    update_time_bar.time_bar_rect = update_time_bar.time_bar_canvas.create_rectangle(
        0, 0, 860, 10, fill=COLOR_PALETTE["SUCCESS"], outline=""
    )
    
    # Forzar actualización después de que la ventana se renderice
    master_window.update_idletasks()
    update_time_bar()


# --- Función: time_up ---
# Controla el temporizador o la barra de tiempo.
def time_up():
    """Maneja cuando se acaba el tiempo"""
    global current_buttons
    
    # Deshabilitar todos los botones
    for b in current_buttons:
        b.config(state="disabled")
    
    # Deshabilitar botón de ayuda
    if hasattr(load_question_ui, 'help_button'):
        load_question_ui.help_button.config(state="disabled")
    
    q = get_current_question()
    if not q:
        return
        
    correct_answer = q.get("respuestaCorrecta", "")
    
    # Mostrar la respuesta correcta en verde y las incorrectas en rojo
    for b in current_buttons:
        text = b.cget("text")
        if text == correct_answer:
            b.config(bg=COLOR_PALETTE["SUCCESS"], fg="white")  # Texto blanco para respuesta correcta
        else:
            b.config(bg=COLOR_PALETTE["ERROR"])
    
    # Cambiar el texto de la pregunta a "TIEMPO AGOTADO"
    if hasattr(load_question_ui, 'question_label'):
        load_question_ui.question_label.config(text="⏰ TIEMPO AGOTADO", bg=COLOR_PALETTE["ERROR"])
    
    # Avanzar después de un breve delay
    master_window.after(2000, advance_after_timeout)


# --- Función: advance_after_timeout ---
# Controla el temporizador o la barra de tiempo.
def advance_after_timeout():
    """Avanza a la siguiente pregunta después de que se acabe el tiempo"""
    if next_question():
        load_question_ui()
    else:
        show_results_ui()

# ==============================
# 4️⃣  SISTEMA DE AYUDAS (elimina opciones incorrectas)
# ==============================
# --- 4. SISTEMA DE AYUDAS ---


# --- Función: use_help ---
# Gestiona las ayudas (elimina opciones incorrectas).
def use_help():
    """Usa una ayuda para eliminar 2 opciones incorrectas"""
    global helps_remaining, helps_used_this_question, current_buttons
    
    if helps_remaining <= 0 or helps_used_this_question:
        return
        
    helps_remaining -= 1
    helps_used_this_question = True
    
    # Actualizar el botón de ayuda
    if hasattr(load_question_ui, 'help_button'):
        if helps_remaining > 0:
            load_question_ui.help_button.config(text=f"❓ Ayuda ({helps_remaining} restantes)", state="normal")
        else:
            load_question_ui.help_button.config(text="❓ Ayudas agotadas", state="disabled")
    
    q = get_current_question()
    if not q:
        return
        
    correct_answer = q.get("respuestaCorrecta", "")
    
    # Encontrar índices de las opciones incorrectas
    incorrect_indices = []
    for i, button in enumerate(current_buttons):
        if button.cget("text") != correct_answer and button.cget("state") == "normal":
            incorrect_indices.append(i)
    
    # Mezclar y tomar 2 opciones incorrectas para eliminar
    if len(incorrect_indices) >= 2:
        random.shuffle(incorrect_indices)
        to_remove = incorrect_indices[:2]
        
        # Eliminar (ocultar y deshabilitar) las 2 opciones seleccionadas
        for index in to_remove:
            current_buttons[index].config(state="disabled", bg="#666666", fg="#999999", text="❌ Eliminada")
    
    # Si solo queda 1 opción incorrecta, eliminar esa
    elif len(incorrect_indices) == 1:
        current_buttons[incorrect_indices[0]].config(state="disabled", bg="#666666", fg="#999999", text="❌ Eliminada")

# ==============================
# 5️⃣  INTERFAZ GRÁFICA CON TKINTER
# ==============================
# --- 5. INTERFAZ GRÁFICA (TKINTER) ---

# Variables globales para la interfaz
main_content_frame = None
category_frame = None
quiz_frame = None
results_frame = None
add_question_frame = None
master_window = None

# Constantes para la interfaz
BUTTON_PAD_NORMAL = 20
BUTTON_WIDTH_FIXED = 35
BUTTON_HEIGHT_FIXED = 4
BUTTON_WRAPLENGTH = 350

font_title = ("Inter", 28, "bold")
font_large = ("Inter", 18, "bold")
font_medium = ("Inter", 12)
font_small = ("Inter", 10)


# --- Función: clear_all_frames ---
# Limpia frames o widgets previos para cambiar de pantalla.
def clear_all_frames():
    """Limpia todos los frames de contenido"""
    for f in [category_frame, quiz_frame, results_frame, add_question_frame]:
        if f:
            f.pack_forget()


# --- Función: create_tooltip ---
# Función auxiliar del juego.
def create_tooltip(widget, text):
    """Crea un tooltip para un widget"""
    tooltip_window = None

# --- Función: enter ---
# Función auxiliar del juego.
    def enter(event):
        nonlocal tooltip_window
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        tooltip_window = Toplevel(widget)
        tooltip_window.wm_overrideredirect(True)
        tooltip_window.wm_geometry(f"+{x}+{y}")
        Label(tooltip_window, text=text, background="#ffffe0", relief="solid", borderwidth=1,
              font=("tahoma", "8", "normal")).pack()
    

# --- Función: leave ---
# Función auxiliar del juego.
    def leave(event):
        nonlocal tooltip_window
        if tooltip_window:
            tooltip_window.destroy()
            tooltip_window = None
    
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)


# --- Función: show_category_selection ---
# Muestra la pantalla de selección de categorías.
def show_category_selection():
    """Muestra la pantalla de selección de categorías"""
    stop_timer()  # Detener cualquier temporizador activo
    clear_all_frames()
    for w in category_frame.winfo_children():
        w.destroy()
    category_frame.pack(fill="both", expand=True)

    Label(category_frame, text=f"Cada quiz tiene {NUM_QUESTIONS} preguntas", font=font_medium,
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SECONDARY_TEXT"]).pack(pady=4)

    grid = Frame(category_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    grid.pack(expand=True, fill="both", pady=10)

    # CORREGIDO: Usar solo las categorías definidas en CATEGORY_COLORS
    # y asegurarse de que no haya duplicados
    cats = list(CATEGORY_COLORS.keys())
    
    # Verificar que no haya duplicados
    seen = set()
    unique_cats = []
    for cat in cats:
        if cat not in seen:
            seen.add(cat)
            unique_cats.append(cat)
    
    cats = unique_cats

    for i, cat in enumerate(cats):
        colors = CATEGORY_COLORS.get(cat, {"bg": "#DDDDDD", "hover": "#CCCCCC", "icon": "❓", "fg": "#111"})
        num_q = len(all_questions_data.get(cat, []))
        has_questions = num_q >= NUM_QUESTIONS

        btn_state = "normal" if has_questions else "disabled"
        tooltip_text = ""
        if not has_questions:
             tooltip_text = f"Faltan preguntas para el quiz ({num_q}/{NUM_QUESTIONS})"

        btn = Button(grid, text=f"{colors['icon']}  {cat}", font=font_large,
                     bg=colors["bg"], fg=colors["fg"], activebackground=colors["hover"],
                     relief="flat", bd=0, padx=30, pady=18, state=btn_state,
                     command=lambda c=cat: start_quiz_ui(c))
        btn.grid(row=i // 2, column=i % 2, padx=16, pady=16, sticky="nsew")

        if not has_questions:
            create_tooltip(btn, tooltip_text)

    for i in range(2):
        grid.grid_columnconfigure(i, weight=1)

    # Botón para agregar pregunta
    Button(category_frame, text="➕ Agregar Pregunta", font=font_medium,
           bg="#4CAF50", fg="white", activebackground="#45a049", relief="flat", bd=0, padx=12, pady=10,
           command=show_add_question_ui).pack(pady=8)


# --- Función: start_quiz_ui ---
# Inicia una nueva partida del quiz.
def start_quiz_ui(category):
    """Inicia la interfaz del quiz para una categoría"""
    if start_quiz(category):
        clear_all_frames()
        quiz_frame.pack(fill="both", expand=True)
        load_question_ui()
    else:
        messagebox.showerror("Error", f"No hay suficientes preguntas disponibles para esta categoría. Necesitas {NUM_QUESTIONS}.")


# --- Función: load_question_ui ---
# Carga o muestra preguntas en la interfaz.
def load_question_ui():
    """Carga y muestra la pregunta actual en la interfaz"""
    global current_buttons, cat_info
    
    # Limpiar widgets previos
    for w in quiz_frame.winfo_children():
        w.destroy()
    
    current_buttons = []
    stop_timer()  # Detener temporizador anterior

    question = get_current_question()
    if not question:
        show_results_ui()
        return

    cat_info = CATEGORY_COLORS.get(current_category, {"hover": "#888", "icon": "?"})
    header = Frame(quiz_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    header.pack(fill="x")
    Button(header, text="← Categorías", command=show_category_selection,
           relief="flat", bd=0, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=5)
    
    # Temporizador en el header
    update_timer_display.timer_label = Label(header, text=f"⏱️ {time_left}s", font=font_medium,
                                            bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SUCCESS"])
    update_timer_display.timer_label.pack(side=RIGHT, padx=8)
    
    Label(header, text=f"Puntaje: {score}/{NUM_QUESTIONS}", font=font_medium,
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SUCCESS"]).pack(side=RIGHT, padx=8)
    Label(header, text=f"{cat_info.get('icon','')}  {current_category}", font=font_medium,
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=RIGHT, padx=8)

    Label(quiz_frame, text=f"Pregunta {current_question_index + 1} de {NUM_QUESTIONS}",
          font=font_small, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SECONDARY_TEXT"]).pack()

    # CAJA DE PREGUNTA (TAMAÑO FIJO)
    question_container = Frame(quiz_frame, bg=cat_info["hover"], height=150)
    question_container.pack(pady=12, fill="x", padx=20) 
    question_container.pack_propagate(False) 

    # Guardar referencia al label de la pregunta para poder cambiarlo después
    load_question_ui.question_label = Label(question_container, text=question["pregunta"], font=font_large,
          bg=cat_info["hover"], fg="white", wraplength=750, 
          justify=CENTER)
    load_question_ui.question_label.pack(expand=True, padx=20, pady=20)

    # BARRA DE TIEMPO HORIZONTAL (dentro de la caja de pregunta)
    create_time_bar(question_container)

    # Opciones 2x2 estilo Kahoot
    options_frame = Frame(quiz_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    options_frame.pack(fill="both", expand=False, pady=10)

    kahoot_colors = ["#E74C3C", "#3498DB", "#F1C40F", "#2ECC71"]
    options_shuffled = random.sample(question["opciones"], len(question["opciones"]))
    current_buttons = []

    for i, opt_text in enumerate(options_shuffled):
        try:
            original_index = question["opciones"].index(opt_text)
        except ValueError:
            original_index = -1

        btn_color = kahoot_colors[i % len(kahoot_colors)]
        
        # Creación de botones con tamaño fijo
        btn = Button(options_frame, text=opt_text, font=("Inter", 14, "bold"),
                     bg=btn_color, fg="white", activeforeground="white", 
                     wraplength=BUTTON_WRAPLENGTH,
                     width=BUTTON_WIDTH_FIXED,
                     height=BUTTON_HEIGHT_FIXED,
                     relief="flat", bd=0, 
                     padx=BUTTON_PAD_NORMAL, pady=BUTTON_PAD_NORMAL,
                     command=lambda idx=original_index, opt=opt_text: handle_answer(idx, opt))
        
        btn.grid(row=i // 2, column=i % 2, padx=12, pady=12, sticky="nsew")
        
        current_buttons.append(btn)

    for col in range(2):
        options_frame.grid_columnconfigure(col, weight=1)

    # BOTÓN DE AYUDA (centrado debajo de las opciones)
    help_frame = Frame(quiz_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    help_frame.pack(pady=15)
    
    help_button_text = f"❓ Ayuda ({helps_remaining} restantes)"
    load_question_ui.help_button = Button(help_frame, text=help_button_text, font=("Inter", 14, "bold"),
                                         bg=COLOR_PALETTE["HELP"], fg="white", 
                                         activebackground="#7C3AED", activeforeground="white",
                                         relief="flat", bd=0, padx=25, pady=15,
                                         command=use_help)
    load_question_ui.help_button.pack()

    # Iniciar temporizador después de que la interfaz se haya renderizado
    master_window.after(100, start_timer)


# --- Función: handle_answer ---
# Maneja la acción del jugador al seleccionar una respuesta.
def handle_answer(selected_option_index, selected_option_text):
    """Maneja la selección de una respuesta"""
    global current_buttons
    
    stop_timer()  # Detener el temporizador cuando se responde
    
    for b in current_buttons:
        b.config(state="disabled")

    # Deshabilitar botón de ayuda
    if hasattr(load_question_ui, 'help_button'):
        load_question_ui.help_button.config(state="disabled")

    q = get_current_question()
    correct_answer = q.get("respuestaCorrecta", "")
    is_correct = check_answer(selected_option_index)

    # Cambiar el texto de la pregunta según si es correcto o incorrecto
    if hasattr(load_question_ui, 'question_label'):
        if is_correct:
            load_question_ui.question_label.config(text="✅ CORRECTO", bg=COLOR_PALETTE["SUCCESS"])
        else:
            load_question_ui.question_label.config(text="❌ INCORRECTO", bg=COLOR_PALETTE["ERROR"])

    # Colorear respuestas: correcta en verde, incorrectas en rojo
    for b in current_buttons:
        text = b.cget("text")
        
        if text == correct_answer:
            b.config(bg=COLOR_PALETTE["SUCCESS"], fg="white")  # Texto blanco para respuesta correcta
        elif text == selected_option_text and not is_correct:
            b.config(bg=COLOR_PALETTE["ERROR"])
        else:
            b.config(bg=COLOR_PALETTE["ERROR"])  # Las otras opciones incorrectas también en rojo

    # Avanzar después de un breve delay para ver los resultados
    master_window.after(2000, advance_to_next)


# --- Función: advance_to_next ---
# Avanza a la siguiente pregunta o pantalla.
def advance_to_next():
    """Avanza a la siguiente pregunta después de mostrar los resultados"""
    if next_question():
        load_question_ui()
    else:
        show_results_ui()


# --- Función: show_results_ui ---
# Muestra o calcula los resultados finales.
def show_results_ui():
    """Muestra la pantalla de resultados"""
    stop_timer()  # Detener cualquier temporizador activo
    clear_all_frames()
    results_frame.pack(fill="both", expand=True)

    # Limpiar widgets previos del marco de resultados
    for w in results_frame.winfo_children():
        w.destroy()

    score_val, total = get_results()
    pct = (score_val / total) * 100 if total > 0 else 0.0

    Label(results_frame, text="RESULTADOS", font=font_title,
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=10)
    Label(results_frame, text=f"{score_val}/{total} correctas - {pct:.1f}%", font=font_large,
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=8)

    ttk.Button(results_frame, text="🔄 Jugar de nuevo (misma categoría)",
               command=lambda: start_quiz_ui(current_category)).pack(pady=10)
    ttk.Button(results_frame, text="🏠 Volver al menú", command=show_category_selection).pack(pady=6)
    ttk.Button(results_frame, text="➕ Agregar Pregunta", command=show_add_question_ui).pack(pady=6)

# Variables para el formulario de agregar preguntas
new_cat_var = None
new_question_text = None
new_option_vars = []
correct_var = None


# --- Función: show_add_question_ui ---
# Función auxiliar del juego.
def show_add_question_ui():
    """Muestra la interfaz para agregar nuevas preguntas"""
    global new_cat_var, new_question_text, new_option_vars, correct_var
    
    stop_timer()  # Detener cualquier temporizador activo
    clear_all_frames()
    add_question_frame.pack(fill="both", expand=True)

    header = Frame(add_question_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    header.pack(fill="x", pady=4)
    Button(header, text="← Volver", command=show_category_selection,
           relief="flat", bd=0, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=6)
    Label(header, text="➕ Agregar Nueva Pregunta", font=font_large,
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=8)

    form = Frame(add_question_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    form.pack(fill="both", expand=True, pady=12, padx=10)

    # Categoría
    Label(form, text="Categoría:", font=font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=0, column=0, sticky="w", pady=6)
    new_cat_var = StringVar()
    # CORREGIDO: Usar solo las categorías definidas en CATEGORY_COLORS
    cats = list(CATEGORY_COLORS.keys())
    new_cat_var.set(cats[0] if cats else "Seleccionar")
    cat_combo = ttk.Combobox(form, textvariable=new_cat_var, values=cats, state="readonly", font=font_medium)
    cat_combo.grid(row=0, column=1, sticky="ew", pady=6)

    # Pregunta
    Label(form, text="Pregunta:", font=font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=1, column=0, sticky="nw", pady=6)
    new_question_text = Text(form, height=5, font=font_medium, wrap=WORD)
    new_question_text.grid(row=1, column=1, sticky="ew", pady=6)

    # Opciones (4)
    Label(form, text="Opciones (4):", font=font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=2, column=0, sticky="nw", pady=6)
    opts_frame = Frame(form, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    opts_frame.grid(row=2, column=1, sticky="ew", pady=6)
    
    new_option_vars = []
    for i in range(4):
        var = StringVar()
        Label(opts_frame, text=f"Opción {i+1}:", bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=i, column=0, sticky="w", padx=4, pady=4)
        Entry(opts_frame, textvariable=var, font=font_medium).grid(row=i, column=1, sticky="ew", padx=4, pady=4)
        opts_frame.grid_columnconfigure(1, weight=1)
        new_option_vars.append(var)

    # Respuesta correcta (radio)
    Label(form, text="Respuesta correcta:", font=font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=3, column=0, sticky="w", pady=6)
    correct_var = IntVar(value=0)
    correct_frame = Frame(form, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    correct_frame.grid(row=3, column=1, sticky="w", pady=6)
    for i in range(4):
        Radiobutton(correct_frame, text=f"Opción {i+1}", variable=correct_var, value=i, 
                    bg=COLOR_PALETTE["BACKGROUND_LIGHT"], command=lambda i=i: correct_var.set(i)).pack(side=LEFT, padx=6)
        
    # Guardar
    Button(form, text="💾 Guardar pregunta", bg="#4CAF50", fg="white",
           relief="flat", bd=0, padx=14, pady=10,
           command=save_new_question).grid(row=4, column=1, sticky="e", pady=12)

    # Ajustes de grid
    form.grid_columnconfigure(1, weight=1)


# --- Función: save_new_question ---
# Guarda una nueva pregunta en el archivo JSON.
def save_new_question():
    """Guarda una nueva pregunta en el archivo JSON"""
    global all_questions_data
    
    categoria = new_cat_var.get()
    pregunta = new_question_text.get("1.0", END).strip()
    if not pregunta:
        messagebox.showerror("Error", "La pregunta no puede estar vacía.")
        return
    opciones = [v.get().strip() for v in new_option_vars]
    if any(not o for o in opciones):
        messagebox.showerror("Error", "Completá las 4 opciones.")
        return
    if len(set(opciones)) != 4:
        messagebox.showerror("Error", "Las opciones no pueden repetirse.")
        return
    idx = correct_var.get()
    
    if categoria not in FILE_MAP:
        messagebox.showerror("Error", "Seleccioná una categoría válida.")
        return
        
    if idx < 0 or idx > 3:
        messagebox.showerror("Error", "Seleccioná la respuesta correcta.")
        return
        
    nueva = {
        "pregunta": pregunta,
        "opciones": opciones,
        "respuestaCorrecta": opciones[idx]
    }
    
    ok, err = save_question_to_json(categoria, nueva)
    
    if ok:
        all_questions_data = load_questions(FILE_MAP)
        messagebox.showinfo("Éxito", f"Pregunta agregada a '{categoria}'.")
        new_question_text.delete("1.0", END)
        for v in new_option_vars:
            v.set("")
        correct_var.set(0)
        show_category_selection()
    else:
        messagebox.showerror("Error al guardar", f"No se pudo guardar: {err}")


# --- Función: initialize_app ---
# Inicializa la aplicación y la ventana principal.
def initialize_app():
    """Inicializa la aplicación"""
    global all_questions_data, master_window
    global main_content_frame, category_frame, quiz_frame, results_frame, add_question_frame
    
    # Cargar datos
    all_questions_data = load_questions(FILE_MAP)
    
    # Crear ventana principal
    master_window = Tk()
    master_window.title("🎯 Respondidos - Estilo Kahoot")
    master_window.geometry("900x720")
    master_window.config(bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    # Hacer la ventana responsive
    master_window.minsize(800, 600)

    # TÍTULO PERMANENTE
    title_label = Label(master_window, text="🎯Respondidos🎯", font=font_title,
                        bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    title_label.pack(pady=8)
    
    # Contenedor principal de vistas
    main_content_frame = Frame(master_window, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    main_content_frame.pack(fill="both", expand=True)

    # Frames de contenido
    category_frame = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)
    quiz_frame = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)
    results_frame = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)
    add_question_frame = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)
    
    # Mostrar pantalla inicial
    show_category_selection()
    
    # Iniciar loop principal
    master_window.mainloop()

# ==============================
# 🔚 EJECUCIÓN PRINCIPAL DEL PROGRAMA
# ==============================
# --- EJECUCIÓN ---
if __name__ == "__main__":
    initialize_app()
