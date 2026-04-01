import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const Viewport3D = () => {
  const mountRef = useRef(null);

  useEffect(() => {
    // 1. Scene Setup
    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050a14);

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(5, 3, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    // 2. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0x00ecff, 1);
    directionalLight.position.set(10, 10, 10);
    scene.add(directionalLight);

    // 3. Motorcycle Placeholder (Procedural)
    const bikeGroup = new THREE.Group();
    
    // Main Body
    const bodyGeo = new THREE.BoxGeometry(3, 1, 0.8);
    const bodyMat = new THREE.MeshPhongMaterial({ color: 0x112240, wireframe: true });
    const mainBody = new THREE.Mesh(bodyGeo, bodyMat);
    bikeGroup.add(mainBody);
    
    // Wheels
    const wheelGeo = new THREE.TorusGeometry(0.5, 0.2, 16, 100);
    const wheelMat = new THREE.MeshPhongMaterial({ color: 0x00ecff });
    const frontWheel = new THREE.Mesh(wheelGeo, wheelMat);
    frontWheel.position.set(1.5, -0.5, 0);
    bikeGroup.add(frontWheel);
    
    const backWheel = new THREE.Mesh(wheelGeo, wheelMat);
    backWheel.position.set(-1.5, -0.5, 0);
    bikeGroup.add(backWheel);
    
    scene.add(bikeGroup);

    // 4. Aero Flow Particle System
    const particleCount = 1000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
      positions[i*3] = (Math.random() - 0.5) * 10;
      positions[i*3 + 1] = Math.random() * 2;
      positions[i*3 + 2] = (Math.random() - 0.5) * 3;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({ color: 0x00ecff, size: 0.05, transparent: true, opacity: 0.4 });
    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // 5. Animation Loop
    const animate = () => {
      requestAnimationFrame(animate);
      
      // Update Particles (Simulate Flow)
      const pos = geometry.attributes.position.array;
      for (let i = 0; i < particleCount; i++) {
        pos[i*3] -= 0.1; // Move against X axis (air flow)
        if (pos[i*3] < -5) pos[i*3] = 5;
      }
      geometry.attributes.position.needsUpdate = true;
      
      // Dynamic pitch (from simulated 'Rake')
      bikeGroup.rotation.z = Math.sin(Date.now() * 0.001) * 0.05;
      
      renderer.render(scene, camera);
    };

    animate();

    // 6. Responsive Handling
    const handleResize = () => {
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      renderer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div className="viewport-3d-container" ref={mountRef} style={{ width: '100%', height: '500px' }}>
      <div className="viewport-overlay" style={{ pointerEvents: 'none' }}>
        <span>MODO: PINN Real-Time Flow</span>
        <span>FPS: 60</span>
        <span>PARTÍCULAS: 1000</span>
      </div>
    </div>
  );
};

export default Viewport3D;
