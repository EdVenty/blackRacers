import gc
import pyb

class RGB:
    buf_bytes = (0x11, 0x13, 0x31, 0x33)

    def __init__(self, spi_bus=1, led_count=1, intensity=1):
        self.led_count = led_count
        self.intensity = intensity
        self.buf_length = self.led_count * 3 * led_count
        self.buf = bytearray(self.buf_length)
        self.spi = pyb.SPI(spi_bus, pyb.SPI.MASTER, baudrate=3200000, polarity=0, phase=0)
        self.show([])

    def show(self, data):
        self.fill_buf(data)
        self.send_buf()

    def send_buf(self):
        self.spi.send(self.buf)
        gc.collect()

    def update_buf(self, data, start=0):
        buf = self.buf
        buf_bytes = self.buf_bytes
        intensity = self.intensity

        mask = 0x03
        index = start * 12
        for red, green, blue in data:
            red = int(red * intensity)
            green = int(green * intensity)
            blue = int(blue * intensity)

            buf[index] = buf_bytes[green >> 6 & mask]
            buf[index+1] = buf_bytes[green >> 4 & mask]
            buf[index+2] = buf_bytes[green >> 2 & mask]
            buf[index+3] = buf_bytes[green & mask]

            buf[index+4] = buf_bytes[red >> 6 & mask]
            buf[index+5] = buf_bytes[red >> 4 & mask]
            buf[index+6] = buf_bytes[red >> 2 & mask]
            buf[index+7] = buf_bytes[red & mask]

            buf[index+8] = buf_bytes[blue >> 6 & mask]
            buf[index+9] = buf_bytes[blue >> 4 & mask]
            buf[index+10] = buf_bytes[blue >> 2 & mask]
            buf[index+11] = buf_bytes[blue & mask]

            index += 12
        return index // 12

    def fill_buf(self, data):
        end = self.update_buf(data)
        buf = self.buf
        off = self.buf_bytes[0]
        for index in range(end * 12, self.buf_length):
            buf[index] = off
            index += 1

# from rgb import RGB
# ring = RGB(spi_bus=1, led_count=4)
# data = [
#     (24, 0, 0),
#     (0, 24, 0),
#     (0, 0, 24),
#     (0, 24, 24),
# ]
# ring.show(data)