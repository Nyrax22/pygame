import time
import random
from machine import Pin, SPI, ADC
from ili9225 import ILI9225

# =====================
# LCD 설정
# =====================
spi = SPI(2, baudrate=20000000, sck=Pin(18), mosi=Pin(23))
lcd = ILI9225(spi, Pin(5, Pin.OUT), Pin(2, Pin.OUT), Pin(4, Pin.OUT))

# =====================
# 조이스틱 설정
# =====================
vx = ADC(Pin(34))
vy = ADC(Pin(35))
sw = Pin(32, Pin.IN, Pin.PULL_UP)
vx.atten(ADC.ATTN_11DB)
vy.atten(ADC.ATTN_11DB)

# =====================
# 게임 설정
# =====================
COLS = 16
ROWS = 20
CELL = 10
OX = 20
OY = 20

BLACK = 0x0000
GREEN = 0x07E0
RED   = 0xF800
WHITE = 0xFFFF

DIRS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}

# =====================
# Snake 클래스
# =====================
class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = [(COLS//2, ROWS//2)]
        self.dir = "RIGHT"
        self.spawn_food()
        self.score = 0
        self.game_over = False
        self.speed = 300

    def spawn_food(self):
        while True:
            pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if pos not in self.snake:
                self.food = pos
                return

    def move(self):
        dx, dy = DIRS[self.dir]
        head = (self.snake[0][0] + dx, self.snake[0][1] + dy)

        # 충돌 판정
        if (head[0] < 0 or head[0] >= COLS or
            head[1] < 0 or head[1] >= ROWS or
            head in self.snake):
            self.game_over = True
            return

        self.snake.insert(0, head)

        if head == self.food:
            self.score += 100
            self.speed = max(80, self.speed - 15)
            self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        lcd.fill(BLACK)

        # 테두리
        lcd.rect(OX-2, OY-2, COLS*CELL+4, ROWS*CELL+4, WHITE)

        # 음식
        fx, fy = self.food
        lcd.fill_rect(OX + fx*CELL, OY + fy*CELL, CELL-1, CELL-1, RED)

        # 뱀
        for x, y in self.snake:
            lcd.fill_rect(OX + x*CELL, OY + y*CELL, CELL-1, CELL-1, GREEN)

        lcd.text(f"Score:{self.score}", 10, 5, WHITE)
        lcd.show()

def wait_restart():
    t0 = None
    while True:
        if sw.value() == 0:
            if t0 is None:
                t0 = time.ticks_ms()
            elif time.ticks_diff(time.ticks_ms(), t0) > 800:
                return
        else:
            t0 = None
        time.sleep_ms(50)

# =====================
# 메인 루프
# =====================
def main():
    game = SnakeGame()
    last = time.ticks_ms()

    while True:
        while not game.game_over:
            now = time.ticks_ms()

            # 조이스틱 입력
            x = vx.read()
            y = vy.read()

            if x < 500 and game.dir != "RIGHT":
                game.dir = "LEFT"
            elif x > 3500 and game.dir != "LEFT":
                game.dir = "RIGHT"
            elif y < 500 and game.dir != "DOWN":
                game.dir = "UP"
            elif y > 3500 and game.dir != "UP":
                game.dir = "DOWN"

            if time.ticks_diff(now, last) > game.speed:
                game.move()
                game.draw()
                last = now

        # GAME OVER 화면
        lcd.fill(BLACK)
        lcd.text("GAME OVER", 45, 90, RED)
        lcd.text("HOLD BUTTON", 32, 115, WHITE)
        lcd.text("TO RESTART", 38, 135, WHITE)
        lcd.show()

        wait_restart()
        game.reset()
        last = time.ticks_ms()

main()
