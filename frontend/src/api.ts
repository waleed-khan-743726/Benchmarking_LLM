import type {
  BenchmarkJob,
  Coordinate,
  Experiment,
  GridConfig,
  Health,
  ModelStatus,
  Simulation
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers }
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = body?.detail ?? `Request failed (${response.status})`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<Health>("/health"),
  models: () => request<ModelStatus>("/api/v1/models"),
  experiments: () => request<Experiment[]>("/api/v1/experiments"),
  startBenchmark: (models: string[], repetitions: number) =>
    request<BenchmarkJob>("/api/v1/benchmarks", {
      method: "POST",
      body: JSON.stringify({ name: "Baseline vs optimized comparison", models, repetitions })
    }),
  benchmarkJob: (id: string) => request<BenchmarkJob>(`/api/v1/benchmarks/jobs/${id}`),
  exportExperiment: (id: string, format: "json" | "csv" | "html" | "pdf") =>
    request<{ format: string; path: string }>(`/api/v1/experiments/${id}/exports/${format}`, {
      method: "POST"
    }),
  createSimulation: (grid: GridConfig, start: Coordinate, goal: Coordinate) =>
    request<Simulation>("/api/v1/simulations", {
      method: "POST",
      body: JSON.stringify({ name: "Interactive arena", grid, start, goal })
    }),
  action: (id: string, action: "plan" | "play" | "pause" | "step" | "reset") =>
    request<Simulation>(`/api/v1/simulations/${id}/actions`, {
      method: "POST",
      body: JSON.stringify({ action })
    }),
  obstacle: (id: string, cell: Coordinate, operation: "add" | "remove") =>
    request<Simulation>(`/api/v1/simulations/${id}/obstacles`, {
      method: "POST",
      body: JSON.stringify({ cell, operation })
    })
};

