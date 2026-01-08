from machine import Pin, ADC
from neopixel import NeoPixel
from time import sleep_ms

#핀 설정
switch_pin = Pin(27, Pin.IN, Pin.PULL_UP) 
NP_PIN = 14
NP_COUNT = 12   
LDR_PIN = 34     

np = NeoPixel(Pin(NP_PIN), NP_COUNT)
ldr = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_11DB)

def set_light(r, g, b):
    for i in range(NP_COUNT):
        np[i] = (r, g, b)
    np.write()

print("슬라이드 스위치 작동 중...")

while True:
    if switch_pin.value() == 0:
        light_level = ldr.read()
        if light_level > 2000:
            set_light(200, 50, 0) # 어두우면 켜짐
        else:
            set_light(0, 0, 0)    # 밝으면 꺼짐
            
    else: #스위치를 반대로 했을때
        set_light(200, 50, 0) # 무조건 켜짐
    

    sleep_ms(100)
