import rclpy
from rclpy.node import Node
from putm_vcl_interfaces.msg import FrontboxDriverInput
import pygame
import time
import os
import sys

# === USTAWIENIA GŁOŚNOŚCI I PRZEJŚĆ ===
VOL_START    = 0.2  # Odpalanie
VOL_STOP     = 0.2  # Gaszenie
VOL_IDLE_MAX = 0.4  # Idle (bez gazu)
VOL_WORK_MAX = 1.0  # Praca (max gaz)

CROSSFADE_MS = 2000 # Czas płynnego przejścia (fade-in/fade-out) w milisekundach
# ======================================

class BizonNode(Node):
    def __init__(self):
        super().__init__('bizon_sound_node')

        pygame.mixer.init()
        pygame.mixer.set_num_channels(3)

        self.ch_idle = pygame.mixer.Channel(0)
        self.ch_work = pygame.mixer.Channel(1)
        self.ch_fx = pygame.mixer.Channel(2) 

        self.files = [
            'fmz_bizon_work_start.ogg', 
            'fmz_bizon_idle_loop.ogg', 
            'fmz_bizon_work_loop.ogg', 
            'fmz_bizon_work_stop.ogg'
        ]
        
        for f in self.files:
            if not os.path.exists(f):
                self.get_logger().error(f"Brak pliku: {f}! Odpal węzeł z folderu z plikami ogg.")
                sys.exit(1)

        self.snd_start = pygame.mixer.Sound(self.files[0])
        self.snd_idle = pygame.mixer.Sound(self.files[1])
        self.snd_work = pygame.mixer.Sound(self.files[2])
        self.snd_stop = pygame.mixer.Sound(self.files[3])

        self.snd_start.set_volume(VOL_START)
        self.snd_stop.set_volume(VOL_STOP)

        self.subscription = self.create_subscription(
            FrontboxDriverInput,
            'putm_vcl/frontbox_driver_input',
            self.pedal_callback,
            10
        )

    def play_start_and_loop(self):
        self.get_logger().info("ODPALANIE BIZONA...")
        
        # Odpalamy dźwięk rozruchu
        self.ch_fx.play(self.snd_start)
        
        # Obliczamy ile musimy poczekać przed startem płynnego wejścia idle
        start_length_sec = self.snd_start.get_length()
        fade_sec = CROSSFADE_MS / 1000.0
        
        # Czekamy na moment, w którym trzeba zacząć robić crossfade
        if start_length_sec > fade_sec:
            time.sleep(start_length_sec - fade_sec)
        
        # Ustawiamy bazową głośność
        self.ch_idle.set_volume(VOL_IDLE_MAX)
        self.ch_work.set_volume(0.0)

        # Odpalamy loopy, ale idle wchodzi z płynnym fade-in
        self.ch_idle.play(self.snd_idle, loops=-1, fade_ms=CROSSFADE_MS)
        self.ch_work.play(self.snd_work, loops=-1)
        
        # Czekamy resztę czasu rozruchu, żeby nie blokować ROSa za wcześnie
        time.sleep(fade_sec)
        
        self.get_logger().info("Bizon odpalony. Czeka na gaz.")

    def play_stop(self):
        self.get_logger().info("GASZENIE BIZONA...")
        
        # Płynne wyciszenie trwających pętli (idle i work znikną w X milisekund)
        self.ch_idle.fadeout(CROSSFADE_MS)
        self.ch_work.fadeout(CROSSFADE_MS)
        
        # Odpalenie dźwięku stop (nakłada się na cichnący silnik, co brzmi realistyczniej)
        self.ch_fx.play(self.snd_stop)
        
        # Czekamy na koniec dźwięku stop, inaczej węzeł ubije proces przed wybrzmieniem
        time.sleep(self.snd_stop.get_length())

    def pedal_callback(self, msg):
        pedal_val = msg.pedal_position / 500.0
        throttle = max(0.0, min(1.0, float(pedal_val)))
        
        self.ch_idle.set_volume((1.0 - throttle) * VOL_IDLE_MAX)
        self.ch_work.set_volume(throttle * VOL_WORK_MAX)

def main(args=None):
    rclpy.init(args=args)
    node = BizonNode()
    
    try:
        node.play_start_and_loop()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        node.get_logger().error(f"Błąd: {e}")
    finally:
        node.play_stop()
        node.destroy_node()
        pygame.mixer.quit()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()