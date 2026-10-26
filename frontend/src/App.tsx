import {
  Activity,
  Bot,
  Boxes,
  CircleHelp,
  FlaskConical,
  Gauge,
  LayoutDashboard,
  MapPin,
  Pause,
  Play,
  RefreshCw,
  RotateCcw,
  Settings,
  SkipForward,
  Sparkles,
  SquareStack,
  TriangleAlert
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "./api";
import { Arena3D } from "./components/Arena3D";
import { ResearchSections } from "./components/ResearchSections";
import type { Coordinate, EditMode, Health, Simulation } from "./types";

const INITIAL_OBSTACLES: Coordinate[] = [
  { x: 4, z: 2 }, { x: 4, z: 3 }, { x: 4, z: 4 }, { x: 4, z: 5 },
  { x: 7, z: 5 }, { x: 8, z: 5 }, { x: 9, z: 5 }, { x: 10, z: 5 },
  { x: 9, z: 1 }, { x: 9, z: 2 }, { x: 2, z: 7 }, { x: 3, z: 7 }
];

const sameCell = (a: Coordinate, b: Coordinate) => a.x === b.x && a.z === b.z;

const navigation = [
  ["Overview", LayoutDashboard],
  ["3D Simulator", Boxes],
  ["Model Laboratory", Bot],
  ["Benchmark Studio", FlaskConical],
  ["Results & Analysis", Gauge],
  ["Research Report", SquareStack],
  ["Settings & Help", Settings]
] as const;

export default function App() {
  const [activeSection, setActiveSection] = useState("3D Simulator");
  const [health, setHealth] = useState<Health | null>(null);
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [obstacles, setObstacles] = useState<Coordinate[]>(INITIAL_OBSTACLES);
  const [start, setStart] = useState<Coordinate>({ x: 1, z: 1 });
  const [goal, setGoal] = useState<Coordinate>({ x: 12, z: 8 });
  const [editMode, setEditMode] = useState<EditMode>("obstacle");
  const [speed, setSpeed] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);
  const grid = useMemo(() => ({ width: 14, depth: 10, obstacles }), [obstacles]);

  const run = useCallback(async <T,>(operation: () => Promise<T>): Promise<T | null> => {
    setBusy(true);
    setError(null);
    try {
      return await operation();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "An unexpected error occurred");
      return null;
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
  }, []);

  const createOrReplan = useCallback(async () => {
    const created = await run(() => api.createSimulation(grid, start, goal));
    if (created) setSimulation(created);
  }, [goal, grid, run, start]);

  useEffect(() => {
    void createOrReplan();
  }, []); // Create the initial authoritative scene once.

  const performAction = useCallback(async (action: "play" | "pause" | "step" | "reset") => {
    if (!simulation) return;
    const updated = await run(() => api.action(simulation.id, action));
    if (updated) setSimulation(updated);
  }, [run, simulation]);

  useEffect(() => {
    if (timerRef.current) window.clearInterval(timerRef.current);
    if (simulation?.status === "running") {
      timerRef.current = window.setInterval(() => void performAction("step"), Math.round(700 / speed));
    }
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
    };
  }, [performAction, simulation?.status, speed]);

  const onCellClick = useCallback(async (cell: Coordinate) => {
    if (busy) return;
    if (editMode === "start") {
      if (sameCell(cell, goal) || obstacles.some((item) => sameCell(item, cell))) return;
      setStart(cell);
      setSimulation(null);
      return;
    }
    if (editMode === "goal") {
      if (sameCell(cell, start) || obstacles.some((item) => sameCell(item, cell))) return;
      setGoal(cell);
      setSimulation(null);
      return;
    }
    if (sameCell(cell, start) || sameCell(cell, goal)) return;
    const exists = obstacles.some((item) => sameCell(item, cell));
    if (simulation) {
      const updated = await run(() => api.obstacle(simulation.id, cell, exists ? "remove" : "add"));
      if (!updated) return;
      setSimulation(updated);
    }
    setObstacles((current) => exists
      ? current.filter((item) => !sameCell(item, cell))
      : [...current, cell]);
  }, [busy, editMode, goal, obstacles, run, simulation, start]);

  const pathSteps = simulation ? Math.max(simulation.route.length - 1, 0) : 0;
  const lastEvent = simulation?.events.at(-1);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Bot size={22} /></div>
          <div><strong>NavLab</strong><span>Robot research system</span></div>
        </div>
        <nav aria-label="Primary navigation">
          {navigation.map(([label, Icon]) => (
            <button
              key={label}
              className={activeSection === label ? "nav-item active" : "nav-item"}
              onClick={() => setActiveSection(label)}
            >
              <Icon size={17} /><span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="runtime-card">
          <div className="runtime-title"><Activity size={15} /> Runtime</div>
          <div className="runtime-row"><span>Backend</span><b className={health ? "good" : "warn"}>{health ? "Ready" : "Unavailable"}</b></div>
          <div className="runtime-row"><span>Language model</span><b className="neutral">Offline mode</b></div>
          <small>{health ? `${health.free_space_gb.toFixed(1)} GB free on D:` : "Start the local API to connect."}</small>
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <p className="eyebrow">AUTONOMOUS NAVIGATION WORKSPACE</p>
            <h1>{activeSection}</h1>
          </div>
          <div className="topbar-actions">
            <span className="status-pill"><span className="status-dot" /> Offline development mode</span>
            <button className="icon-button" aria-label="Help"><CircleHelp size={18} /></button>
          </div>
        </header>

        {activeSection === "3D Simulator" ? (
          <div className="simulator-layout">
            <section className="arena-panel">
              <div className="arena-toolbar">
                <div>
                  <span className="section-kicker">LIVE ARENA</span>
                  <h2>Warehouse Grid · 14 × 10</h2>
                </div>
                <div className="segmented" aria-label="Map editing mode">
                  {(["obstacle", "start", "goal"] as EditMode[]).map((mode) => (
                    <button key={mode} className={editMode === mode ? "selected" : ""} onClick={() => setEditMode(mode)}>{mode}</button>
                  ))}
                </div>
              </div>
              <div className="arena-canvas">
                <Arena3D
                  width={grid.width}
                  depth={grid.depth}
                  start={start}
                  goal={goal}
                  obstacles={obstacles}
                  simulation={simulation}
                  editMode={editMode}
                  onCellClick={onCellClick}
                />
                <div className="canvas-hint">Drag to orbit · Scroll to zoom · Click a tile to edit</div>
                <div className="coordinate-readout">
                  <MapPin size={14} /> Robot ({simulation?.position.x ?? start.x}, {simulation?.position.z ?? start.z})
                </div>
              </div>
              <div className="legend">
                <span><i className="legend-dot robot" /> Robot</span>
                <span><i className="legend-dot goal" /> Goal</span>
                <span><i className="legend-dot route" /> Valid route</span>
                <span><i className="legend-dot obstacle" /> Obstacle</span>
              </div>
              <div className="playback">
                <button className="primary-control" onClick={() => performAction("play")} disabled={!simulation || busy}><Play size={16} /> Play</button>
                <button onClick={() => performAction("pause")} disabled={!simulation || busy}><Pause size={16} /> Pause</button>
                <button onClick={() => performAction("step")} disabled={!simulation || busy}><SkipForward size={16} /> Step</button>
                <button onClick={() => performAction("reset")} disabled={!simulation || busy}><RotateCcw size={16} /> Reset</button>
                <label className="speed-control">Speed <input type="range" min="0.5" max="3" step="0.5" value={speed} onChange={(event) => setSpeed(Number(event.target.value))} /><b>{speed.toFixed(1)}×</b></label>
                <span className={`run-state state-${simulation?.status ?? "idle"}`}>{simulation?.status ?? "Connecting"}</span>
              </div>
            </section>

            <aside className="control-panel">
              <div className="panel-heading"><div><span className="section-kicker">MISSION CONTROL</span><h2>Plan a route</h2></div><Sparkles size={18} /></div>
              <label className="field-label" htmlFor="instruction">Natural-language instruction</label>
              <textarea id="instruction" defaultValue="Navigate to the destination using the shortest safe route. Replan if the corridor becomes blocked." />
              <div className="offline-note"><TriangleAlert size={16} /><div><b>LLM is offline</b><span>The deterministic route planner remains fully available. Offline runs are never counted as model results.</span></div></div>
              <button className="calculate-button" onClick={createOrReplan} disabled={busy}><RefreshCw size={17} className={busy ? "spin" : ""} /> {busy ? "Working…" : "Calculate valid route"}</button>
              {error && <div className="error-box" role="alert">{error}</div>}
              <div className="metrics-grid">
                <div><span>Path length</span><b>{pathSteps || "—"}</b><small>grid moves</small></div>
                <div><span>Route progress</span><b>{simulation ? `${simulation.route_index}/${pathSteps}` : "—"}</b><small>completed steps</small></div>
                <div><span>Replans</span><b>{simulation?.replans ?? 0}</b><small>safe route updates</small></div>
                <div><span>Obstacles</span><b>{obstacles.length}</b><small>blocked cells</small></div>
              </div>
              <div className="event-card">
                <div className="event-title"><Activity size={15} /> Latest system event</div>
                <p>{lastEvent?.message ?? "Waiting for the first verified plan."}</p>
                {lastEvent?.planning_time_ms != null && <small>A* completed in {lastEvent.planning_time_ms.toFixed(3)} ms</small>}
              </div>
              <div className="coordinate-card">
                <div><span>Start</span><b>({start.x}, {start.z})</b></div>
                <div><span>Goal</span><b>({goal.x}, {goal.z})</b></div>
              </div>
            </aside>
          </div>
        ) : <ResearchSections section={activeSection} health={health} openSimulator={() => setActiveSection("3D Simulator")} />}
      </main>
    </div>
  );
}

