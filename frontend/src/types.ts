export type Coordinate = { x: number; z: number };

export type GridConfig = {
  width: number;
  depth: number;
  obstacles: Coordinate[];
};

export type SimulationEvent = {
  kind: string;
  message: string;
  position: Coordinate;
  planning_time_ms: number | null;
};

export type Simulation = {
  id: string;
  name: string;
  status: string;
  position: Coordinate;
  goal: Coordinate;
  route: Coordinate[];
  route_index: number;
  replans: number;
  events: SimulationEvent[];
};

export type Health = {
  status: "ok";
  version: string;
  offline_mode: boolean;
  project_root: string;
  data_dir: string;
  results_dir: string;
  report_dir: string;
  free_space_gb: number;
};

export type EditMode = "obstacle" | "start" | "goal";

export type ModelCandidate = {
  tag: string;
  family: string;
  approximate_size_mb: number;
  context: string;
  license_summary: string;
  source_url: string;
  rationale: string;
  installed: boolean;
};

export type ModelStatus = {
  ollama_ready: boolean;
  endpoint: string;
  ollama_version: string | null;
  offline_mode: boolean;
  candidates: ModelCandidate[];
  installed_models: Array<Record<string, unknown>>;
};

export type NavigationTask = {
  objective: "navigate" | "unsupported";
  start: Coordinate | null;
  goal: Coordinate | null;
  movement_preference: "shortest" | "safe" | "unspecified";
  avoid_areas: string[];
  replan_on_obstacle: boolean;
  clarification_needed: boolean;
  clarification_reason: string | null;
};

export type InterpretationResult = {
  model: string;
  prompt_version: string;
  task: NavigationTask;
  metrics: {
    wall_time_ms: number;
    total_duration_ms: number | null;
    load_duration_ms: number | null;
    prompt_tokens: number | null;
    generated_tokens: number | null;
    cache_hit: boolean;
  };
  raw_response: string;
};

export type Experiment = {
  id: string;
  name: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  config: Record<string, unknown>;
  results: Array<Record<string, unknown>>;
};

export type BenchmarkJob = {
  id: string;
  status: "queued" | "running" | "completed" | "failed";
  experiment_id: string | null;
  error: string | null;
};

