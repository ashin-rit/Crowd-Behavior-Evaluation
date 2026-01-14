"""
Audio Alert Generator
Generates audio alerts using pygame (for GUI integration)
"""

try:
    import pygame
    import numpy as np
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️  Pygame not available - audio alerts will be simulated")


class AudioAlertGenerator:
    """
    Generates and plays audio alerts
    """
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize audio generator
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.initialized = False
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
                self.initialized = True
                print("✓ Audio system initialized")
            except:
                print("⚠️  Could not initialize audio system")
                self.initialized = False
    
    def generate_beep(self, frequency: float, duration: float) -> Optional[np.ndarray]:
        """
        Generate a beep sound
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            
        Returns:
            Audio samples as numpy array
        """
        if not PYGAME_AVAILABLE:
            return None
        
        # Generate time array
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Generate sine wave
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Apply envelope (fade in/out to avoid clicks)
        envelope_length = int(0.01 * self.sample_rate)  # 10ms
        envelope = np.ones_like(wave)
        envelope[:envelope_length] = np.linspace(0, 1, envelope_length)
        envelope[-envelope_length:] = np.linspace(1, 0, envelope_length)
        
        wave = wave * envelope
        
        # Convert to 16-bit
        wave = (wave * 32767).astype(np.int16)
        
        return wave
    
    def play_alert_pattern(self, pattern: List[Tuple[str, float]], frequency: float):
        """
        Play an alert pattern
        
        Args:
            pattern: List of (action, duration) tuples
            frequency: Beep frequency in Hz
        """
        if not self.initialized:
            print(f"  [SIMULATED AUDIO] Pattern: {pattern} at {frequency}Hz")
            return
        
        for action, duration in pattern:
            if action == 'beep':
                wave = self.generate_beep(frequency, duration)
                if wave is not None:
                    # Create stereo sound
                    stereo_wave = np.column_stack((wave, wave))
                    sound = pygame.sndarray.make_sound(stereo_wave)
                    sound.play()
                    pygame.time.wait(int(duration * 1000))
            elif action == 'pause':
                pygame.time.wait(int(duration * 1000))
    
    def play_warning_alert(self):
        """Play warning level alert"""
        pattern = [('beep', 0.3)]
        self.play_alert_pattern(pattern, 800)
    
    def play_critical_alert(self):
        """Play critical level alert"""
        pattern = [('beep', 0.5), ('pause', 0.2), ('beep', 0.5)]
        self.play_alert_pattern(pattern, 1000)
    
    def play_emergency_alert(self):
        """Play emergency level alert"""
        pattern = [
            ('beep', 0.7), 
            ('pause', 0.2), 
            ('beep', 0.7), 
            ('pause', 0.2), 
            ('beep', 0.7)
        ]
        self.play_alert_pattern(pattern, 1200)
    
    def cleanup(self):
        """Cleanup audio resources"""
        if self.initialized:
            pygame.mixer.quit()


# Testing function
def test_audio_generator():
    """Test audio alert generation"""
    print("=" * 80)
    print("AUDIO ALERT GENERATOR TEST")
    print("=" * 80)
    
    generator = AudioAlertGenerator()
    
    if not generator.initialized:
        print("\n⚠️  Audio not available - showing simulated output only")
    
    print("\n--- Testing Warning Alert ---")
    generator.play_warning_alert()
    
    print("\n--- Testing Critical Alert ---")
    generator.play_critical_alert()
    
    print("\n--- Testing Emergency Alert ---")
    generator.play_emergency_alert()
    
    print("\n✓ Audio test complete")
    
    generator.cleanup()


if __name__ == '__main__':
    test_audio_generator()