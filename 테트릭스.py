import time
import random
from machine import Pin, SPI, ADC
from ili9225 import ILI9225

# --- [1. 핀 설정] ---
# LCD (VSPI)
spi = SPI(2, baudrate=20000000, sck=Pin(18), mosi=Pin(23))
lcd = ILI9225(spi, Pin(5, Pin.OUT), Pin(2, Pin.OUT), Pin(4, Pin.OUT))

# 조이스틱 (입력)
vx = ADC(Pin(34))
vy = ADC(Pin(35))
sw = Pin(32, Pin.IN, Pin.PULL_UP)
vx.atten(ADC.ATTN_11DB)
vy.atten(ADC.ATTN_11DB)

# --- [2. 게임 설정] ---
COLS = 10
ROWS = 18
CELL_SIZE = 10  # 한 칸의 크기 (픽셀)
OFFSET_X = 38   # 화면 중앙 정렬을 위한 여백
OFFSET_Y = 20

# 테트리미노 모양 (7가지)
SHAPES = [
    [[1, 1, 1, 1]], # I
    [[1, 1], [1, 1]], # O
    [[0, 1, 0], [1, 1, 1]], # T
    [[1, 1, 0], [0, 1, 1]], # S
    [[0, 1, 1], [1, 1, 0]], # Z
    [[1, 0, 0], [1, 1, 1]], # L
    [[0, 0, 1], [1, 1, 1]]  # J
]

COLORS = [0xF800, 0x07E0, 0x001F, 0xFFE0, 0xF81F, 0x07FF, 0x7BEF]

class Tetris:
    def __init__(self):
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.new_piece()
        self.score = 0
        self.game_over = False

    def new_piece(self):
        self.piece = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.px = COLS // 2 - len(self.piece[0]) // 2
        self.py = 0
        if self.check_collision(self.px, self.py, self.piece):
            self.game_over = True

    def check_collision(self, x, y, piece):
        for r, row in enumerate(piece):
            for c, val in enumerate(row):
                if val:
                    if x + c < 0 or x + c >= COLS or y + r >= ROWS:
                        return True
                    if self.board[y + r][x + c]:
                        return True
        return False

    def rotate(self, piece):
        return [list(row) for row in zip(*piece[::-1])]

    def lock_piece(self):
        for r, row in enumerate(self.piece):
            for c, val in enumerate(row):
                if val:
                    self.board[self.py + r][self.px + c] = self.color
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        new_board = [row for row in self.board if any(val == 0 for val in row)]
        lines_cleared = ROWS - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [0] * COLS)
        self.board = new_board
        self.score += lines_cleared * 100

    def draw(self):
        lcd.fill(0x0000) # 배경 지우기
        # 보드 테두리
        lcd.rect(OFFSET_X-2, OFFSET_Y-2, COLS*CELL_SIZE+4, ROWS*CELL_SIZE+4, 0xFFFF)
        
        # 고정된 블록들 그리기
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c]:
                    lcd.fill_rect(OFFSET_X + c*CELL_SIZE, OFFSET_Y + r*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1, self.board[r][c])
        
        # 현재 떨어지는 블록 그리기
        for r, row in enumerate(self.piece):
            for c, val in enumerate(row):
                if val:
                    lcd.fill_rect(OFFSET_X + (self.px + c)*CELL_SIZE, OFFSET_Y + (self.py + r)*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1, self.color)
        
        lcd.text(f"Score: {self.score}", 10, 5, 0xFFFF)
        lcd.show()

def main():
    game = Tetris()
    last_fall_time = time.ticks_ms()
    
    while not game.game_over:
        current_time = time.ticks_ms()
        
        # 조이스틱 입력 처리
        x_val = vx.read()
        y_val = vy.read()
        
        if x_val < 500: # Left
            if not game.check_collision(game.px - 1, game.py, game.piece):
                game.px -= 1
            time.sleep_ms(100)
        elif x_val > 3500: # Right
            if not game.check_collision(game.px + 1, game.py, game.piece):
                game.px += 1
            time.sleep_ms(100)
        
        if y_val < 500: # Rotate (Up)
            rotated = game.rotate(game.piece)
            if not game.check_collision(game.px, game.py, rotated):
                game.piece = rotated
            time.sleep_ms(150)
        elif y_val > 3500: # Fast Drop (Down)
            if not game.check_collision(game.px, game.py + 1, game.piece):
                game.py += 1
        
        # 일정 시간마다 자동 낙하
        if time.ticks_diff(current_time, last_fall_time) > 500:
            if not game.check_collision(game.px, game.py + 1, game.piece):
                game.py += 1
            else:
                game.lock_piece()
            last_fall_time = current_time
        
        game.draw()

    lcd.fill(0x0000)
    lcd.text("GAME OVER", 50, 100, 0xF800)
    lcd.text(f"Score: {game.score}", 55, 120, 0xFFFF)
    lcd.show()
    print("Game Over!")

main()
