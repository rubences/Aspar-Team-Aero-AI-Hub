import json
import time
import random
import numpy as np
from confluent_kafka import Producer
import threading

class BikeTelemetrySimulator:
    """
    High-fidelity Digital Twin simulator for Aspar Team motorcycles.
    Supports 1000Hz (1ms) sampling and lattice-based noise injection.
    """
    def __init__(self, bootstrap_servers: str = "localhost:9092", topic: str = "telemetry.raw"):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.topic = topic
        self.running = True
        self.anomaly_active = False
        self.frequency = 1000 # Hz
        self.bike_id = "ASPAR-AERO-01"
        
        # Simple identity lattice for noise injection
        self.lattice_basis = np.eye(3) 

    def _inject_lattice_noise(self, vector: np.ndarray) -> np.ndarray:
        """
        Simulates quantization noise by adding a perturbation 
        and then 'snapping' to a simulated sensor lattice.
        """
        noise = np.random.normal(0, 0.05, vector.shape)
        perturbed = vector + noise
        # Quantize to nearest 0.1 (simulated sensor precision)
        return np.round(perturbed / 0.1) * 0.1

    def toggle_anomaly(self):
        self.anomaly_active = not self.anomaly_active
        status = "ACTIVE" if self.anomaly_active else "DEACTIVATED"
        print(f"\n[SIMULATOR] Aerodynamic Anomaly: {status}")

    def generate_telemetry(self):
        """
        Main loop producing 1000 messages per second.
        """
        print(f"Starting simulation at {self.frequency}Hz on topic '{self.topic}'...")
        print("Press 'a' then Enter to toggle Anomaly, 'q' to Quit.")
        
        start_time = time.time()
        count = 0
        
        while self.running:
            t = time.time() - start_time
            
            # 1. Base Signal (Sinusoidal)
            rpm = 12000 + 2000 * np.sin(t * 2)
            temp = 90 + 5 * np.sin(t * 0.5)
            rake = 1.2 + 0.1 * np.sin(t * 1)
            
            # 2. Apply Anomaly (Critical rake drop / Temperature spike)
            if self.anomaly_active:
                rake -= 0.8 # Simulated Stall/Drag increase
                temp += 15  # Simulated Overheat
            
            # 3. Lattice Noise & Quantization
            raw_vec = np.array([rpm, temp, rake])
            quantized_vec = self._inject_lattice_noise(raw_vec)
            
            # 4. Prepare Payload
            payload = {
                "bike_id": self.bike_id,
                "timestamp": t,
                "sensors": {
                    "rpm": float(quantized_vec[0]),
                    "temp": float(quantized_vec[1]),
                    "rake": float(quantized_vec[2])
                },
                "meta": {"freq": self.frequency, "anomaly": self.anomaly_active}
            }
            
            # 5. Send to Kafka
            self.producer.produce(self.topic, json.dumps(payload).encode('utf-8'))
            
            count += 1
            if count % 1000 == 0:
                self.producer.flush()
                # print(f"Sent {count} messages...")

            # Maintain 1000Hz (approximate)
            time.sleep(1.0 / self.frequency)

    def stop(self):
        self.running = False

def input_listener(sim):
    while sim.running:
        cmd = input().lower()
        if cmd == 'a':
            sim.toggle_anomaly()
        elif cmd == 'q':
            sim.stop()
            break

if __name__ == "__main__":
    sim = BikeTelemetrySimulator()
    
    # Run input listener in a separate thread
    threading.Thread(target=input_listener, args=(sim,), daemon=True).start()
    
    try:
        sim.generate_telemetry()
    except KeyboardInterrupt:
        sim.stop()
    print("Simulation stopped.")
