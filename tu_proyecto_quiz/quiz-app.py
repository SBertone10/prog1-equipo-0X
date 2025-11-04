"""
RESPONDIDOS - APLICACIÓN DE PREGUNTAS Y RESPUESTAS - ESTILO KAHOOT
Versión Final: Incluye todas las categorías solicitadas y optimizaciones.
CORRECCIÓN FINAL: Eliminado el efecto hover de los botones de respuesta y ajustados los tamaños.
"""

import json
import random
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os

# --- 1. CONFIGURACIÓN Y CARGA DE DATOS ---

FILE_MAP = {
    "Peliculas y Series": "PeliSeries.json",
    "Ciencia": "Ciencia.json",
    "Videojuegos": "Videojuegos.json",
    "Historia": "Historia.json",
    "Música": "Musica.json",
    "Futbol": "Futbol.json",
    "Star Wars": "StarWars.json"
}

def script_dir():
    return os.path.dirname(os.path.abspath(__file__))

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

ALL_QUESTIONS = load_questions(FILE_MAP)
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

# --- 2. LÓGICA DEL QUIZ ---

class QuizLogic:
    def __init__(self, data):
        self.all_data = data
        self.current_questions = []
        self.current_question_index = 0
        self.score = 0
        self.current_category = None

    def start_quiz(self, category):
        if category not in self.all_data or not isinstance(self.all_data[category], list) or not self.all_data[category] or len(self.all_data[category]) < NUM_QUESTIONS:
            return False
        self.current_category = category
        self.score = 0
        self.current_question_index = 0
        questions = list(self.all_data[category])
        random.shuffle(questions)
        self.current_questions = questions[:NUM_QUESTIONS]
        return True

    def get_current_question(self):
        if self.current_question_index < len(self.current_questions):
            return self.current_questions[self.current_question_index]
        return None

    def check_answer(self, selected_option_index):
        q = self.get_current_question()
        if not q:
            return False
        try:
            correct_answer = q["respuestaCorrecta"]
            correct_index = q["opciones"].index(correct_answer)
        except Exception:
            return False
        correct = (selected_option_index == correct_index)
        if correct:
            self.score += 1
        return correct

    def next_question(self):
        self.current_question_index += 1
        return self.current_question_index < len(self.current_questions)

    def get_results(self):
        return self.score, len(self.current_questions)

# --- 3. INTERFAZ GRÁFICA (TKINTER) ---

class QuizApp:
    def __init__(self, master, quiz_logic):
        self.master = master
        self.quiz = quiz_logic
        self.current_buttons = []

        master.title("🎯 Respondidos - Estilo Kahoot")
        master.geometry("900x720")
        master.config(bg=COLOR_PALETTE["BACKGROUND_LIGHT"])

        self.font_title = ("Inter", 28, "bold")
        self.font_large = ("Inter", 18, "bold")
        self.font_medium = ("Inter", 12)
        self.font_small = ("Inter", 10)
        
        # Constantes para el padding (solo normal, el hover pad ya no se usa para agrandar)
        self.BUTTON_PAD_NORMAL = 20

        # Constantes para tamaño fijo de las cajas de respuesta (AJUSTADO)
        self.BUTTON_WIDTH_FIXED = 35
        self.BUTTON_HEIGHT_FIXED = 4
        self.BUTTON_WRAPLENGTH = 350

        # Contenedor principal de vistas
        self.main_content_frame = Frame(master, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
        self.main_content_frame.pack(fill="both", expand=True)

        # Frames de contenido, empaquetados dentro de main_content_frame
        self.category_frame = Frame(self.main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)
        self.quiz_frame = Frame(self.main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)
        self.results_frame = Frame(self.main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)
        self.add_question_frame = Frame(self.main_content_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], padx=20, pady=20)
        
        self.show_category_selection()

    def clear_all_frames(self):
        for f in [self.category_frame, self.quiz_frame, self.results_frame, self.add_question_frame]:
            f.pack_forget()

    # ----------------- PANTALLA DE CATEGORÍAS -----------------
    def show_category_selection(self):
        self.clear_all_frames()
        self.category_frame.pack(fill="both", expand=True)

        Label(self.category_frame, text=f"Cada quiz tiene {NUM_QUESTIONS} preguntas", font=self.font_medium,
              bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SECONDARY_TEXT"]).pack(pady=4)

        grid = Frame(self.category_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
        grid.pack(expand=True, fill="both", pady=10)

        cats = list(CATEGORY_COLORS.keys())
        for i, cat in enumerate(cats):
            colors = CATEGORY_COLORS[cat]
            num_q = len(self.quiz.all_data.get(cat, []))
            has_questions = num_q >= NUM_QUESTIONS
            
            btn_state = "normal" if has_questions else "disabled"
            tooltip_text = ""
            if not has_questions:
                 tooltip_text = f"Faltan preguntas para el quiz ({num_q}/{NUM_QUESTIONS})"

            btn = Button(grid, text=f"{colors['icon']}  {cat}", font=self.font_large,
                         bg=colors["bg"], fg=colors["fg"], activebackground=colors["hover"],
                         relief="flat", bd=0, padx=30, pady=18, state=btn_state,
                         command=lambda c=cat: self.start_quiz_ui(c))
            btn.grid(row=i // 2, column=i % 2, padx=16, pady=16, sticky="nsew")

            if not has_questions:
                self.create_tooltip(btn, tooltip_text)


        for i in range(2):
            grid.grid_columnconfigure(i, weight=1)

        # Botón para agregar pregunta
        Button(self.category_frame, text="➕ Agregar Pregunta", font=self.font_medium,
               bg="#4CAF50", fg="white", activebackground="#45a049", relief="flat", bd=0, padx=12, pady=10,
               command=self.show_add_question_ui).pack(pady=8)

    # Helper para tooltip (requiere Toplevel)
    def create_tooltip(self, widget, text):
        tooltip_window = None
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
        
        def leave(event):
            nonlocal tooltip_window
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    # ----------------- INICIAR QUIZ -----------------
    def start_quiz_ui(self, category):
        if self.quiz.start_quiz(category):
            self.clear_all_frames()
            self.quiz_frame.pack(fill="both", expand=True)
            self.load_question_ui()
        else:
            messagebox.showerror("Error", f"No hay suficientes preguntas disponibles para esta categoría. Necesitas {NUM_QUESTIONS}.")


    # ----------------- CARGAR PREGUNTA (UI) -----------------
    def load_question_ui(self):
        for w in self.quiz_frame.winfo_children():
            w.destroy()

        question = self.quiz.get_current_question()
        if not question:
            self.show_results_ui()
            return

        cat_info = CATEGORY_COLORS.get(self.quiz.current_category, {"hover": "#888", "icon": "?"})
        header = Frame(self.quiz_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
        header.pack(fill="x")
        Button(header, text="← Categorías", command=self.show_category_selection,
               relief="flat", bd=0, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=5)
        Label(header, text=f"Puntaje: {self.quiz.score}/{NUM_QUESTIONS}", font=self.font_medium,
              bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SUCCESS"]).pack(side=RIGHT, padx=8)
        Label(header, text=f"{cat_info.get('icon','')}  {self.quiz.current_category}", font=self.font_medium,
              bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=RIGHT, padx=8)

        Label(self.quiz_frame, text=f"Pregunta {self.quiz.current_question_index + 1} de {NUM_QUESTIONS}",
              font=self.font_small, bg=COLOR_PALETTE["BACKGROUND_LIGHT"], fg=COLOR_PALETTE["SECONDARY_TEXT"]).pack()

        # CAJA DE PREGUNTA (TAMAÑO FIJO)
        question_container = Frame(self.quiz_frame, bg=cat_info["hover"], height=150)
        question_container.pack(pady=12, fill="x", padx=20) 
        question_container.pack_propagate(False) 

        Label(question_container, text=question["pregunta"], font=self.font_large,
              bg=cat_info["hover"], fg="white", wraplength=750, 
              justify=CENTER).pack(expand=True, padx=20, pady=20)

        # Opciones 2x2 estilo Kahoot
        options_frame = Frame(self.quiz_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
        options_frame.pack(fill="both", expand=False, pady=10)

        kahoot_colors = ["#E74C3C", "#3498DB", "#F1C40F", "#2ECC71"]
        options_shuffled = random.sample(question["opciones"], len(question["opciones"]))
        self.current_buttons = []

        for i, opt_text in enumerate(options_shuffled):
            try:
                original_index = question["opciones"].index(opt_text)
            except ValueError:
                original_index = -1

            btn_color = kahoot_colors[i % len(kahoot_colors)]
            
            # --- CREACIÓN DE BOTONES CON TAMAÑO FIJO (SIN HOVER BINDING) ---
            btn = Button(options_frame, text=opt_text, font=("Inter", 14, "bold"),
                         bg=btn_color, fg="white", activeforeground="white", 
                         wraplength=self.BUTTON_WRAPLENGTH,
                         width=self.BUTTON_WIDTH_FIXED,
                         height=self.BUTTON_HEIGHT_FIXED,
                         relief="flat", bd=0, 
                         padx=self.BUTTON_PAD_NORMAL, pady=self.BUTTON_PAD_NORMAL,
                         command=lambda idx=original_index, opt=opt_text: self.handle_answer(idx, opt))
            
            btn.grid(row=i // 2, column=i % 2, padx=12, pady=12, sticky="nsew")
            
            self.current_buttons.append(btn)

        for col in range(2):
            options_frame.grid_columnconfigure(col, weight=1)

        # etiqueta de ayuda / progreso
        Label(self.quiz_frame, text=f"Puntaje: {self.quiz.score}/{NUM_QUESTIONS}",
              font=self.font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"],
              fg=COLOR_PALETTE["SECONDARY_TEXT"]).pack(pady=8)

    def darken_color(self, hex_color, factor):
        """Oscurece un color hex por factor (0-1)."""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        dr = max(0, int(r * factor))
        dg = max(0, int(g * factor))
        db = max(0, int(b * factor))
        return f"#{dr:02x}{dg:02x}{db:02x}"

    # ----------------- MANEJO DE RESPUESTA -----------------
    def handle_answer(self, selected_option_index, selected_option_text):
        for b in self.current_buttons:
            b.config(state="disabled")
            b.unbind("<Enter>")
            b.unbind("<Leave>")

        q = self.quiz.get_current_question()
        correct_answer = q.get("respuestaCorrecta", "")
        is_correct = self.quiz.check_answer(selected_option_index)

        for b in self.current_buttons:
            text = b.cget("text")
            
            # Restaurar padding y tamaño a normal (no hay hover que restaurar, pero se mantiene la consistencia)
            b.config(padx=self.BUTTON_PAD_NORMAL, pady=self.BUTTON_PAD_NORMAL,
                     width=self.BUTTON_WIDTH_FIXED, height=self.BUTTON_HEIGHT_FIXED)

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
            
            if self.quiz.next_question():
                self.load_question_ui()
            else:
                self.show_results_ui()
                
        self.master.after(500, next_step)

    # ----------------- RESULTADOS -----------------
    def show_results_ui(self):
        self.clear_all_frames()
        self.results_frame.pack(fill="both", expand=True)

        # Limpiar widgets previos del marco de resultados
        for w in self.results_frame.winfo_children():
            w.destroy()

        score, total = self.quiz.get_results()
        pct = (score / total) * 100 if total > 0 else 0.0

        Label(self.results_frame, text="RESULTADOS", font=self.font_title,
              bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=10)
        Label(self.results_frame, text=f"{score}/{total} correctas - {pct:.1f}%", font=self.font_large,
              bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(pady=8)

        ttk.Button(self.results_frame, text="🔄 Jugar de nuevo (misma categoría)",
                   command=lambda: self.start_quiz_ui(self.quiz.current_category)).pack(pady=10)
        ttk.Button(self.results_frame, text="🏠 Volver al menú", command=self.show_category_selection).pack(pady=6)
        ttk.Button(self.results_frame, text="➕ Agregar Pregunta", command=self.show_add_question_ui).pack(pady=6)

    # ----------------- AGREGAR PREGUNTA (UI) -----------------
    def show_add_question_ui(self):
        self.clear_all_frames()
        self.add_question_frame.pack(fill="both", expand=True)

        header = Frame(self.add_question_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
        header.pack(fill="x", pady=4)
        Button(header, text="← Volver", command=self.show_category_selection,
               relief="flat", bd=0, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=6)
        Label(header, text="➕ Agregar Nueva Pregunta", font=self.font_large,
              bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).pack(side=LEFT, padx=8)

        form = Frame(self.add_question_frame, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
        form.pack(fill="both", expand=True, pady=12, padx=10)

        # Categoría
        Label(form, text="Categoría:", font=self.font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=0, column=0, sticky="w", pady=6)
        self.new_cat_var = StringVar()
        cats = list(ALL_QUESTIONS.keys())
        self.new_cat_var.set(cats[0] if cats else "Seleccionar")
        cat_combo = ttk.Combobox(form, textvariable=self.new_cat_var, values=cats, state="readonly", font=self.font_medium)
        cat_combo.grid(row=0, column=1, sticky="ew", pady=6)

        # Pregunta
        Label(form, text="Pregunta:", font=self.font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=1, column=0, sticky="nw", pady=6)
        self.new_question_text = Text(form, height=5, font=self.font_medium, wrap=WORD)
        self.new_question_text.grid(row=1, column=1, sticky="ew", pady=6)

        # Opciones (4)
        Label(form, text="Opciones (4):", font=self.font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=2, column=0, sticky="nw", pady=6)
        opts_frame = Frame(form, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
        opts_frame.grid(row=2, column=1, sticky="ew", pady=6)
        self.new_option_vars = []
        for i in range(4):
            var = StringVar()
            Label(opts_frame, text=f"Opción {i+1}:", bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=i, column=0, sticky="w", padx=4, pady=4)
            Entry(opts_frame, textvariable=var, font=self.font_medium).grid(row=i, column=1, sticky="ew", padx=4, pady=4)
            opts_frame.grid_columnconfigure(1, weight=1)
            self.new_option_vars.append(var)

        # Respuesta correcta (radio)
        Label(form, text="Respuesta correcta:", font=self.font_medium, bg=COLOR_PALETTE["BACKGROUND_LIGHT"]).grid(row=3, column=0, sticky="w", pady=6)
        self.correct_var = IntVar(value=0)
        correct_frame = Frame(form, bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
        correct_frame.grid(row=3, column=1, sticky="w", pady=6)
        for i in range(4):
            Radiobutton(correct_frame, text=f"Opción {i+1}", variable=self.correct_var, value=i, 
                        bg=COLOR_PALETTE["BACKGROUND_LIGHT"], command=lambda i=i: self.correct_var.set(i)).pack(side=LEFT, padx=6)
            
        # Guardar
        Button(form, text="💾 Guardar pregunta", bg="#4CAF50", fg="white",
               relief="flat", bd=0, padx=14, pady=10,
               command=self.save_new_question).grid(row=4, column=1, sticky="e", pady=12)

        # Ajustes de grid
        form.grid_columnconfigure(1, weight=1)

    def save_new_question(self):
        categoria = self.new_cat_var.get()
        pregunta = self.new_question_text.get("1.0", END).strip()
        if not pregunta:
            messagebox.showerror("Error", "La pregunta no puede estar vacía.")
            return
        opciones = [v.get().strip() for v in self.new_option_vars]
        if any(not o for o in opciones):
            messagebox.showerror("Error", "Completá las 4 opciones.")
            return
        if len(set(opciones)) != 4:
            messagebox.showerror("Error", "Las opciones no pueden repetirse.")
            return
        idx = self.correct_var.get()
        
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
            global ALL_QUESTIONS
            ALL_QUESTIONS = load_questions(FILE_MAP)
            self.quiz.all_data = ALL_QUESTIONS
            messagebox.showinfo("Éxito", f"Pregunta agregada a '{categoria}'.")
            self.new_question_text.delete("1.0", END)
            for v in self.new_option_vars:
                v.set("")
            self.correct_var.set(0)
            self.show_category_selection()
        else:
            messagebox.showerror("Error al guardar", f"No se pudo guardar: {err}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    if not ALL_QUESTIONS:
        ALL_QUESTIONS = load_questions(FILE_MAP)

    root = Tk()
    
    # TÍTULO PERMANENTE EN EL ROOT
    title_label = Label(root, text="🎯 Respondidos", font=("Inter", 28, "bold"),
                        bg=COLOR_PALETTE["BACKGROUND_LIGHT"])
    title_label.pack(pady=8)
    
    app = QuizApp(root, QuizLogic(ALL_QUESTIONS))
    root.mainloop()