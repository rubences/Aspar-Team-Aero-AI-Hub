/**
 * Viewport3D — 3D aerodynamic flow visualiser.
 * Renders CFD mesh geometries and flow field visualisations using Three.js.
 */

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

const Viewport3D = ({ meshData = null, flowData = null, title = "Aerodynamic Flow Visualiser" }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const frameRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({ vertices: 0, faces: 0 });

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e1a);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      60,
      mount.clientWidth / mount.clientHeight,
      0.01,
      100
    );
    camera.position.set(2, 1.5, 2.5);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    mount.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Orbit controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404060, 0.6);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 10, 7);
    scene.add(dirLight);

    // Grid helper
    const grid = new THREE.GridHelper(4, 20, 0x1e3a5f, 0x0d1f3c);
    scene.add(grid);

    // Axes helper
    const axes = new THREE.AxesHelper(0.5);
    scene.add(axes);

    // Render provided mesh or a default placeholder
    if (meshData && meshData.vertices && meshData.faces) {
      const geometry = new THREE.BufferGeometry();
      const vertices = new Float32Array(meshData.vertices.flat());
      const indices = meshData.faces.flat();
      geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));
      geometry.setIndex(indices);
      geometry.computeVertexNormals();

      const material = new THREE.MeshPhongMaterial({
        color: 0x1e88e5,
        wireframe: false,
        transparent: true,
        opacity: 0.8,
        side: THREE.DoubleSide,
      });
      const mesh = new THREE.Mesh(geometry, material);
      scene.add(mesh);

      // Wireframe overlay
      const wireMat = new THREE.MeshBasicMaterial({ color: 0x60a5fa, wireframe: true, transparent: true, opacity: 0.3 });
      const wireMesh = new THREE.Mesh(geometry.clone(), wireMat);
      scene.add(wireMesh);

      setStats({ vertices: meshData.vertices.length, faces: meshData.faces.length });
    } else {
      // Placeholder wing geometry
      const wingGeometry = new THREE.BoxGeometry(2.0, 0.05, 0.4);
      const wingMaterial = new THREE.MeshPhongMaterial({
        color: 0xcc2222,
        specular: 0x444444,
        shininess: 30,
      });
      const wing = new THREE.Mesh(wingGeometry, wingMaterial);
      scene.add(wing);

      // Flow arrows (placeholder)
      const arrowDir = new THREE.Vector3(1, -0.1, 0).normalize();
      for (let i = -5; i <= 5; i++) {
        const arrow = new THREE.ArrowHelper(
          arrowDir,
          new THREE.Vector3(-3, 0.2 + i * 0.02, i * 0.06),
          0.8,
          0x00d4ff,
          0.15,
          0.08
        );
        scene.add(arrow);
      }
      setStats({ vertices: 8, faces: 12 });
    }

    setIsLoading(false);

    // Animation loop
    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      if (!mount) return;
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(frameRef.current);
      mount.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, [meshData]);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        minHeight: 400,
        background: "#0a0e1a",
        borderRadius: 8,
        overflow: "hidden",
      }}
    >
      {/* Header overlay */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 10,
          padding: "10px 16px",
          background: "rgba(10,14,26,0.8)",
          color: "#f9fafb",
          fontSize: 13,
          fontFamily: "monospace",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #1e3a5f",
        }}
      >
        <span style={{ fontWeight: 700, color: "#60a5fa" }}>🌐 {title}</span>
        <span style={{ color: "#6b7280", fontSize: 11 }}>
          {stats.vertices.toLocaleString()} vertices · {stats.faces.toLocaleString()} faces
        </span>
      </div>

      {/* 3D viewport */}
      <div ref={mountRef} style={{ width: "100%", height: "100%" }} />

      {isLoading && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#60a5fa",
            fontSize: 14,
            fontFamily: "monospace",
          }}
        >
          Initialising 3D viewport...
        </div>
      )}

      {/* Legend overlay */}
      <div
        style={{
          position: "absolute",
          bottom: 12,
          left: 12,
          zIndex: 10,
          background: "rgba(10,14,26,0.8)",
          padding: "8px 12px",
          borderRadius: 6,
          color: "#9ca3af",
          fontSize: 11,
          fontFamily: "monospace",
        }}
      >
        🖱 Drag to orbit · Scroll to zoom · Right-click to pan
      </div>
    </div>
  );
};

export default Viewport3D;
