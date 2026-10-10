import pygame
import math
import random
from brain_wrapper import WormBrain

# ==========================================
# AYARLAR (Eğitim ortamıyla birebir aynı)
# ==========================================
GRID_SIZE = 40
CELL_SIZE = 15
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
HIZ_CARPANI = 1   
def get_wall_distance(x, y, dx, dy):
   
    if dx == 1: return (GRID_SIZE - 1) - x
    if dx == -1: return x
    if dy == 1: return (GRID_SIZE - 1) - y
    if dy == -1: return y
    return 0

def play_champion(filename):
    print(f"[{filename}] beyni (SNN) RAM'e yukleniyor...")
    
    # 1. Ağırlıkları (Genleri) Yükle
    try:
        with open(filename, 'r') as f:
            weights = [float(w) for w in f.read().split(',')]
    except FileNotFoundError:
        print("HATA: Dosya bulunamadi! Dosya yolunu kontrol et.")
        return

    # 2. Arayüz Hazırlığı
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Evrim Arenasi - 4 Sensörlü Şampiyon Yayını")
    clock = pygame.time.Clock()

    # 3. C++ Beynini Başlat
    brain = WormBrain()
    brain.set_weights(weights)

    # Başlangıç Değerleri
    head_x, head_y = GRID_SIZE // 2, GRID_SIZE // 2
    apple_x, apple_y = random.randint(2, GRID_SIZE - 3), random.randint(2, GRID_SIZE - 3)
    direction = 0 # 0:Yukarı, 1:Sağ, 2:Aşağı, 3:Sol
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- FİZİK VE DÜŞÜNME DÖNGÜSÜ (Hızlandırılmış) ---
        for _ in range(HIZ_CARPANI):
            # A. Yön Vektörleri
            dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            lx, ly = dirs[(direction - 1) % 4] # Sol Vektör
            rx, ry = dirs[(direction + 1) % 4] # Sağ Vektör
            dx, dy = apple_x - head_x, apple_y - head_y

            # B. Koku Sensörleri (Nokta Çarpım)
            apple_left = max(0.0, (dx * lx + dy * ly))
            apple_right = max(0.0, (dx * rx + dy * ry))

            # C. Duvar/Bıyık Sensörleri (Lidar Mantığı)
            dist_left = get_wall_distance(head_x, head_y, lx, ly)
            dist_right = get_wall_distance(head_x, head_y, rx, ry)
            
            # Duvara 5 bloktan yakınsa voltaj (uyarı) artar
            wall_left = max(0.0, 1.0 - (dist_left / 5.0))
            wall_right = max(0.0, 1.0 - (dist_right / 5.0))

            # D. GİRİŞ PİNLERİ: [Sol Koku, Sağ Koku, Sol Duvar, Sağ Duvar]
            sensors = [apple_left / 5.0, apple_right / 5.0, wall_left, wall_right]

            # E. İŞLEMCİ: Beyne veriyi gönder, motor komutlarını al
            outputs = brain.tick(sensors)

            # F. ÇIKIŞ PİNLERİ: Yön Güncelleme
            if outputs[2]: direction = (direction - 1) % 4   # RIML (Sol Motor)
            elif outputs[3]: direction = (direction + 1) % 4 # RIMR (Sağ Motor)

            # İleri Gitme Komutu (AVB)
            if outputs[0]:
                head_x += dirs[direction][0]
                head_y += dirs[direction][1]

            # --- OYUN KURALLARI ---
            if head_x < 0 or head_x >= GRID_SIZE or head_y < 0 or head_y >= GRID_SIZE:
                print(f"DUVARA CARPTI! Toplam Elma: {score}")
                running = False
                break

            if head_x == apple_x and head_y == apple_y:
                score += 1
                print(f"ELMA YEDI! Skor: {score}")
                apple_x, apple_y = random.randint(2, GRID_SIZE - 3), random.randint(2, GRID_SIZE - 3)
                break # Görselin tazelenmesi için döngüden çık

        # ==========================================
        # EKRAN ÇİZİM KISMI
        # ==========================================
        screen.fill((30, 30, 30))

        # Elmayı çiz (Kırmızı)
        pygame.draw.rect(screen, (255, 50, 50), (apple_x*CELL_SIZE, apple_y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Yılanı çiz (Yeşil)
        pygame.draw.rect(screen, (50, 255, 50), (head_x*CELL_SIZE, head_y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # Yılanın yönünü belli eden göz
        eye_x = head_x*CELL_SIZE + CELL_SIZE//2 + dirs[direction][0]*CELL_SIZE//2
        eye_y = head_y*CELL_SIZE + CELL_SIZE//2 + dirs[direction][1]*CELL_SIZE//2
        pygame.draw.circle(screen, (0, 0, 0), (eye_x, eye_y), 3)

        pygame.display.flip()
        clock.tick(60) 

    brain.destroy()
    pygame.quit()

if __name__ == "__main__":
    # BURAYA 84 ELMALIK ŞAMPİYONUNUN TAM YOLUNU YAZ:
    dosya_yolu = r"evrim_kayitlari_v4\V2_nesil_0932_elma_84_skor_38847_sure_00sa_58dk_10sn.txt"
    play_champion(dosya_yolu)