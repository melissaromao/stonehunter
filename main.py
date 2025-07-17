import pgzrun, random
from pgzero.builtins import Rect

menu = True
music_on = True

music.play('pixelland')

button_play = Rect((300, 150), (200, 50))
button_leave = Rect((300, 220), (200, 50))
button_music = Rect((300, 290), (200, 50))
button_reset = Rect((300, 290), (200, 50))

WIDTH = 800
HEIGHT = 500
TILE_SIZE = 18

tilemap = []
tilemap += [["S"] * 45 for i in range(10)]
tilemap += [
    ["S"] * 10 + ["G"] * 5 + ["S"] * 30,
    ["S"] * 45,
    ["S"] * 45,
    ["S"] * 25 + ["G"] * 5 + ["S"] * 15,
    ["S"] * 45,
    ["S"] * 45,
    ["S"] * 5 + ["G"] * 5 + ["S"] * 35,
    ["S"] * 35 + ["G"] * 5 + ["S"] * 5
]
tilemap += [["S"] * 45 for i in range(4)]
tilemap.append(["G"] * 45)
tilemap += [["D"] * 45 for i in range(6)]

tiles = []
stones = []
game_state = "game"

class Player:
    def __init__(self, pos):
        self.sprites = {
            "left": "player_left_static",
            "left_blink": "player_left_static_close_eyes",
            "right": "player_right_static",
            "right_blink": "player_right_static_close_eyes",
            "left_move": "player_left_moving",
            "right_move": "player_right_moving",
            "hit_right": "player_right_hurt",
            "hit_left": "player_left_hurt"
        }
        self.dir = "right"
        self.frame = 0
        self.count = 0
        self.hit_timer = 0
        self.sprite = Actor(self.sprites["right"])
        self.sprite.pos = pos
        self.vertical_speed = 0
        self.vel_grav = 0.5
        self.delay = 15
        self.hits_taken = 0
        self.damage_cooldown = 0
        self.state = "normal"
        self.damage = True

    def draw(self):
        self.sprite.draw()

    def update(self):
        move = False
        half_width = self.sprite.width // 2

        if keyboard.left and self.sprite.x - 2 - half_width >= 0:
            self.sprite.x -= 2
            self.sprite.image = self.sprites["left_move"]
            self.dir = "left"
            self.frame = 0
            self.count = 0
            move = True

        elif keyboard.right and self.sprite.x + 2 + half_width <= WIDTH:
            self.sprite.x += 2
            self.sprite.image = self.sprites["right_move"]
            self.dir = "right"
            self.frame = 0
            self.count = 0
            move = True

        self.vertical_speed += self.vel_grav
        self.sprite.y += self.vertical_speed

        for tile in tiles:
            if tile.image in ["grass", "ground"]:
                if self.sprite.colliderect(tile) and self.vertical_speed > 0:
                    self.sprite.y = tile.top - self.sprite.height / 2
                    self.vertical_speed = 0

        if keyboard.up and self.on_ground():
            self.vertical_speed = -11
            move = True

        if self.state == "normal":
            if not move:
                self.count += 1
                if self.count >= self.delay:
                    self.frame = (self.frame + 1) % 2
                    if self.dir == "left":
                        self.sprite.image = self.sprites["left"] if self.frame == 0 else self.sprites["left_blink"]
                    else:
                        self.sprite.image = self.sprites["right"] if self.frame == 0 else self.sprites["right_blink"]
                    self.count = 0

        elif self.state == "hit":
            self.sprite.image = self.sprites["hit_left"] if self.dir == "left" else self.sprites["hit_right"]
            self.hit_timer += 1
            sounds.hit_player.play()
            if self.hit_timer > 30:
                self.state = "normal"
                self.hit_timer = 0

        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

    def on_ground(self):
        for tile in tiles:
            if tile.image in ["grass", "ground"]:
                if (self.sprite.y + self.sprite.height / 2) >= tile.top and \
                   (self.sprite.y + self.sprite.height / 2) <= tile.top + 5 and \
                   abs(self.sprite.x - tile.x) < TILE_SIZE:
                    return True
        return False

class Enemy:
    def __init__(self, pos, direction=1):
        self.sprites = {
            "right1": "robot_bottom_static_right",
            "right2": "robot_up_static_right",
            "left1": "robot_bottom_static_left",
            "left2": "robot_up_static_left",
            "hit_right": "robot_hit_right",
            "hit_left": "robot_hit_left"
        }
        self.sprite = Actor(self.sprites["right1"])
        self.sprite.pos = pos
        self.dir = direction
        self.speed = 1
        self.frame = 0
        self.count = 0
        self.delay = 20
        self.state = "normal"
        self.hits_taken = 0

    def draw(self):
        self.sprite.draw()

    def on_ground(self):
        x = self.sprite.x + (self.dir * TILE_SIZE // 2)
        y = self.sprite.y + self.sprite.height // 2 + 1
        for tile in tiles:
            if tile.image in ["grass", "ground"]:
                if tile.collidepoint((x, y)):
                    return True
        return False

    def update(self):
        if self.state == "normal":
            self.sprite.x += self.dir * self.speed
            if not self.on_ground():
                self.dir *= -1

            self.count += 1
            if self.count >= self.delay:
                self.frame = (self.frame + 1) % 2
                if self.dir == 1:
                    self.sprite.image = self.sprites["right1"] if self.frame == 0 else self.sprites["right2"]
                else:
                    self.sprite.image = self.sprites["left1"] if self.frame == 0 else self.sprites["left2"]
                self.count = 0
        elif self.state == "hit":
            self.count += 1
            if self.count > 30:
                self.state = "normal"
                self.count = 0

def create_map():
    tile_dict = {"G": "grass", "D": "ground", "S": "sky"}
    for i in range(len(tilemap)):
        for j in range(len(tilemap[i])):
            tile_type = tilemap[i][j]
            tile = tile_dict.get(tile_type)
            if tile:
                bloc = Actor(tile)
                bloc.topleft = (j * TILE_SIZE, i * TILE_SIZE)
                tiles.append(bloc)

player = Player((100, 100))
enemies = []
create_map()

def create_stones():
    stones.clear()
    stone_temp = Actor("stone")
    stone = stone_temp.height
    pos_ok = []

    for tile in tiles:
        if tile.image == "grass":
            x = tile.x
            y = tile.top - stone // 2
            pos_ok.append((x, y))

    for pos in random.sample(pos_ok, k=min(len(pos_ok), random.randint(3, 7))):
        stone = Actor("stone")
        stone.pos = pos
        stones.append(stone)

def create_enemies():
    enemies.clear()
    positions = [
        (12 * TILE_SIZE, 9.5 * TILE_SIZE),
        (27 * TILE_SIZE, 12.5 * TILE_SIZE),
        (7 * TILE_SIZE, 15.5 * TILE_SIZE),
        (37 * TILE_SIZE, 16.5 * TILE_SIZE),
        (20 * TILE_SIZE, 21.5 * TILE_SIZE)
    ]
    for pos in positions:
        enemy = Enemy(pos, direction=1)
        enemies.append(enemy)

create_stones()
create_enemies()

def update():
    global game_state

    if menu or game_state == "game_over":
        return

    player.update()

    for stone in stones[:]:
        if player.sprite.colliderect(stone):
            stones.remove(stone)
            sounds.collect.play()

    for enemy in enemies:
        enemy.update()
        if player.sprite.colliderect(enemy.sprite):
            if player.vertical_speed > 0 and player.sprite.y < enemy.sprite.y:
                player.vertical_speed = -8
                enemy.state = "hit"
                enemy.hits_taken += 1
                sounds.hit_enemy.play()
                enemy.sprite.image = enemy.sprites["hit_right"] if enemy.dir == 1 else enemy.sprites["hit_left"]
            else:
                if player.damage and player.damage_cooldown == 0:
                    player.hits_taken += 1
                    player.damage_cooldown = 30
                    player.damage = False
                    player.state = "hit"
                    player.hit_timer = 0
                    
                    if player.hits_taken >= 6:
                        game_state = "game_over"
        else:
            player.damage = True

    enemies[:] = [e for e in enemies if e.hits_taken < 3]

    if not stones and not enemies:
        game_state = "victory"

def draw_hearts():
    for i in range(3):
        damage = max(0, player.hits_taken - i * 2)
        img = "life_1" if damage == 0 else "life_2" if damage == 1 else "life_3"
        heart = Actor(img)
        heart.topleft = (10 + i * 25, 10)
        heart.draw()

def draw_menu():
    screen.blit("background_menu", (0, 0))
    screen.draw.text("STONE HUNTER", center=(WIDTH//2, 80), fontsize=40, color="black")
    screen.draw.text("Colete todas as pedras e derrote seus inimigos!", center=(WIDTH//2, 110), fontsize=30, color="#444444")
    screen.draw.filled_rect(button_play, "#2eb082")
    screen.draw.text("Jogar", center=button_play.center, color="white")
    screen.draw.filled_rect(button_leave, "#dd442c")
    screen.draw.text("Sair", center=button_leave.center, color="white")
    screen.draw.filled_rect(button_music, "#32bee9")
    texto_musica = "Musica: ON" if music_on else "Musica: OFF"
    screen.draw.text(texto_musica, center=button_music.center, color="white")

def on_mouse_down(pos):
    global menu, music_on, game_state, player

    if menu:
        if button_play.collidepoint(pos):
            menu = False
        elif button_leave.collidepoint(pos):
            exit()
        elif button_music.collidepoint(pos):
            music_on = not music_on
            music.set_volume(0.5 if music_on else 0.0)

    elif game_state in ["victory", "game_over"]:
        if button_reset.collidepoint(pos):
            menu = True
            game_state = "game"
            player = Player((100, 100))
            create_stones()
            create_enemies()

def draw():
    screen.clear()
    if menu:
        draw_menu()
        return
    for bloc in tiles:
        bloc.draw()
    for enemy in enemies:
        enemy.draw()
    for stone in stones:
        stone.draw()
    player.draw()
    draw_hearts()

    if game_state in ["victory", "game_over"]:
        screen.blit("background_menu", (0, 0))
        mensagem = "Pedras coletadas! Player venceu!" if game_state == "victory" else "Player perdeu!"
        screen.draw.text(mensagem, center=(WIDTH//2, HEIGHT//2), fontsize=50, color="black")
        screen.draw.filled_rect(button_reset, "#2ba0c4")
        screen.draw.text("Reiniciar", center=button_reset.center, color="white")