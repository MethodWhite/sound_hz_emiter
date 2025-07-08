import tkinter as tk
from tkinter import ttk
from core.domain import WaveType

class FrequencyControl(tk.Frame):
    def __init__(self, master, config, on_play, on_pause, on_stop, on_change):
        super().__init__(master, bd=1, relief=tk.RAISED, padx=5, pady=5)
        self.config = config
        self.on_play = on_play
        self.on_pause = on_pause
        self.on_stop = on_stop
        self.on_change = on_change
        
        tk.Label(self, text=f"Frecuencia {config.id}").grid(row=0, column=0, padx=5)
        
        self.wave_var = tk.StringVar(value=config.wave_type.value)
        wave_combo = ttk.Combobox(
            self, 
            textvariable=self.wave_var,
            values=[wt.value for wt in WaveType],
            state="readonly",
            width=15
        )
        wave_combo.grid(row=0, column=1, padx=5)
        wave_combo.bind("<<ComboboxSelected>>", self._on_wave_change)
        
        self.freq_var = tk.DoubleVar(value=config.frequency)
        freq_entry = tk.Entry(self, textvariable=self.freq_var, width=8)
        freq_entry.grid(row=0, column=2, padx=5)
        self.freq_var.trace_add("write", self._on_freq_change)
        
        self.play_btn = tk.Button(self, text="Reproducir", command=on_play, width=8)
        self.play_btn.grid(row=0, column=3, padx=2)
        
        self.pause_btn = tk.Button(self, text="Pausar", command=on_pause, width=8)
        self.pause_btn.grid(row=0, column=4, padx=2)
        
        stop_btn = tk.Button(self, text="Parar", command=on_stop, width=8)
        stop_btn.grid(row=0, column=5, padx=2)
        
        self._update_ui()
    
    def _on_wave_change(self, event):
        new_type = next(wt for wt in WaveType if wt.value == self.wave_var.get())
        self.on_change(self.config.id, new_type, self.freq_var.get())
    
    def _on_freq_change(self, *args):
        try:
            freq = float(self.freq_var.get())
            if freq < 0:
                freq = 0
                self.freq_var.set(0)
            self.on_change(self.config.id, self.config.wave_type, freq)
        except ValueError:
            pass
    
    def update_config(self, new_config):
        self.config = new_config
        self._update_ui()
    
    def _update_ui(self):
        self.wave_var.set(self.config.wave_type.value)
        self.freq_var.set(self.config.frequency)
        
        if self.config.is_playing:
            self.play_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
        elif self.config.is_paused:
            self.play_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
        else:
            self.play_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.NORMAL)

class TimerControl(tk.Frame):
    def __init__(self, master, on_start, on_stop):
        super().__init__(master, bd=1, relief=tk.RAISED, padx=5, pady=5)
        
        tk.Label(self, text="Temporizador:").grid(row=0, column=0, padx=5)
        
        self.hours_var = tk.IntVar(value=0)
        tk.Spinbox(self, from_=0, to=99, width=3, textvariable=self.hours_var).grid(row=0, column=1, padx=2)
        tk.Label(self, text="h").grid(row=0, column=2)
        
        self.minutes_var = tk.IntVar(value=0)
        tk.Spinbox(self, from_=0, to=59, width=3, textvariable=self.minutes_var).grid(row=0, column=3, padx=2)
        tk.Label(self, text="m").grid(row=0, column=4)
        
        self.seconds_var = tk.IntVar(value=10)
        tk.Spinbox(self, from_=0, to=59, width=3, textvariable=self.seconds_var).grid(row=0, column=5, padx=2)
        tk.Label(self, text="s").grid(row=0, column=6)
        
        start_btn = tk.Button(self, text="Iniciar", command=on_start)
        start_btn.grid(row=0, column=7, padx=5)
        
        stop_btn = tk.Button(self, text="Detener", command=on_stop)
        stop_btn.grid(row=0, column=8, padx=5)
        
        self.time_label = tk.Label(self, text="00:00:00", font=("Arial", 12, "bold"))
        self.time_label.grid(row=0, column=9, padx=10)
    
    def get_time(self):
        return (
            self.hours_var.get(),
            self.minutes_var.get(),
            self.seconds_var.get()
        )
    
    def update_time(self, time_str):
        self.time_label.config(text=time_str)