import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
from pathlib import Path


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Respondidos - Quiz de Cultura General")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a2e")
        
        # Variables de estado
        self.categories = {}
        self.current_category = None
        self.current_questions = []
        self.current_question_index = 0
        self.score = 0
        self.selected_answer = tk.StringVar()
        
        # Cargar todas las categorías
        self.load_categories()
        
        # Mostrar pantalla principal
        self.show_main_menu()
    
    def load_categories(self):
        """Carga todas las categorías desde los archivos JSON"""
        data_path = Path("data")
        json_files = ["cine.json", "musica.json", "historia.json", 
                      "deportes.json", "videojuegos.json", "ciencia.json"]
        
        for json_file in json_files:
            file_path = data_path / json_file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    category_key = json_file.replace('.json', '')
                    self.categories[category_key] = data
            except FileNotFoundError:
                messagebox.showerror("Error", f"No se encontró el archivo {json_file}")
            except json.JSONDecodeError:
                messagebox.showerror("Error", f"Error al leer {json_file}")
    
    def clear_window(self):
        """Limpia todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_main_menu(self):
        """Muestra el menú principal con todas las categorías"""
        self.clear_window()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="RESPONDIDOS",
            font=("Arial", 48, "bold"),
            fg="#00d4ff",
            bg="#1a1a2e"
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(
            main_frame,
            text="Selecciona una categoría para comenzar",
            font=("Arial", 16),
            fg="#ffffff",
            bg="#1a1a2e"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Grid de categorías
        categories_frame = tk.Frame(main_frame, bg="#1a1a2e")
        categories_frame.pack(expand=True)
        
        # Colores para cada categoría
        category_colors = {
            'cine': '#ef4444',
            'musica': '#8b5cf6',
            'historia': '#f59e0b',
            'deportes': '#10b981',
            'videojuegos': '#3b82f6',
            'ciencia': '#06b6d4'
        }
        
        row = 0
        col = 0
        for category_key, category_data in self.categories.items():
            color = category_colors.get(category_key, '#6b7280')
            
            # Frame de categoría
            cat_frame = tk.Frame(
                categories_frame,
                bg=color,
                width=250,
                height=150,
                cursor="hand2"
            )
            cat_frame.grid(row=row, column=col, padx=15, pady=15)
            cat_frame.pack_propagate(False)
            
            # Icono
            icon_label = tk.Label(
                cat_frame,
                text=category_data['category']['icon'],
                font=("Arial", 48),
                bg=color,
                fg="#ffffff"
            )
            icon_label.pack(pady=(20, 5))
            
            # Nombre
            name_label = tk.Label(
                cat_frame,
                text=category_data['category']['name'],
                font=("Arial", 18, "bold"),
                bg=color,
                fg="#ffffff"
            )
            name_label.pack()
            
            # Número de preguntas
            count_label = tk.Label(
                cat_frame,
                text=f"{len(category_data['questions'])} preguntas",
                font=("Arial", 12),
                bg=color,
                fg="#ffffff"
            )
            count_label.pack(pady=(5, 0))
            
            # Bind click event
            cat_frame.bind("<Button-1>", lambda e, key=category_key: self.start_quiz(key))
            icon_label.bind("<Button-1>", lambda e, key=category_key: self.start_quiz(key))
            name_label.bind("<Button-1>", lambda e, key=category_key: self.start_quiz(key))
            count_label.bind("<Button-1>", lambda e, key=category_key: self.start_quiz(key))
            
            col += 1
            if col > 2:
                col = 0
                row += 1
    
    def start_quiz(self, category_key):
        """Inicia el quiz de una categoría específica"""
        self.current_category = category_key
        self.current_questions = self.categories[category_key]['questions'].copy()
        random.shuffle(self.current_questions)
        self.current_question_index = 0
        self.score = 0
        self.show_question()
    
    def show_question(self):
        """Muestra la pregunta actual"""
        self.clear_window()
        self.selected_answer.set("")
        
        if self.current_question_index >= len(self.current_questions):
            self.show_results()
            return
        
        question_data = self.current_questions[self.current_question_index]
        category_data = self.categories[self.current_category]['category']
        
        # Colores para cada categoría
        category_colors = {
            'cine': '#ef4444',
            'musica': '#8b5cf6',
            'historia': '#f59e0b',
            'deportes': '#10b981',
            'videojuegos': '#3b82f6',
            'ciencia': '#06b6d4'
        }
        color = category_colors.get(self.current_category, '#6b7280')
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Header con categoría y progreso
        header_frame = tk.Frame(main_frame, bg="#1a1a2e")
        header_frame.pack(fill="x", pady=(0, 30))
        
        category_label = tk.Label(
            header_frame,
            text=f"{category_data['icon']} {category_data['name']}",
            font=("Arial", 24, "bold"),
            fg=color,
            bg="#1a1a2e"
        )
        category_label.pack(side="left")
        
        progress_label = tk.Label(
            header_frame,
            text=f"Pregunta {self.current_question_index + 1}/{len(self.current_questions)}",
            font=("Arial", 16),
            fg="#ffffff",
            bg="#1a1a2e"
        )
        progress_label.pack(side="right")
        
        # Pregunta
        question_frame = tk.Frame(main_frame, bg="#2d2d44", relief="solid", borderwidth=2)
        question_frame.pack(fill="x", pady=(0, 30), padx=20)
        
        question_label = tk.Label(
            question_frame,
            text=question_data['question'],
            font=("Arial", 20, "bold"),
            fg="#ffffff",
            bg="#2d2d44",
            wraplength=750,
            justify="center"
        )
        question_label.pack(pady=30, padx=30)
        
        # Opciones
        options_frame = tk.Frame(main_frame, bg="#1a1a2e")
        options_frame.pack(fill="both", expand=True)
        
        for i, option in enumerate(question_data['options']):
            option_button = tk.Radiobutton(
                options_frame,
                text=option,
                variable=self.selected_answer,
                value=option,
                font=("Arial", 16),
                fg="#ffffff",
                bg="#2d2d44",
                selectcolor="#1a1a2e",
                activebackground="#3d3d54",
                activeforeground="#ffffff",
                indicatoron=False,
                width=60,
                height=2,
                cursor="hand2",
                relief="solid",
                borderwidth=2
            )
            option_button.pack(pady=10, padx=40)
        
        # Botones de navegación
        nav_frame = tk.Frame(main_frame, bg="#1a1a2e")
        nav_frame.pack(fill="x", pady=(30, 0))
        
        back_button = tk.Button(
            nav_frame,
            text="← Volver al Menú",
            font=("Arial", 14),
            bg="#6b7280",
            fg="#ffffff",
            cursor="hand2",
            relief="flat",
            padx=20,
            pady=10,
            command=self.show_main_menu
        )
        back_button.pack(side="left")
        
        next_button = tk.Button(
            nav_frame,
            text="Siguiente →",
            font=("Arial", 14, "bold"),
            bg=color,
            fg="#ffffff",
            cursor="hand2",
            relief="flat",
            padx=30,
            pady=10,
            command=self.check_answer
        )
        next_button.pack(side="right")
    
    def check_answer(self):
        """Verifica la respuesta seleccionada"""
        if not self.selected_answer.get():
            messagebox.showwarning("Atención", "Por favor selecciona una respuesta")
            return
        
        question_data = self.current_questions[self.current_question_index]
        
        if self.selected_answer.get() == question_data['correct']:
            self.score += 1
            messagebox.showinfo("¡Correcto!", "¡Respuesta correcta! 🎉")
        else:
            messagebox.showinfo(
                "Incorrecto",
                f"Respuesta incorrecta.\nLa respuesta correcta era: {question_data['correct']}"
            )
        
        self.current_question_index += 1
        self.show_question()
    
    def show_results(self):
        """Muestra los resultados finales"""
        self.clear_window()
        
        category_data = self.categories[self.current_category]['category']
        total_questions = len(self.current_questions)
        percentage = (self.score / total_questions) * 100
        
        # Colores para cada categoría
        category_colors = {
            'cine': '#ef4444',
            'musica': '#8b5cf6',
            'historia': '#f59e0b',
            'deportes': '#10b981',
            'videojuegos': '#3b82f6',
            'ciencia': '#06b6d4'
        }
        color = category_colors.get(self.current_category, '#6b7280')
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="¡Quiz Completado!",
            font=("Arial", 42, "bold"),
            fg="#00d4ff",
            bg="#1a1a2e"
        )
        title_label.pack(pady=(40, 20))
        
        # Categoría
        category_label = tk.Label(
            main_frame,
            text=f"{category_data['icon']} {category_data['name']}",
            font=("Arial", 24),
            fg=color,
            bg="#1a1a2e"
        )
        category_label.pack(pady=(0, 40))
        
        # Resultados
        results_frame = tk.Frame(main_frame, bg="#2d2d44", relief="solid", borderwidth=3)
        results_frame.pack(pady=20, padx=100)
        
        score_label = tk.Label(
            results_frame,
            text=f"{self.score} / {total_questions}",
            font=("Arial", 72, "bold"),
            fg=color,
            bg="#2d2d44"
        )
        score_label.pack(pady=(40, 10))
        
        percentage_label = tk.Label(
            results_frame,
            text=f"{percentage:.1f}% de aciertos",
            font=("Arial", 24),
            fg="#ffffff",
            bg="#2d2d44"
        )
        percentage_label.pack(pady=(0, 40))
        
        # Mensaje según el porcentaje
        if percentage >= 90:
            message = "¡Excelente! Eres un experto 🏆"
        elif percentage >= 70:
            message = "¡Muy bien! Buen trabajo 👏"
        elif percentage >= 50:
            message = "¡No está mal! Sigue practicando 💪"
        else:
            message = "Necesitas estudiar más 📚"
        
        message_label = tk.Label(
            main_frame,
            text=message,
            font=("Arial", 20),
            fg="#ffffff",
            bg="#1a1a2e"
        )
        message_label.pack(pady=(30, 50))
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg="#1a1a2e")
        buttons_frame.pack()
        
        retry_button = tk.Button(
            buttons_frame,
            text="🔄 Reintentar",
            font=("Arial", 16, "bold"),
            bg=color,
            fg="#ffffff",
            cursor="hand2",
            relief="flat",
            padx=30,
            pady=15,
            command=lambda: self.start_quiz(self.current_category)
        )
        retry_button.pack(side="left", padx=10)
        
        menu_button = tk.Button(
            buttons_frame,
            text="🏠 Volver al Menú",
            font=("Arial", 16, "bold"),
            bg="#6b7280",
            fg="#ffffff",
            cursor="hand2",
            relief="flat",
            padx=30,
            pady=15,
            command=self.show_main_menu
        )
        menu_button.pack(side="left", padx=10)


def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
