import tkinter as tk
from tkinter import ttk, messagebox
from .components import FrequencyControl, TimerControl
from core.domain import WaveType

class MainApplication(tk.Tk):
    def __init__(self, freq_manager, timer_manager):
        super().__init__()
        self.title("Generador de Frecuencias sound hz emiter")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")
        
        self.freq_manager = freq_manager
        self.timer_manager = timer_manager
        
        # Definir max_frequencies ANTES de create_widgets
        self.max_frequencies = 16
        
        self.create_widgets()
        self.update_ui()
        self.update_timer_display()
    
    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame desplazable
        canvas = tk.Canvas(main_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón para agregar frecuencias
        self.add_frequency_btn = tk.Button(
            self.scrollable_frame, 
            text="+ Agregar Frecuencia", 
            command=self.add_frequency,
            pady=10,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.add_frequency_btn.pack(fill=tk.X, padx=10, pady=10)
        
        # Contador de frecuencias
        self.freq_counter = tk.Label(
            self.scrollable_frame, 
            text=f"Frecuencias: 0/{self.max_frequencies}",
            bg="#f0f0f0",
            font=("Arial", 9)
        )
        self.freq_counter.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Temporizador
        timer_frame = tk.LabelFrame(
            self, 
            text="Control de Tiempo",
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        timer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.timer_control = TimerControl(
            timer_frame,
            on_start=self.start_timer,
            on_stop=self.stop_timer
        )
        self.timer_control.pack(fill=tk.X, padx=5, pady=5)
        
        # Agregar frecuencia inicial
        self.freq_controls = []
        self.add_frequency()
    
    def add_frequency(self):
        if len(self.freq_controls) >= self.max_frequencies:
            messagebox.showwarning(
                "Límite alcanzado", 
                f"No se pueden agregar más de {self.max_frequencies} frecuencias"
            )
            return
            
        config = self.freq_manager.add_frequency(WaveType.SILENCE, 0.0)
        control = FrequencyControl(
            self.scrollable_frame,
            config,
            on_play=lambda: self.play_frequency(config.id),
            on_pause=lambda: self.pause_frequency(config.id),
            on_stop=lambda: self.stop_frequency(config.id),
            on_change=self.update_frequency
        )
        control.pack(fill=tk.X, padx=10, pady=5, before=self.add_frequency_btn)
        self.freq_controls.append(control)
        self.update_freq_counter()
    
    def update_freq_counter(self):
        count = len(self.freq_controls)
        self.freq_counter.config(text=f"Frecuencias: {count}/{self.max_frequencies}")
    
    def play_frequency(self, freq_id):
        self.freq_manager.toggle_play(freq_id)
        self.update_ui()
    
    def pause_frequency(self, freq_id):
        self.freq_manager.toggle_play(freq_id)
        self.update_ui()
    
    def stop_frequency(self, freq_id):
        self.freq_manager.stop_frequency(freq_id)
        self.update_ui()
    
    def update_frequency(self, freq_id, wave_type, frequency):
        configs = self.freq_manager.get_all_frequencies()
        for config in configs:
            if config.id == freq_id:
                config.wave_type = wave_type
                config.frequency = frequency
                self.freq_manager.update_frequency(config)
                break
        self.update_ui()
    
    def start_timer(self):
        hours, minutes, seconds = self.timer_control.get_time()
        if hours == 0 and minutes == 0 and seconds == 0:
            messagebox.showwarning("Tiempo inválido", "Por favor establece un tiempo mayor a 0")
            return
            
        self.timer_manager.start_timer(hours, minutes, seconds)
    
    def stop_timer(self):
        self.timer_manager.stop_timer()
        self.update_timer_display()
    
    def update_ui(self):
        configs = self.freq_manager.get_all_frequencies()
        for control in self.freq_controls:
            for config in configs:
                if config.id == control.config.id:
                    control.update_config(config)
                    break
    
    def update_timer_display(self):
        time_str = self.timer_manager.get_remaining_time()
        self.timer_control.update_time(time_str)
        self.after(1000, self.update_timer_display)