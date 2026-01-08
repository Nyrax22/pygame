import bluetooth #블루투스 라이브러리
import struct

class BLESimplePeripheral:
    def __init__(self, ble, name="ESP32-Mood"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((
            (bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E"), (
                (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_NOTIFY), #RX
                (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_WRITE),  #TX
            )),
        ))
        self._write_callback = None
        self._payload = self._ad_payload(name=name)
        self._advertise()

    def _irq(self, event, data):
        if event == 1: self._advertise()
        elif event == 3:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(self._ble.gatts_read(self._handle_rx))

    def _ad_payload(self, name):
        payload = bytearray(b'\x02\x01\x06')
        payload += struct.pack("BB", len(name) + 1, 0x09) + name.encode()
        return payload

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):

        self._write_callback = callback
