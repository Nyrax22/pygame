import time
import struct
import framebuf

class ILI9225(framebuf.FrameBuffer):
    def __init__(self, spi, cs, rs, rst, width=176, height=220):
        self.spi = spi
        self.cs = cs
        self.rs = rs
        self.rst = rst
        self.width = width
        self.height = height
        
        # RGB565 버퍼 생성
        self.buffer = bytearray(self.width * self.height * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        
        self.cs.init(self.cs.OUT, value=1)
        self.rs.init(self.rs.OUT, value=0)
        self.rst.init(self.rst.OUT, value=1)
        
        self.reset()
        self.init_display()

    def write_reg(self, reg, data):
        self.rs.value(0)
        self.cs.value(0)
        self.spi.write(struct.pack('>H', reg))
        self.cs.value(1)
        self.rs.value(1)
        self.cs.value(0)
        self.spi.write(struct.pack('>H', data))
        self.cs.value(1)

    def reset(self):
        self.rst.value(1)
        time.sleep_ms(50)
        self.rst.value(0)
        time.sleep_ms(100)
        self.rst.value(1)
        time.sleep_ms(100)

    def init_display(self):
        config = [
            (0x10, 0x0000), (0x01, 0x011C), (0x02, 0x0100), (0x03, 0x1030),
            (0x08, 0x0808), (0x0C, 0x0000), (0x0F, 0x0E01), (0x20, 0x0000),
            (0x21, 0x0000), (0x11, 0x103B), (0x12, 0x2311), (0x13, 0x0066),
            (0x14, 0x5560), (0x07, 0x1017)
        ]
        for reg, val in config:
            self.write_reg(reg, val)
        time.sleep_ms(100)

    def show(self):
        self.write_reg(0x36, self.width - 1)
        self.write_reg(0x37, 0)
        self.write_reg(0x38, self.height - 1)
        self.write_reg(0x39, 0)
        self.write_reg(0x20, 0)
        self.write_reg(0x21, 0)
        self.rs.value(0)
        self.cs.value(0)
        self.spi.write(struct.pack('>H', 0x22))
        self.cs.value(1)
        self.rs.value(1)
        self.cs.value(0)
        self.spi.write(self.buffer)
        self.cs.value(1)
        self.spi.write(b'\xff')
