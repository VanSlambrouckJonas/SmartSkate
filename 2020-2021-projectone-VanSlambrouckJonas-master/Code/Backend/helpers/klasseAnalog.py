from RPi import GPIO
import time
import spidev

min = 3.2
max = 4.2

class ANALOG:
    def __init__(self,bus=0,device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device) # Bus SPI0, slave op CE 0
        self.spi.max_speed_hz = 10 ** 5 # 100

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(16, GPIO.OUT)

    def read_channel(self, sens):
        channel = sens << 4 | 128

        bytes_out = [0b00000001, channel, 0b00000000]

        bytes_in = self.spi.xfer2(bytes_out)

        byte1 = bytes_in[1]
        byte2 = bytes_in[2]
        result = byte1 << 8 | byte2

        if sens == 2:
            print("#" + format(sens, '.2f') + "            " + format((3.3*(result / 1023.0) * 1.52), '.2f') + "V" + "      " + format((((3.3*(result / 1023.0) * 1.52) - min) * 100) / (max - min), '.2f') + "%")
            return format((((3.3*(result / 1023.0) * 1.52) - min) * 100) / (max - min), '.2f')
        elif sens == 3:
            print("#" + format(sens, '.2f') + "            " + format((3.3*(result / 1023.0) * 1.16), '.2f') + "V" + "      " + format((((3.3*(result / 1023.0) * 1.16) - min) * 100) / (max - min), '.2f') + "%")
            return format((((3.3*(result / 1023.0) * 1.16) - min) * 100) / (max - min), '.2f')
        elif sens == 4:
            print("#" + format(sens, '.2f') + "            " + format((3.3*(result / 1023.0) * 1.62), '.2f') + "V" + "      " + format((((3.3*(result / 1023.0) * 1.62) - min) * 100) / (max - min), '.2f') + "%")
            return format((((3.3*(result / 1023.0) * 1.62) - min) * 100) / (max - min), '.2f')
        elif sens == 5:
            print("#" + format(sens, '.2f') + "            " + format((3.3*(result / 1023.0) * 1.6), '.2f') + "V" + "      " + format((((3.3*(result / 1023.0) * 1.6) - min) * 100) / (max - min), '.2f') + "%")
            return format((((3.3*(result / 1023.0) * 1.6) - min) * 100) / (max - min), '.2f')
        elif sens == 6:
            print("#" + format(sens, '.2f') + "            " + format((3.3*(result / 1023.0) * 1.41), '.2f') + "V" + "      " + format((((3.3*(result / 1023.0) * 1.41) - min) * 100) / (max - min), '.2f') + "%")
            return format((((3.3*(result / 1023.0) * 1.41) - min) * 100) / (max - min), '.2f')
        elif sens == 7:
            print("#" + format(sens, '.2f') + "            " + format((3.3*(result / 1023.0) * 1.34), '.2f') + "V" + "      " + format((((3.3*(result / 1023.0) * 1.34) - min) * 100) / (max - min), '.2f') + "%")
            return format((((3.3*(result / 1023.0) * 1.34) - min) * 100) / (max - min), '.2f')
        

    def closespi(self):
        self.spi.close()

ANALOG().__init__()