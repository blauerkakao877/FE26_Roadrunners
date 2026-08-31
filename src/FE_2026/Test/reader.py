import time
import random
import numpy as np
from multiprocessing import shared_memory

ARRAY_SIZE = 360
SHM_NAME = "lidar_distances"

def wait_for_shm():
    while True:
        try:
            return shared_memory.SharedMemory(name=SHM_NAME)
        except FileNotFoundError:
            print("Waiting for writer...")
            time.sleep(0.1)

def main():
    shm = wait_for_shm()
    distances = np.ndarray((ARRAY_SIZE,), dtype=np.float32, buffer=shm.buf)

    try:
        while True:
            angle = random.randint(0, ARRAY_SIZE - 1)
            value = distances[angle]
            print(f"[Reader] angle={angle}, value={value:.2f}")
            time.sleep(0.1)
    finally:
        shm.close()

if __name__ == "__main__":
    main()
