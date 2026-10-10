import ctypes
import os
import random

# 1. DLL DOSYASINI BUL VE YÜKLE
dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worm_brain.dll")
try:
    lib = ctypes.CDLL(dll_path)
except OSError as e:
    print(f"WINDOWS'UN ASIL HATASI: {e}")
    exit(1)

# 2. C++ FONKSİYONLARININ GİRDİ/ÇIKTI TİPLERİNİ TANIMLA
lib.Brain_new.restype = ctypes.c_void_p

lib.Brain_set_weights.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float)]

lib.Brain_tick.argtypes = [
    ctypes.c_void_p,                  # Brain pointer
    ctypes.POINTER(ctypes.c_float),   # Sensor input array
    ctypes.c_uint8,                   # Input count
    ctypes.POINTER(ctypes.c_bool),    # Command output array
    ctypes.c_uint8                    # Output count
]

lib.Brain_delete.argtypes = [ctypes.c_void_p]

# 3. PYTHON İÇİN NESNE YÖNELİMLİ (OOP) BEYİN SINIFI
class WormBrain:
    def __init__(self):
        # C++ tarafında beyni yarat ve bellekteki adresini (pointer) al
        self.obj = lib.Brain_new()
        self.num_weights = 7379 # Duzelttigimiz dogru kablo sayisi!
        
    def set_weights(self, weights_list):
        # Python listesini C++'in anlayacagi float dizisine cevir
        if len(weights_list) != self.num_weights:
            raise ValueError(f"HATA: Agirlik listesi tam olarak {self.num_weights} adet olmali!")
            
        weights_array = (ctypes.c_float * self.num_weights)(*weights_list)
        lib.Brain_set_weights(self.obj, weights_array)
        
    def tick(self, sensors):
        # sensors: [ASIL, ASIR, ASHL, ASHR]
        # returns: [AVB, AVA, RIML, RIMR]
        
        sensor_array = (ctypes.c_float * 4)(*sensors)
        command_array = (ctypes.c_bool * 4)() # Cikis icin bos dizi
        
        lib.Brain_tick(self.obj, sensor_array, 4, command_array, 4)
        
        return list(command_array)
        
    def destroy(self):
        # Bellek sizintisi (Memory Leak) yapmamak icin isimiz bitince RAM'den siliyoruz
        lib.Brain_delete(self.obj)

# ==========================================
# BAĞLANTI TESTİ (Doğrudan bu dosyayı çalıştırırsan çalışır)
# ==========================================
if __name__ == "__main__":
    print("--- C++ BEYNI PYTHON'A YUKLENIYOR ---")
    brain = WormBrain()
    
    # Motorlarin kesin ateslemesi icin sadece pozitif ve guclu agirliklar veriyoruz (0.0 ile 1.0 arasi)
    dummy_weights = [random.uniform(0.0, 1.0) for _ in range(7379)]
    brain.set_weights(dummy_weights)
    print("7379 adet gen (agirlik) C++ anakartina basariyla aktarildi.\n")
    
    test_sensors = [2.0, 0.0, 0.0, 0.0] # ASIL (Sol koku) sensorune surekli 2.0V veriyoruz
    
    print("[ BEYIN SIMULASYONU BASLIYOR ]")
    print("Sinyalin beyinde ilerlemesi bekleniyor...\n")
    
    # Beyni 50 tick (50 milisaniye) boyunca calistir
    for tick in range(1, 51):
        motor_outputs = brain.tick(test_sensors)
        
        # any() fonksiyonu dizideki degerlerden en az biri True ise calisir
        if any(motor_outputs):
            print(f">>> BINGO! Tick {tick} : Motorlar Atesledi! -> {motor_outputs} <<<")
             # Ateslemeyi gordugumuz an donguyu durdur
    else:
        print("50 Tick boyunca hicbir motor esigi gecemedi (Agirliklar zayif kaldi).")
        
    brain.destroy()
    print("\nTest basarili, beyin bellekten guvenle silindi.")