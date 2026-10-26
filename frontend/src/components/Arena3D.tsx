import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { memo } from "react";
import type { Coordinate, EditMode, Simulation } from "../types";

type ArenaProps = {
  width: number;
  depth: number;
  start: Coordinate;
  goal: Coordinate;
  obstacles: Coordinate[];
  simulation: Simulation | null;
  editMode: EditMode;
  onCellClick: (cell: Coordinate) => void;
};

const key = (cell: Coordinate) => `${cell.x}:${cell.z}`;

function Robot({ cell }: { cell: Coordinate }) {
  return (
    <group position={[cell.x, 0.55, cell.z]}>
      <mesh castShadow position={[0, 0.1, 0]}>
        <boxGeometry args={[0.64, 0.35, 0.76]} />
        <meshStandardMaterial color="#e9f2ee" roughness={0.35} metalness={0.35} />
      </mesh>
      <mesh castShadow position={[0, 0.42, 0.08]}>
        <boxGeometry args={[0.46, 0.28, 0.42]} />
        <meshStandardMaterial color="#d8e7e1" roughness={0.3} metalness={0.4} />
      </mesh>
      <mesh position={[0, 0.45, -0.145]}>
        <boxGeometry args={[0.24, 0.09, 0.04]} />
        <meshStandardMaterial color="#39d4a0" emissive="#17664f" emissiveIntensity={0.8} />
      </mesh>
      {[-0.34, 0.34].map((x) => (
        <mesh key={x} castShadow position={[x, 0, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.17, 0.17, 0.12, 16]} />
          <meshStandardMaterial color="#1b2422" roughness={0.8} />
        </mesh>
      ))}
    </group>
  );
}

const ArenaScene = memo(function ArenaScene(props: ArenaProps) {
  const obstacleKeys = new Set(props.obstacles.map(key));
  const routeKeys = new Set((props.simulation?.route ?? []).map(key));
  const robot = props.simulation?.position ?? props.start;
  const centerX = (props.width - 1) / 2;
  const centerZ = (props.depth - 1) / 2;

  return (
    <>
      <color attach="background" args={["#0c1211"]} />
      <fog attach="fog" args={["#0c1211", 15, 38]} />
      <ambientLight intensity={0.95} />
      <directionalLight castShadow position={[8, 14, 6]} intensity={2.1} color="#e8fff5" />
      <group position={[-centerX, 0, -centerZ]}>
        {Array.from({ length: props.width * props.depth }, (_, index) => {
          const cell = { x: index % props.width, z: Math.floor(index / props.width) };
          const cellKey = key(cell);
          const blocked = obstacleKeys.has(cellKey);
          const onRoute = routeKeys.has(cellKey);
          const isStart = key(props.start) === cellKey;
          const isGoal = key(props.goal) === cellKey;
          const color = isGoal
            ? "#e7b65c"
            : isStart
              ? "#52a7d8"
              : onRoute
                ? "#287a64"
                : (cell.x + cell.z) % 2
                  ? "#17201e"
                  : "#1b2523";
          return (
            <group key={cellKey} position={[cell.x, 0, cell.z]}>
              <mesh
                receiveShadow
                position={[0, -0.08, 0]}
                onClick={(event) => {
                  event.stopPropagation();
                  props.onCellClick(cell);
                }}
              >
                <boxGeometry args={[0.94, 0.12, 0.94]} />
                <meshStandardMaterial color={color} roughness={0.88} />
              </mesh>
              {blocked && (
                <mesh castShadow position={[0, 0.45, 0]}>
                  <boxGeometry args={[0.72, 0.86, 0.72]} />
                  <meshStandardMaterial color="#a95c52" roughness={0.55} />
                </mesh>
              )}
              {isGoal && !blocked && (
                <mesh position={[0, 0.22, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                  <torusGeometry args={[0.28, 0.06, 12, 28]} />
                  <meshStandardMaterial color="#ffd481" emissive="#8d5f16" emissiveIntensity={0.7} />
                </mesh>
              )}
              {onRoute && !blocked && !isGoal && (
                <mesh position={[0, 0.045, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                  <circleGeometry args={[0.12, 16]} />
                  <meshBasicMaterial color="#61dbb0" />
                </mesh>
              )}
            </group>
          );
        })}
        <Robot cell={robot} />
      </group>
      <gridHelper args={[Math.max(props.width, props.depth) + 8, Math.max(props.width, props.depth) + 8, "#31413d", "#18221f"]} position={[0, -0.16, 0]} />
      <OrbitControls
        makeDefault
        target={[0, 0, 0]}
        minDistance={5}
        maxDistance={28}
        maxPolarAngle={Math.PI / 2.05}
        enableDamping
      />
    </>
  );
});

export function Arena3D(props: ArenaProps) {
  return (
    <Canvas
      shadows
      dpr={[1, 1.5]}
      camera={{ position: [9, 11, 12], fov: 42, near: 0.1, far: 100 }}
      gl={{ antialias: true, powerPreference: "high-performance" }}
    >
      <ArenaScene {...props} />
    </Canvas>
  );
}

