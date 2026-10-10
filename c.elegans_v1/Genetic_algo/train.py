import math
import random
import os
import time
from brain_wrapper import WormBrain

# ==========================================
# 1. AYARLAR VE SABİTLER
# ==========================================
GRID_SIZE = 40
POPULATION_SIZE = 100  # 100'e geri döndük, ince ayar yapacağız
GENERATIONS = 1000
MUTATION_RATE = 0.05
MUTATION_POWER = 0.1   # Mutasyonu biraz kıstık (Öğrendiklerini çok çabuk unutmasın diye)

# YENİ: TRANSFER LEARNING (ATA DNA'SI)
# Buraya seçtiğin 34 elma yiyen şampiyonun tam dosya yolunu yaz!
BASE_DNA_FILE = r"evrim_kayitlari_v3\V2_nesil_0844_elma_59_skor_26758_sure_00sa_48dk_19sn.txt"

SAVE_DIR = "evrim_kayitlari_v4" # Duvar eğitimlerini yeni bir klasöre kaydedelim
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

START_TIME = time.time()

def get_elapsed_time():
    elapsed = int(time.time() - START_TIME)
    h = elapsed // 3600
    m = (elapsed % 3600) // 60
    s = elapsed % 60
    return f"{h:02d}sa_{m:02d}dk_{s:02d}sn"

# ==========================================
# 2. BİREY SINIFI
# ==========================================
class WormAgent:
    def __init__(self, dna_weights=None):
        if dna_weights is None:
            self.weights = [random.uniform(-1.0, 1.0) for _ in range(7379)]
        else:
            self.weights = dna_weights
            
        self.fitness = 0.0
        self.apples_eaten = 0 
        self.brain = None 

    def wake_up(self):
        self.brain = WormBrain()
        self.brain.set_weights(self.weights)

    def sleep(self):
        if self.brain:
            self.brain.destroy()
            self.brain = None

# YENİ: DUVAR MESAFESİ HESAPLAMA (BIYIKLAR)
def get_wall_distance(x, y, dx, dy):
    """Verilen yöndeki duvara olan mesafeyi blok cinsinden hesaplar"""
    if dx == 1: return (GRID_SIZE - 1) - x
    if dx == -1: return x
    if dy == 1: return (GRID_SIZE - 1) - y
    if dy == -1: return y
    return 0

# ==========================================
# 3. SİMÜLASYON ARENASI (DUVAR SENSÖRLERİ EKLENDİ)
# ==========================================
def evaluate_agent(agent):
    agent.wake_up()
    
    head_x, head_y = GRID_SIZE // 2, GRID_SIZE // 2
    direction = 0 
    
    fitness = 0.0
    agent.apples_eaten = 0
    apple_x, apple_y = random.randint(2, GRID_SIZE - 3), random.randint(2, GRID_SIZE - 3)
    
    prev_distance = math.dist((head_x, head_y), (apple_x, apple_y))
    time_left = 400 
    
    while time_left > 0:
        time_left -= 1
        
        # --- A. SENSÖRLER ---
        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        lx, ly = dirs[(direction - 1) % 4] 
        rx, ry = dirs[(direction + 1) % 4] 
        dx, dy = apple_x - head_x, apple_y - head_y
        
        # 1. Koku Sensörleri (Eskisi gibi)
        apple_left = max(0.0, (dx * lx + dy * ly))
        apple_right = max(0.0, (dx * rx + dy * ry))
        
        # 2. YENİ: Duvar/Bıyık Sensörleri
        # Eğer duvara 5 bloktan daha yakınsa sensör uyarır (1.0 = Çarpıyorsun!, 0.0 = Güvendesin)
        dist_left = get_wall_distance(head_x, head_y, lx, ly)
        dist_right = get_wall_distance(head_x, head_y, rx, ry)
        
        wall_left = max(0.0, 1.0 - (dist_left / 5.0))
        wall_right = max(0.0, 1.0 - (dist_right / 5.0))
        if wall_left > 0.0 or wall_right > 0.0:
            fitness -= 2.0
        # Dört sensör de devrede! [KokuSol, KokuSağ, DuvarSol, DuvarSağ]
        sensors = [apple_left / 5.0, apple_right / 5.0, wall_left, wall_right]
        
        # --- B. BEYNİ ÇALIŞTIR ---
        outputs = agent.brain.tick(sensors)
        
        # --- C. MOTORLAR ---
        if outputs[2]: direction = (direction - 1) % 4
        elif outputs[3]: direction = (direction + 1) % 4
            
        if outputs[0]: 
            fx, fy = dirs[direction]
            head_x += fx
            head_y += fy
        else:
            fitness -= 0.5 
            
        # --- D. KURALLAR ---
        if head_x < 0 or head_x >= GRID_SIZE or head_y < 0 or head_y >= GRID_SIZE:
            fitness -= 100.0 # Duvara çarpma cezası hâlâ geçerli! Bunu öğrenmeleri gerek.
            break
            
        if head_x == apple_x and head_y == apple_y:
            fitness += 500.0
            agent.apples_eaten += 1
            time_left += 100 
            apple_x, apple_y = random.randint(2, GRID_SIZE - 3), random.randint(2, GRID_SIZE - 3)
                
        current_distance = math.dist((head_x, head_y), (apple_x, apple_y))
        if current_distance < prev_distance: 
            fitness += 1.0   
        elif current_distance > prev_distance: 
            fitness -= 1.5   
            
        prev_distance = current_distance
        
    agent.fitness = fitness
    agent.sleep() 

# ==========================================
# 4. GENETİK ALGORİTMA DÖNGÜSÜ
# ==========================================
def run_evolution():
    print(f"--- 2. ASAMA: DUVAR EGITIMI BASLIYOR | Klasor: {SAVE_DIR} ---")
    
    # 1. ATA DNA'YI YÜKLE
    try:
        with open(BASE_DNA_FILE, 'r') as f:
            base_weights = [float(w) for w in f.read().split(',')]
        print(f"[{BASE_DNA_FILE}] basariyla ata gen olarak yuklendi!")
    except FileNotFoundError:
        print("HATA: Ata DNA dosyasi bulunamadi! Dosya yolunu kontrol et.")
        return

    # 2. POPÜLASYONU ATA'NIN KLONLARINDAN OLUSTUR (Ufak mutasyonlarla)
    population = []
    for _ in range(POPULATION_SIZE):
        child_weights = base_weights.copy()
        for i in range(7379):
            if random.random() < MUTATION_RATE:
                child_weights[i] += random.uniform(-MUTATION_POWER, MUTATION_POWER)
                child_weights[i] = max(-1.0, min(1.0, child_weights[i]))
        population.append(WormAgent(child_weights))

    best_historical_score = 0.0 
    
    for generation in range(1, GENERATIONS + 1):
        
        for agent in population:
            evaluate_agent(agent)
            
        population.sort(key=lambda x: x.fitness, reverse=True)
        best_agent = population[0]
        avg_fitness = sum(agent.fitness for agent in population) / POPULATION_SIZE
        
        print(f"Nesil: {generation:04d} | En Iyi Skor: {best_agent.fitness:7.2f} (Elma: {best_agent.apples_eaten}) | Ortalama Skor: {avg_fitness:7.2f}")
        
        if best_agent.fitness > best_historical_score and best_agent.apples_eaten >= 5:
            best_historical_score = best_agent.fitness
            elapsed_time_str = get_elapsed_time()
            
            filename = os.path.join(SAVE_DIR, f"V2_nesil_{generation:04d}_elma_{best_agent.apples_eaten}_skor_{int(best_historical_score)}_sure_{elapsed_time_str}.txt")
            
            with open(filename, "w") as f:
                f.write(",".join(map(str, best_agent.weights)))
                
            print(f"\n>>> YENI REKOR! Beyin diske yazildi: {filename} <<<\n")
        
        new_population = []
        new_population.append(WormAgent(best_agent.weights.copy()))
        new_population.append(WormAgent(population[1].weights.copy()))
        
        top_performers = population[:20]
        
        while len(new_population) < POPULATION_SIZE:
            parent1 = random.choice(top_performers)
            parent2 = random.choice(top_performers)
            
            child_weights = []
            for i in range(7379):
                weight = parent1.weights[i] if random.random() < 0.5 else parent2.weights[i]
                if random.random() < MUTATION_RATE:
                    weight += random.uniform(-MUTATION_POWER, MUTATION_POWER)
                    weight = max(-1.0, min(1.0, weight))
                child_weights.append(weight)
                
            new_population.append(WormAgent(child_weights))
            
        population = new_population

if __name__ == "__main__":
    run_evolution()