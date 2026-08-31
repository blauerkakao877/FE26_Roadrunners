import time
import random
import numpy as np
from multiprocessing import shared_memory

ARRAY_SIZE = 360
SHM_NAME = "lidar_distances"

def main():
    try:
        shm = shared_memory.SharedMemory(
            name=SHM_NAME,
            create=True,
            size=ARRAY_SIZE * 4  # float32 = 4 Bytes
        )
        print("Shared memory created")
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=SHM_NAME)
        print("Shared memory attached")

    distances = np.ndarray(
        (ARRAY_SIZE,),
        dtype=np.float32,
        buffer=shm.buf
    )

    # Initialisieren
    distances[:] = 0.0

    try:
        while True:
            angle = random.randint(0, ARRAY_SIZE - 1)
            value = random.uniform(0.1, 5.0)

            distances[angle] = value
            print(f"[Writer] angle={angle:3d}, value={value:.2f}")

            time.sleep(0.05)  # ~20 Hz
    except KeyboardInterrupt:
        print("Writer stopping...")
    finally:
        shm.close()
        shm.unlink()  # nur EIN Prozess darf unlinken!

if __name__ == "__main__":
    main()
