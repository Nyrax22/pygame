from machine import Pin, SPI
import time

# SPI 설정 (속도를 100kHz로 시작 - 초기화용)
sck = Pin(14)
mosi = Pin(13)
miso = Pin(19)
cs = Pin(27, Pin.OUT, value=1)

# ESP32 하드웨어 SPI 2번 사용
spi = SPI(2, baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

def test_sd():
    print("SD 카드 연결 테스트 시작...")
    
    # 1. 칩 선택 해제 상태에서 충분한 더미 클럭 공급
    cs.value(1)
    for _ in range(100): 
        spi.write(b'\xff')
    
    time.sleep_ms(10) # 잠시 대기
    
    # 2. CMD0 전송 (CS=0)
    cs.value(0)
    # CMD0: 0x40 | 0 = 0x40, 인자 0, CRC 0x95
    spi.write(bytearray([0x40, 0, 0, 0, 0, 0x95]))
    
    # 3. 응답(R1) 대기 (최대 100번 시도)
    res = 0xff
    for i in range(100):
        res = spi.read(1, 0xff)[0]
        if res != 0xff:
            break
            
    cs.value(1) # 종료 시 CS 높임
    spi.write(b'\xff') # 추가 클럭

    if res == 0x01:
        print(f"성공! SD 카드가 Idle 상태(0x01)로 진입했습니다.")
        return True
    else:
        print(f"실패: 응답값 {hex(res)} (0xff인 경우 연결 문제)")
        return False

test_sd()
