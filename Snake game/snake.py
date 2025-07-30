import pygame, sys, random
from pygame.math import Vector2

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

cell_size = 20
cell_number = 40
screen = pygame.display.set_mode((cell_number * cell_size, cell_number * cell_size))
clock = pygame.time.Clock()
apple = pygame.image.load('Graphics/apple.png').convert_alpha()
game_font = pygame.font.Font('Font/PoetsenOne-Regular.ttf', 25)
menu_font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 58)

mode = "Medium"
game_state = "menu"
speed = 150

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, speed)

class SNAKE:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)
        self.new_block = False

        self.head_up = pygame.image.load('Graphics/head_up.png').convert_alpha()
        self.head_down = pygame.image.load('Graphics/head_down.png').convert_alpha()
        self.head_right = pygame.image.load('Graphics/head_right.png').convert_alpha()
        self.head_left = pygame.image.load('Graphics/head_left.png').convert_alpha()

        self.tail_up = pygame.image.load('Graphics/tail_up.png').convert_alpha()
        self.tail_down = pygame.image.load('Graphics/tail_down.png').convert_alpha()
        self.tail_right = pygame.image.load('Graphics/tail_right.png').convert_alpha()
        self.tail_left = pygame.image.load('Graphics/tail_left.png').convert_alpha()

        self.body_vertical = pygame.image.load('Graphics/body_vertical.png').convert_alpha()
        self.body_horizontal = pygame.image.load('Graphics/body_horizontal.png').convert_alpha()

        self.body_tr = pygame.image.load('Graphics/body_tr.png').convert_alpha()
        self.body_tl = pygame.image.load('Graphics/body_tl.png').convert_alpha()
        self.body_br = pygame.image.load('Graphics/body_br.png').convert_alpha()
        self.body_bl = pygame.image.load('Graphics/body_bl.png').convert_alpha()

        self.crunch_sound = pygame.mixer.Sound('Sounds/sound.mp3')

    def draw_snake(self):
        self.update_head_graphics()
        self.update_tail_graphics()

        for index, block in enumerate(self.body):
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)

            if index == 0:
                screen.blit(self.head, block_rect)
            elif index == len(self.body) - 1:
                screen.blit(self.tail, block_rect)
            else:
                previous_block = self.body[index + 1] - block
                next_block = self.body[index - 1] - block
                if previous_block.x == next_block.x:
                    screen.blit(self.body_vertical, block_rect)
                elif previous_block.y == next_block.y:
                    screen.blit(self.body_horizontal, block_rect)
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        screen.blit(self.body_tl, block_rect)
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        screen.blit(self.body_bl, block_rect)
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        screen.blit(self.body_tr, block_rect)
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        screen.blit(self.body_br, block_rect)

    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1, 0): self.head = self.head_left
        elif head_relation == Vector2(-1, 0): self.head = self.head_right
        elif head_relation == Vector2(0, 1): self.head = self.head_up
        elif head_relation == Vector2(0, -1): self.head = self.head_down

    def update_tail_graphics(self):
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Vector2(1, 0): self.tail = self.tail_left
        elif tail_relation == Vector2(-1, 0): self.tail = self.tail_right
        elif tail_relation == Vector2(0, 1): self.tail = self.tail_up
        elif tail_relation == Vector2(0, -1): self.tail = self.tail_down

    def move_snake(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self):
        self.new_block = True

    def play_crunch_sound(self):
        self.crunch_sound.play()

    def reset(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)

class FRUIT:
    def __init__(self, obstacles):
        self.obstacles = obstacles
        self.randomize()

    def draw_fruit(self):
        fruit_rect = pygame.Rect(int(self.pos.x * cell_size), int(self.pos.y * cell_size), cell_size, cell_size)
        screen.blit(apple, fruit_rect)

    def randomize(self):
        while True:
            self.x = random.randint(0, cell_number - 1)
            self.y = random.randint(0, cell_number - 1)
            self.pos = Vector2(self.x, self.y)
            fruit_rect = pygame.Rect(self.x * cell_size, self.y * cell_size, cell_size, cell_size)
            if all(not fruit_rect.colliderect(obs) for obs in self.obstacles):
                break

class MAIN:
    def __init__(self):
        self.obstacles = []
        self.snake = SNAKE()
        self.generate_obstacles()
        self.fruit = FRUIT(self.obstacles)

    def generate_obstacles(self):
        self.obstacles.clear()
        count = 7 if mode == "Easy" else 9 if mode == "Medium" else 11
        while len(self.obstacles) < count:
            x = random.randint(0, cell_number - 1)
            y = random.randint(0, cell_number - 1)
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            if rect.collidelist(self.obstacles) == -1 and all(Vector2(x, y) != b for b in self.snake.body):
                self.obstacles.append(rect)

    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()

    def draw_elements(self):
        self.draw_grass()
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_obstacles()
        self.draw_score()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()

        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()

    def check_fail(self):
        head = self.snake.body[0]
        head_rect = pygame.Rect(int(head.x * cell_size), int(head.y * cell_size), cell_size, cell_size)
        if not 0 <= head.x < cell_number or not 0 <= head.y < cell_number:
            self.game_over()
        for block in self.snake.body[1:]:
            if block == head:
                self.game_over()
        for obs in self.obstacles:
            if head_rect.colliderect(obs):
                self.game_over()

    def game_over(self):
        current_score = len(self.snake.body) - 3
        try:
            with open("highscore.txt", "r") as f:
                high_score = int(f.read())
        except:
            high_score = 0
        if current_score > high_score:
            with open("highscore.txt", "w") as f:
                f.write(str(current_score))
        self.snake.reset()
        self.generate_obstacles()
        self.fruit.randomize()

    def draw_obstacles(self):
        for rect in self.obstacles:
            pygame.draw.rect(screen, (139, 0, 0), rect)

    def draw_grass(self):
        grass_color = (167, 209, 61)
        for row in range(cell_number):
            for col in range(cell_number):
                if (row + col) % 2 == 0:
                    grass_rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                    pygame.draw.rect(screen, grass_color, grass_rect)

    def draw_score(self):
        score_text = str(len(self.snake.body) - 3)
        score_surface = game_font.render(score_text, True, (56, 74, 12))
        score_x = int(cell_size * cell_number - 60)
        score_y = int(cell_size * cell_number - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        apple_rect = apple.get_rect(midright=(score_rect.left, score_rect.centery))
        bg_rect = pygame.Rect(apple_rect.left, apple_rect.top, apple_rect.width + score_rect.width + 6, apple_rect.height)

        pygame.draw.rect(screen, (167, 209, 61), bg_rect)
        screen.blit(score_surface, score_rect)
        screen.blit(apple, apple_rect)
        pygame.draw.rect(screen, (56, 74, 12), bg_rect, 2)

main_game = MAIN()

def draw_text_center(text, font, color, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(cell_number * cell_size // 2, y))
    screen.blit(surface, rect)

def show_menu():
    screen.fill((30, 30, 30))
    draw_text_center("🐍 Snake Game", title_font, (255, 255, 255), 120)
    draw_text_center("1. ▶️ Play Game", menu_font, (200, 200, 200), 200)
    draw_text_center(f"2. 🎮 Select Mode: {mode}", menu_font, (200, 200, 200), 260)
    draw_text_center("3. 📜 How to Play", menu_font, (200, 200, 200), 320)
    draw_text_center("4. ❌ Quit", menu_font, (200, 200, 200), 380)
    pygame.display.flip()

def show_instructions():
    screen.fill((20, 20, 20))
    draw_text_center("📜 How to Play", title_font, (255, 255, 255), 100)
    lines = [
        "Use arrow keys to move the snake.",
        "Eat apples to grow.",
        "Don't hit walls, yourself or obstacles.",
        "Press ESC to return."
    ]
    for i, line in enumerate(lines):
        draw_text_center(line, menu_font, (200, 200, 200), 180 + i * 50)
    pygame.display.flip()

while True:
    if game_state == "menu":
        show_menu()
    elif game_state == "howto":
        show_instructions()
    elif game_state == "play":
        screen.fill((175, 215, 70))
        main_game.draw_elements()
        pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_state = "play"
                    speed = 200 if mode == "Easy" else 150 if mode == "Medium" else 100
                    pygame.time.set_timer(SCREEN_UPDATE, speed)
                    main_game = MAIN()
                elif event.key == pygame.K_2:
                    mode = "Easy" if mode == "Medium" else "Hard" if mode == "Easy" else "Medium"
                elif event.key == pygame.K_3:
                    game_state = "howto"
                elif event.key == pygame.K_4:
                    pygame.quit()
                    sys.exit()
        elif game_state == "howto" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = "menu"
        elif game_state == "play":
            if event.type == SCREEN_UPDATE:
                main_game.update()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                if event.key == pygame.K_UP and main_game.snake.direction.y != 1:
                    main_game.snake.direction = Vector2(0, -1)
                if event.key == pygame.K_DOWN and main_game.snake.direction.y != -1:
                    main_game.snake.direction = Vector2(0, 1)
                if event.key == pygame.K_LEFT and main_game.snake.direction.x != 1:
                    main_game.snake.direction = Vector2(-1, 0)
                if event.key == pygame.K_RIGHT and main_game.snake.direction.x != -1:
                    main_game.snake.direction = Vector2(1, 0)

    clock.tick(60)