import pygame
import random
import sys

# --- AYARLAR ---
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # Klasik yılan hızı (Saniyede 10 kare kare hareket)

# Renkler
BG_COLOR = (20, 20, 20)
GRID_COLOR = (40, 40, 40)
WORM_HEAD_COLOR = (100, 250, 100)
WORM_BODY_COLOR = (50, 150, 50)
FOOD_COLOR = (250, 50, 50)
TEXT_COLOR = (200, 200, 200)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("C. elegans - Klasik Snake Arenasi")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 16)

class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        # Yılanın başlangıç pozisyonu (Ekranın ortasında 3 birimlik bir yılan)
        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.body = [(cx, cy), (cx, cy+1), (cx, cy+2)] 
        self.direction = (0, -1) # Başlangıçta yukarı bakıyor
        self.score = 0
        self.spawn_food()
        self.game_over = False

    def spawn_food(self):
        while True:
            fx = random.randint(0, GRID_WIDTH - 1)
            fy = random.randint(0, GRID_HEIGHT - 1)
            if (fx, fy) not in self.body:
                self.food = (fx, fy)
                break

    def step(self, avb_up, ava_down, riml_left, rimr_right):
        if self.game_over:
            return

        # Yön Güncellemesi (Zıt yöne dönmesini engelle)
        if avb_up and self.direction != (0, 1):
            self.direction = (0, -1)
        elif ava_down and self.direction != (0, -1):
            self.direction = (0, 1)
        elif riml_left and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif rimr_right and self.direction != (-1, 0):
            self.direction = (1, 0)

        # Yeni baş pozisyonunu hesapla
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Çarpışma Kontrolü (Duvarlar veya Kendi Gövdesi)
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or 
            new_head in self.body):
            self.game_over = True
            return

        # Yılanı hareket ettir
        self.body.insert(0, new_head)

        # Elma yeme kontrolü
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
        else:
            self.body.pop() # Elma yemezse kuyruğu sil (boyut sabit kalsın)

    def get_sensor_data(self):
        head_x, head_y = self.body[0]
        food_x, food_y = self.food

        # 1. ELMA SENSÖRLERİ (ASIL, ASIR)
        dx = food_x - head_x
        dy = food_y - head_y

        asil_volt = 0.0
        asir_volt = 0.0

        if dx < 0: # Elma Solda
            asil_volt = 2.0
        elif dx > 0: # Elma Sağda
            asir_volt = 2.0
            
        if dx == 0 and dy != 0: # Elma tam hizada
            asil_volt = 1.0
            asir_volt = 1.0

        # 2. DUVAR (TEHLİKE) SENSÖRLERİ (ASHL, ASHR)
        # Yılanın baktığı yöne göre sağına ve soluna 1 birimlik sanal bir "bıyık" (whisker) atıyoruz.
        ashl_volt = 0.0
        ashr_volt = 0.0
        
        # Yılanın mevcut yönüne (dx, dy) göre sol ve sağ karelerin koordinatları
        dir_x, dir_y = self.direction
        left_square = (head_x + dir_y, head_y - dir_x)
        right_square = (head_x - dir_y, head_y + dir_x)
        
        # Sol tarafta duvar veya kendi kuyruğu varsa ASHL (Sol Acı) tetiklensin
        if (left_square[0] < 0 or left_square[0] >= GRID_WIDTH or 
            left_square[1] < 0 or left_square[1] >= GRID_HEIGHT or 
            left_square in self.body):
            ashl_volt = 2.0
            
        # Sağ tarafta duvar veya kendi kuyruğu varsa ASHR (Sağ Acı) tetiklensin
        if (right_square[0] < 0 or right_square[0] >= GRID_WIDTH or 
            right_square[1] < 0 or right_square[1] >= GRID_HEIGHT or 
            right_square in self.body):
            ashr_volt = 2.0

        return asil_volt, asir_volt, ashl_volt, ashr_volt

    def draw(self, surface):
        surface.fill(BG_COLOR)
        
        # Izgarayı (Grid) çiz (İsteğe bağlı, retro bir hava katar)
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))

        # Elmayı çiz
        fx, fy = self.food
        pygame.draw.rect(surface, FOOD_COLOR, (fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Yılanı çiz
        for i, (bx, by) in enumerate(self.body):
            color = WORM_HEAD_COLOR if i == 0 else WORM_BODY_COLOR
            pygame.draw.rect(surface, color, (bx * CELL_SIZE, by * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Oyunu başlat
game = SnakeGame()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game.game_over:
            if event.key == pygame.K_SPACE:
                game.reset() # Yanarsa BOŞLUK tuşuyla yeniden başlat

    # BEYİN YERİNE KLAVYE (Ok Tuşları)
    keys = pygame.key.get_pressed()
    avb = keys[pygame.K_UP]
    ava = keys[pygame.K_DOWN]
    riml = keys[pygame.K_LEFT]
    rimr = keys[pygame.K_RIGHT]

    # Koku sensörlerini oku
    asil, asir,ashl,ashr = game.get_sensor_data()

    # Yılanı 1 kare ilerlet
    game.step(avb, ava, riml, rimr)

    # Çizim
    game.draw(screen)

    # Arayüz
    ui_texts = [
        f"SKOR: {game.score}",
        f"--- SENSORLER (Giris) ---",
        f"ASIL (Sol Burun) : {asil:.1f} V",
        f"ASIR (Sag Burun) : {asir:.1f} V",
        f"ASHL (Sol Burun) : {ashl:.1f} V",
        f"ASHR (Sag Burun) : {ashr:.1f} V",
        f"--- MOTORLAR (Cikis) ---",
        f"AVB (Yukari) : {'KASILDI' if avb else '-'}",
        f"AVA (Asagi)  : {'KASILDI' if ava else '-'}",
        f"RIML (Sola)  : {'KASILDI' if riml else '-'}",
        f"RIMR (Saga)  : {'KASILDI' if rimr else '-'}"
    ]

    if game.game_over:
        ui_texts.append("")
        ui_texts.append("GAME OVER! (Yeniden baslamak icin BOSLUK)")

    for i, text in enumerate(ui_texts):
        text_surface = font.render(text, True, TEXT_COLOR)
        screen.blit(text_surface, (10, 10 + (i * 20)))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()