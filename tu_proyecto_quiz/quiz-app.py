"""
RESPONDIDOS - APLICACIÓN DE PREGUNTAS Y RESPUESTAS - ESTILO KAHOOT
"""

import json
import random
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os

# --- CONFIGURACIÓN Y CARGA DE DATOS ---

FILE_MAP = {
    "Peliculas y Series": "PeliSeries.json",
    "Ciencia": "Ciencia.json",
    "Videojuegos": "Videojuegos.json",
    "Historia": "Historia.json",
    "Música": "Musica.json",
    "Futbol": "Futbol.json",
    "Star Wars": "StarWars.json"
}

NUM_QUESTIONS = 10

COLOR_PALETTE = {
    "BACKGROUND_LIGHT": "#d4d4d4",
    "PRIMARY_TEXT": "#1f2937",
    "SECONDARY_TEXT": "#6b7280",
    "SUCCESS": "#10b981",
    "ERROR": "#ef4444"
}

CATEGORY_COLORS = {
    "Peliculas y Series": {"bg": "#FFCC99", "hover": "#FFB880", "icon": "🎬", "fg": "#333"},
    "Ciencia": {"bg": "#B3E0B3", "hover": "#99CC99", "icon": "🔬", "fg": "#333"},
    "Videojuegos": {"bg": "#FFA0A0", "hover": "#FF8080", "icon": "🎮", "fg": "#333"},
    "Historia": {"bg": "#F3DFA2", "hover": "#EAC36E", "icon": "🏛️", "fg": "#2D2D2D"},
    "Música": {"bg": "#DDA0DD", "hover": "#CC88CC", "icon": "🎵", "fg": "#333"},
    "Futbol": {"bg": "#99CC99", "hover": "#80B380", "icon": "⚽", "fg": "#333"},
    "Star Wars": {"bg": "#ADD8E6", "hover": "#87CEEB", "icon": "🌌", "fg": "#191970"} 
}

# --- VARIABLES GLOBALES ---
all_questions = {}
current_questions = []
current_question_index = 0
score = 0
current_category = None
current_buttons = []

# --- FUNCIONES DE DATOS ---

def script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def load_questions(file_map):
    """Carga todas las preguntas desde los archivos JSON."""
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

# --- FUNCIONES DEL QUIZ ---

def start_quiz(category):
    """Inicia un nuevo quiz para la categoría seleccionada."""
    global current_questions, current_question_index, score, current_category
    
    if category not in all_questions or not all_questions[category] or len(all_questions[category]) < NUM_QUESTIONS:
        return False
    
    current_category = category
    score = 0
    current_question_index = 0
    questions = list(all_questions[category])
    random.shuffle(questions)
    current_questions = questions[:NUM_QUESTIONS]
    return True

def get_current_question():
    """Obtiene la pregunta actual."""
    if current_question_index < len(current_questions):
        return current_questions[current_question_index]
    return None

def check_answer(selected_option_index):
    """Verifica si la respuesta es correcta."""
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

def next_question():
    """Avanza a la siguiente pregunta."""
    global current_question_index
    current_question_index += 1
    return current_question_index < len(current_questions)

def get_results():
    """Obtiene los resultados del quiz."""
    return score, len(current_questions)

# --- FUNCIONES DE INTERFAZ ---

def clear_frame(frame):
    """Limpia todos los widgets de un frame."""
    for widget in frame.winfo_children():
        widget.destroy()

def show_category_selection():
    """Muestra la pantalla de selección de categorías."""
    clear_frame(main_content_frame)
    
    # Título
    Label(main_content_frame, text="🎯 Respondidos", font=("Inter", 28, "bold"),
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=20)

    Label(main_content_frame, text=f"Cada quiz tiene {NUM_QUESTIONS} preguntas", 
          font=("Inter", 12), bg=COLOR_PALETTE["BACKGROUND_LIGHT"], 
          fg=COLOR_PALETTE["SECONDARY_TEXT"]).pack(pady=4)

    grid = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    grid.pack(expand=True, fill="both", pady=10)

    cats = list(CATEGORY_COLORS.keys())
    for i, cat in enumerate(cats):
        colors = CATEGORY_COLORS[cat]
        num_q = len(all_questions.get(cat, []))
        has_questions = num_q >= NUM_QUESTIONS
        
        btn_state = "normal" if has_questions else "disabled"

        btn = Button(grid, text=f"{colors['icon']}  {cat}", font=("Inter", 18, "bold"),
                     bg=colors["bg"], fg=colors["fg"], activebackground=colors["hover"],
                     relief="flat", bd=0, padx=30, pady=18, state=btn_state,
                     command=lambda c=cat: start_quiz_ui(c))
        btn.grid(row=i // 2, column=i % 2, padx=16, pady=16, sticky="nsew")

    for i in range(2):
        grid.grid_columnconfigure(i, weight=1)

    # Botón para agregar pregunta
    Button(main_content_frame, text="➕ Agregar Pregunta", font=("Inter", 12),
           bg="#4CAF50", fg="white", activebackground="#45a049", relief="flat", 
           bd=0, padx=12, pady=10, command=show_add_question_ui).pack(pady=8)

def start_quiz_ui(category):
    """Inicia la interfaz del quiz."""
    if start_quiz(category):
        load_question_ui()
    else:
        messagebox.showerror("Error", f"No hay suficientes preguntas disponibles para esta categoría. Necesitas {NUM_QUESTIONS}.")

def load_question_ui():
    """Carga la interfaz de una pregunta."""
    clear_frame(main_content_frame)
    
    question = get_current_question()
    if not question:
        show_results_ui()
        return

    cat_info = CATEGORY_COLORS.get(current_category, {"hover": "#888", "icon": "?"})
    
    # Header
    header = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    header.pack(fill="x")
    
    Button(header, text="← Categorías", command=show_category_selection,
           relief="flat", bd=0, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=5)
    
    Label(header, text=f"Puntaje: {score}/{NUM_QUESTIONS}", font=("Inter", 12),
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SUCCESS"]).pack(side=RIGHT, padx=8)
    
    Label(header, text=f"{cat_info.get('icon','')}  {current_category}", font=("Inter", 12),
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=RIGHT, padx=8)

    Label(main_content_frame, text=f"Pregunta {current_question_index + 1} de {NUM_QUESTIONS}",
          font=("Inter", 10), bg=COLOR_PALETTE["BACKGROUND_LIGHT"], 
          fg=COLOR_PALETTE["SECONDARY_TEXT"]).pack()

    # Caja de pregunta
    question_container = Frame(main_content_frame, bg=cat_info["hover"], height=150)
    question_container.pack(pady=12, fill="x", padx=20) 
    question_container.pack_propagate(False) 

    Label(question_container, text=question["pregunta"], font=("Inter", 18, "bold"),
          bg=cat_info["hover"], fg="white", wraplength=750, 
          justify=CENTER).pack(expand=True, padx=20, pady=20)

    # Opciones
    options_frame = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    options_frame.pack(fill="both", expand=False, pady=10)

    kahoot_colors = ["#E74C3C", "#3498DB", "#F1C40F", "#2ECC71"]
    options_shuffled = random.sample(question["opciones"], len(question["opciones"]))
    global current_buttons
    current_buttons = []

    for i, opt_text in enumerate(options_shuffled):
        try:
            original_index = question["opciones"].index(opt_text)
        except ValueError:
            original_index = -1

        btn_color = kahoot_colors[i % len(kahoot_colors)]
        
        btn = Button(options_frame, text=opt_text, font=("Inter", 14, "bold"),
                     bg=btn_color, fg="white", activeforeground="white", 
                     wraplength=350, width=35, height=4,
                     relief="flat", bd=0, padx=20, pady=20,
                     command=lambda idx=original_index, opt=opt_text: handle_answer(idx, opt))
        
        btn.grid(row=i // 2, column=i % 2, padx=12, pady=12, sticky="nsew")
        current_buttons.append(btn)

    for col in range(2):
        options_frame.grid_columnconfigure(col, weight=1)

def handle_answer(selected_option_index, selected_option_text):
    """Maneja la respuesta del usuario."""
    global current_buttons
    
    for b in current_buttons:
        b.config(state="disabled")

    question = get_current_question()
    correct_answer = question.get("respuestaCorrecta", "")
    is_correct = check_answer(selected_option_index)

    for b in current_buttons:
        text = b.cget("text")
        if text == correct_answer:
            b.config(bg=COLOR_PALETTE["SUCCESS"])
        elif text == selected_option_text and not is_correct:
            b.config(bg=COLOR_PALETTE["ERROR"])

    if is_correct:
        message_text = "✅ ¡Correcto!"
    else:
        message_text = f"❌ Incorrecto. La respuesta correcta era:\n{correct_answer}"
    
    def next_step():
        messagebox.showinfo("Resultado", message_text)
        
        if next_question():
            load_question_ui()
        else:
            show_results_ui()
            
    root.after(500, next_step)

def show_results_ui():
    """Muestra la pantalla de resultados."""
    clear_frame(main_content_frame)
    
    score_val, total = get_results()
    pct = (score_val / total) * 100 if total > 0 else 0.0

    # Título
    Label(main_content_frame, text="🎯 Respondidos", font=("Inter", 28, "bold"),
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=10)

    Label(main_content_frame, text="RESULTADOS", font=("Inter", 28, "bold"),
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=10)
    
    Label(main_content_frame, text=f"{score_val}/{total} correctas - {pct:.1f}%", 
          font=("Inter", 18, "bold"), bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=8)

    ttk.Button(main_content_frame, text="🔄 Jugar de nuevo (misma categoría)",
               command=lambda: start_quiz_ui(current_category)).pack(pady=10)
    ttk.Button(main_content_frame, text="🏠 Volver al menú", command=show_category_selection).pack(pady=6)
    ttk.Button(main_content_frame, text="➕ Agregar Pregunta", command=show_add_question_ui).pack(pady=6)

def show_add_question_ui():
    """Muestra la pantalla para agregar preguntas."""
    clear_frame(main_content_frame)
    
    # Título
    Label(main_content_frame, text="🎯 Respondidos", font=("Inter", 28, "bold"),
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=10)

    header = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    header.pack(fill="x", pady=4)
    
    Button(header, text="← Volver", command=show_category_selection,
           relief="flat", bd=0, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=6)
    
    Label(header, text="➕ Agregar Nueva Pregunta", font=("Inter", 18, "bold"),
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=8)

    form = Frame(main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    form.pack(fill="both", expand=True, pady=12, padx=10)

    # Variables para el formulario
    new_cat_var = StringVar()
    new_question_text = Text(form, height=5, font=("Inter", 12), wrap=WORD)
    option_vars = [StringVar() for _ in range(4)]
    correct_var = IntVar(value=0)

    # Categoría
    Label(form, text="Categoría:", font=("Inter", 12), 
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=0, column=0, sticky="w", pady=6)
    
    cats = list(all_questions.keys())
    new_cat_var.set(cats[0] if cats else "Seleccionar")
    cat_combo = ttk.Combobox(form, textvariable=new_cat_var, values=cats, 
                            state="readonly", font=("Inter", 12))
    cat_combo.grid(row=0, column=1, sticky="ew", pady=6)

    # Pregunta
    Label(form, text="Pregunta:", font=("Inter", 12), 
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=1, column=0, sticky="nw", pady=6)
    
    new_question_text.grid(row=1, column=1, sticky="ew", pady=6)

    # Opciones (4)
    Label(form, text="Opciones (4):", font=("Inter", 12), 
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=2, column=0, sticky="nw", pady=6)
    
    opts_frame = Frame(form, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    opts_frame.grid(row=2, column=1, sticky="ew", pady=6)
    
    for i in range(4):
        Label(opts_frame, text=f"Opción {i+1}:", bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(
            row=i, column=0, sticky="w", padx=4, pady=4)
        Entry(opts_frame, textvariable=option_vars[i], font=("Inter", 12)).grid(
            row=i, column=1, sticky="ew", padx=4, pady=4)
        opts_frame.grid_columnconfigure(1, weight=1)

    # Respuesta correcta
    Label(form, text="Respuesta correcta:", font=("Inter", 12), 
          bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=3, column=0, sticky="w", pady=6)
    
    correct_frame = Frame(form, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    correct_frame.grid(row=3, column=1, sticky="w", pady=6)
    
    for i in range(4):
        Radiobutton(correct_frame, text=f"Opción {i+1}", variable=correct_var, value=i, 
                    bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=6)
            
    # Guardar
    def save_question():
        categoria = new_cat_var.get()
        pregunta = new_question_text.get("1.0", END).strip()
        if not pregunta:
            messagebox.showerror("Error", "La pregunta no puede estar vacía.")
            return
        
        opciones = [v.get().strip() for v in option_vars]
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
            global all_questions
            all_questions = load_questions(FILE_MAP)
            messagebox.showinfo("Éxito", f"Pregunta agregada a '{categoria}'.")
            new_question_text.delete("1.0", END)
            for v in option_vars:
                v.set("")
            correct_var.set(0)
            show_category_selection()
        else:
            messagebox.showerror("Error al guardar", f"No se pudo guardar: {err}")

    Button(form, text="💾 Guardar pregunta", bg="#4CAF50", fg="white",
           relief="flat", bd=0, padx=14, pady=10,
           command=save_question).grid(row=4, column=1, sticky="e", pady=12)

    form.grid_columnconfigure(1, weight=1)

# --- INICIALIZACIÓN ---
all_questions = load_questions(FILE_MAP)

root = Tk()
root.title("🎯 Respondidos - Estilo Kahoot")
root.geometry("900x720")
root.config(bg=COLOR_PALETTE["BACKGROUND_LIGHT"])

# Frame principal para el contenido
main_content_frame = Frame(root, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
main_content_frame.pack(fill="both", expand=True)

# Iniciar con la pantalla de categorías
show_category_selection()

root.mainloop()