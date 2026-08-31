
import serial
import struct
from crc_utils import crc_table

from multiprocessing import shared_memory
import numpy as np
import time
import socket

ARRAY_SIZE = 360
SHM_NAME = "lidar360"
SHM_SIGNAL_NAME = "rr_signal"

class LIDAR_READER:
    def __init__(self):
        self.serial_port="/dev/ttyUSB0"
        self.baudrate=230400
        self.PACKET_LENGTH = 49
        self.POINT_PER_PACK = 12
        self.serial_conn = serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=1)
        if self.serial_conn:
            print("serial connection offen")
        else:
            print("error serial connection")

# Shared Memory für Nutzer-Prozesse erzeugen
        try:
            self.shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=ARRAY_SIZE * 4)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=SHM_NAME)

        self.distances = np.ndarray((ARRAY_SIZE,), dtype=np.int32, buffer=self.shm.buf)
        # Explizit mit Nullen füllen
        self.distances[:] = 0
        
# Shared Memory für Start-Signal:
        try:
            self.shm_signal = shared_memory.SharedMemory(name=SHM_SIGNAL_NAME, create=True, size=4)
        except FileExistsError:
            self.shm_signal = shared_memory.SharedMemory(name=SHM_SIGNAL_NAME)

        # Explizit mit Null füllen
        # Startsignal
        self.shm_signal.buf[0] = 0
        #Stopsignal
        self.shm_signal.buf[1] = 0


    def calculate_crc8(self, data):
        crc = 0x00
        for byte in data:
            crc = crc_table[(crc ^ byte) & 0xFF]
        return crc

    def parse_packet(self, packet):
        if len(packet) != self.PACKET_LENGTH:
            print("Invalid packet length.")
            return

        if packet[0] != 0x54 or packet[1] != 0x2C:
            print("Invalid packet header")
            return

        received_crc = packet[self.PACKET_LENGTH - 3]
        calculated_crc = self.calculate_crc8(packet[: self.PACKET_LENGTH - 3])
        if received_crc != calculated_crc:
            print("CRC8 checksum mismatch")
            return

        header, ver_len, speed, start_angle = struct.unpack("<BBHH", packet[:6])

        points = []
        offset = 6  # 4 + 2 bytes
        for _ in range(self.POINT_PER_PACK):
            distance, intensity = struct.unpack(
                "<HB", packet[offset : offset + 3]
            )  # 3-> 2+1 for slicing
            points.append({"distance": distance, "intensity": intensity})
            offset += 3

        end_angle, timestamp = struct.unpack("<HH", packet[42:46])

        # convert angles from hundredth of a degree to degrees
        start_angle = (start_angle % 36000) / 100.0
        end_angle = (end_angle % 36000) / 100.0

        # calculate angle increment
        angle_diff = (end_angle - start_angle + 360.0) % 360.0
        angle_increment = angle_diff / 11  # 12 points, so 11 intervals

        # interpolate angles for each point
        angles = [
            (start_angle + i * angle_increment) % 360.0
            for i in range(self.POINT_PER_PACK)
        ]

        scan_data = []
        for i, point in enumerate(points):
            scan_point = {
                "angle": angles[i],
                "distance": point["distance"],
                "intensity": point["intensity"],
            }
            scan_data.append(scan_point)

        return {
            "speed": speed,
            "start_angle": start_angle,
            "end_angle": end_angle,
            "timestamp": timestamp,
            "scan_data": scan_data,
        }

    def read_lidar_data(self):
        # read until header and ver_len values are found
        packet = self.serial_conn.read_until(b"\x54\x2C")
        if len(packet) != (self.PACKET_LENGTH - 2):
            return
        packet = bytes(b"\x54\x2C") + packet  # needed for checksum verification
        if len(packet) == self.PACKET_LENGTH:
            if data := self.parse_packet(packet):
                return data

    def wait_for_start(self):
        while self.shm_signal.buf[0] == 0:
            time.sleep(0.02)

    def close_serial_connection(self):
        self.serial_conn.close()
        
        
    def close(self):
        """Zentralisierte Aufräum-Logik."""
        #schließe Lidar scanner
        self.serial_conn.close()
        
        #Shared Memory freigeben
        self.shm.close()
        self.shm.unlink()
        self.shm_signal.close()
        self.shm_signal.unlink()
        

    # 1. Der "klassische" Destruktor (Garbage Collection)
    def __del__(self):
        self.close()

    # 2. Context Manager (für das 'with'-Statement)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
if __name__ == "__main__":
    print("Start Lidar Reader")
    lidar = LIDAR_READER()
    
    #warte auf Startknopf-Signal wg Regel 6.12
    print("Warte auf Start Signal")
    lidar.wait_for_start()
    print("Start Signal")
    
    try:
        
        counts = np.zeros(360, dtype=int)
        
        while True:
            data = lidar.read_lidar_data()
            if data:
                
                #print(f"Speed: {data['speed']} RPM")
                #print(f"Start Angle: {data['start_angle']:.2f}°")
                #print(f"End Angle: {data['end_angle']:.2f}°")
                #print(f"Timestamp: {data['timestamp']}")
                for point in data["scan_data"]:
                    
                    # Ganzzahliger Winkel als array-index
                    winkel = int(point['angle'])%360
                    
                    # wrap around    
                    if winkel == 360:
                        winkel = 0
                        
    
                    lidar.distances[winkel] = point['distance']
    
                
                    #print(f"Angle: {point['angle']:.2f}°, Distance: {point['distance']} mm, Intensity: {point['intensity']}")
                #print("\n---\n")

    except KeyboardInterrupt:
        print("\nStopping Lidar data reading.")
    finally:
        lidar.close()

