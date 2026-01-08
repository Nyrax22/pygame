import time

class SDCard:
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        self.cmdbuf = bytearray(6)
        self.cs.init(self.cs.OUT, value=1)
        # 초기화 전 전압 안정화 대기
        time.sleep_ms(50)
        self.init_card()

    def init_card(self):
        # 1. 초기화 전 더미 클럭 송신 (최소 74비트 이상)
        self.cs.value(1)
        for i in range(100):
            self.spi.write(b'\xff')
        
        # 2. 소프트웨어 리셋 (CMD0) - Idle 상태 진입
        success = False
        for i in range(20): # 시도 횟수 증가
            if self.cmd(0, 0, 0x95) == 1:
                success = True
                break
            time.sleep_ms(50)
        if not success:
            raise OSError("SD 카드 CMD0 응답 없음 (연결 확인)")

        # 3. 전압 및 버전 확인 (CMD8)
        self.cmd(8, 0x1aa, 0x87)

        # 4. 카드 활성화 (ACMD41) - 고용량 카드 지원(HCS=1)
        for i in range(100):
            self.cmd(55, 0, 0)
            if self.cmd(41, 0x40000000, 0) == 0:
                print("SD 카드 활성화 완료")
                break
            time.sleep_ms(20)
        else:
            raise OSError("SD 카드 ACMD41 타임아웃")
        
        # 5. 블록 사이즈 확인
        self.cmd(58, 0, 0)
        self.cs.value(1)
        self.spi.write(b'\xff')

    def cmd(self, cmd, arg, crc):
        self.cs.value(0)
        self.cmdbuf[0] = 0x40 | cmd
        self.cmdbuf[1] = arg >> 24
        self.cmdbuf[2] = arg >> 16
        self.cmdbuf[3] = arg >> 8
        self.cmdbuf[4] = arg
        self.cmdbuf[5] = crc
        self.spi.write(self.cmdbuf)
        
        # 응답 대기 (최대 100바이트)
        for i in range(100):
            res = self.spi.read(1, 0xff)[0]
            if not (res & 0x80):
                self.cs.value(1)
                self.spi.write(b'\xff')
                return res
        self.cs.value(1)
        self.spi.write(b'\xff')
        return 0xff

    def readblocks(self, n, buf):
        self.cs.value(0)
        # 최신 카드는 n(블록 번호)을 직접 사용
        if self.cmd(17, n, 0) != 0:
            self.cs.value(1)
            raise OSError("SD 읽기 명령(CMD17) 실패")

        # 데이터 시작 토큰(0xFE) 대기 (루프 최적화)
        timeout = 50000
        while timeout > 0:
            if self.spi.read(1, 0xff)[0] == 0xfe:
                break
            timeout -= 1
        
        if timeout <= 0:
            self.cs.value(1)
            raise OSError("SD 데이터 토큰 타임아웃")

        self.spi.readinto(buf)
        self.spi.read(2, 0xff) # CRC 생략
        self.cs.value(1)
        self.spi.write(b'\xff')

    def ioctl(self, op, arg):
        if op == 4: return 31250000
        if op == 5: return 512
        return 0
