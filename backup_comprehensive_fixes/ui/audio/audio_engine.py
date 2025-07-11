"""
Motor de audio refactorizado - Responsabilidad única de gestión de audio
"""

from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal
from .audio_thread import AudioThread
from ..utils.constants import AudioConstants

class AudioEngine(QObject):
    """
    Motor de audio con responsabilidad única
    Separado de la lógica de UI
    """
    
    # Señales para comunicación con UI
    audio_started = Signal()
    audio_stopped = Signal()
    tone_added = Signal(int)  # tone_id
    tone_removed = Signal(int)  # tone_id
    
    def __init__(self):
        super().__init__()
        self.audio_thread = AudioThread()
        self.is_running = False
        self._active_tones: Dict[int, dict] = {}
    
    def start_audio(self) -> bool:
        """Inicia el sistema de audio"""
        if self.is_running:
            return True
        
        try:
            success = self.audio_thread.start_audio()
            if success:
                self.is_running = True
                self.audio_started.emit()
                return True
            return False
        except Exception as e:
            print(f"Error iniciando audio: {e}")
            return False
    
    def stop_audio(self) -> None:
        """Detiene el sistema de audio"""
        if not self.is_running:
            return
        
        self.audio_thread.stop_audio()
        self.is_running = False
        self.audio_stopped.emit()
    
    def add_tone(self, tone_id: int, frequency: float, volume: float, 
                 wave_type: str = "seno", panning: float = 0.0) -> bool:
        """Agrega un tono al sistema"""
        if tone_id in self._active_tones:
            return self.update_tone(tone_id, frequency, volume, wave_type, panning)
        
        if len(self._active_tones) >= AudioConstants.MAX_CONCURRENT_TONES:
            print(f"Máximo de {AudioConstants.MAX_CONCURRENT_TONES} tonos simultáneos")
            return False
        
        tone_config = {
            'frequency': frequency,
            'volume': volume,
            'wave_type': wave_type,
            'panning': panning,
            'active': True
        }
        
        self._active_tones[tone_id] = tone_config
        self.audio_thread.add_tone(tone_id, frequency, volume, wave_type, True, panning)
        self.tone_added.emit(tone_id)
        return True
    
    def remove_tone(self, tone_id: int) -> bool:
        """Elimina un tono del sistema"""
        if tone_id not in self._active_tones:
            return False
        
        del self._active_tones[tone_id]
        self.audio_thread.remove_tone(tone_id)
        self.tone_removed.emit(tone_id)
        return True
    
    def update_tone(self, tone_id: int, frequency: float, volume: float,
                   wave_type: str, panning: float) -> bool:
        """Actualiza un tono existente"""
        if tone_id not in self._active_tones:
            return False
        
        self._active_tones[tone_id].update({
            'frequency': frequency,
            'volume': volume,
            'wave_type': wave_type,
            'panning': panning
        })
        
        self.audio_thread.add_tone(tone_id, frequency, volume, wave_type, True, panning)
        return True
    
    def set_tone_active(self, tone_id: int, active: bool) -> bool:
        """Activa/desactiva un tono"""
        if tone_id not in self._active_tones:
            return False
        
        self._active_tones[tone_id]['active'] = active
        self.audio_thread.set_tone_active(tone_id, active)
        return True
    
    def get_active_tone_count(self) -> int:
        """Retorna el número de tonos activos"""
        return sum(1 for tone in self._active_tones.values() if tone['active'])
    
    def get_total_tone_count(self) -> int:
        """Retorna el número total de tonos"""
        return len(self._active_tones)
    
    def clear_all_tones(self) -> None:
        """Elimina todos los tonos"""
        tone_ids = list(self._active_tones.keys())
        for tone_id in tone_ids:
            self.remove_tone(tone_id)