import {
  Activity,
  Bot,
  CheckCircle2,
  Database,
  Download,
  FlaskConical,
  HardDrive,
  Info,
  Play,
  Server,
  ShieldCheck,
  TriangleAlert
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { BenchmarkJob, Experiment, Health, ModelStatus } from "../types";

type Props = {
  section: string;
  health: Health | null;
  openSimulator: () => void;
};

function SectionHeader({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <div className="research-header"><span className="section-kicker">{eyebrow}</span><h2>{title}</h2><p>{description}</p></div>;
}

type ResultSummary = { key: string; model: string; prompt: string; runs: number; successes: number; meanLatency: number; meanPath: number; cacheHits: number };

function summarize(experiment: Experiment | undefined): ResultSummary[] {
  if (!experiment) return [];
  const groups = new Map<string, Array<Record<string, unknown>>>();
  for (const row of experiment.results) {
    const key = `${String(row.model)}|${String(row.prompt_mode)}`;
    groups.set(key, [...(groups.get(key) ?? []), row]);
  }
  return [...groups.entries()].map(([key, rows]) => {
    const numeric = (field: string) => rows
      .map((row) => row[field])
      .filter((value) => value !== null && value !== undefined)
      .map(Number)
      .filter(Number.isFinite);
    const latency = numeric("wall_time_ms");
    const paths = numeric("path_length");
    return {
      key, model: String(rows[0].model), prompt: String(rows[0].prompt_mode), runs: rows.length,
      successes: rows.filter((row) => row.success === true).length,
      meanLatency: latency.length ? latency.reduce((sum, value) => sum + value, 0) / latency.length : 0,
      meanPath: paths.length ? paths.reduce((sum, value) => sum + value, 0) / paths.length : 0,
      cacheHits: rows.filter((row) => row.cache_hit === true).length
    };
  });
}

export function ResearchSections({ section, health, openSimulator }: Props) {
  const [models, setModels] = useState<ModelStatus | null>(null);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [job, setJob] = useState<BenchmarkJob | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = () => {
    api.models().then((value) => {
      setModels(value);
      setSelectedModels((current) => current.length ? current : value.candidates.filter((item) => item.installed).map((item) => item.tag));
    }).catch(() => setModels(null));
    api.experiments().then(setExperiments).catch(() => setExperiments([]));
  };

  useEffect(refresh, [section]);
  useEffect(() => {
    if (!job || !["queued", "running"].includes(job.status)) return;
    const timer = window.setInterval(() => {
      api.benchmarkJob(job.id).then((next) => {
        setJob(next);
        if (next.status === "completed" || next.status === "failed") refresh();
      }).catch(() => undefined);
    }, 900);
    return () => window.clearInterval(timer);
  }, [job]);

  const totalRuns = useMemo(() => experiments.reduce((sum, item) => sum + item.results.length, 0), [experiments]);
  const latestSummary = useMemo(() => summarize(experiments[0]), [experiments]);

  const exportLatest = async (format: "json" | "csv" | "html" | "pdf") => {
    const latest = experiments[0];
    if (!latest) return;
    const result = await api.exportExperiment(latest.id, format);
    setMessage(`Created ${format.toUpperCase()} at ${result.path}`);
  };

  if (section === "Overview") return (
    <div className="research-page">
      <SectionHeader eyebrow="RESEARCH OVERVIEW" title="Language in. Validated movement out." description="A local language model interprets intent; deterministic A* owns every movement decision." />
      <div className="hero-workflow"><div><span>01</span><Bot /><b>Interpret</b><p>Convert ordinary language into a strict task schema.</p></div><div><span>02</span><ShieldCheck /><b>Plan & validate</b><p>Calculate a legal route and independently inspect every step.</p></div><div><span>03</span><Activity /><b>Simulate & measure</b><p>Move, replan, and preserve evidence for comparison.</p></div></div>
      <div className="overview-grid">
        <article><Server /><span>Backend</span><b>{health ? "Ready" : "Unavailable"}</b><small>FastAPI {health?.version ?? "—"}</small></article>
        <article><Bot /><span>Ollama</span><b>{models?.ollama_ready ? "Ready" : "Offline"}</b><small>{models?.installed_models.length ?? 0} local models detected</small></article>
        <article><Database /><span>Recorded evidence</span><b>{totalRuns}</b><small>benchmark observations</small></article>
        <article><HardDrive /><span>Project drive</span><b>{health ? `${health.free_space_gb.toFixed(1)} GB` : "—"}</b><small>free on D:</small></article>
      </div>
      <button className="section-primary" onClick={openSimulator}><Play size={16} /> Open 3D simulator</button>
    </div>
  );

  if (section === "Model Laboratory") return (
    <div className="research-page">
      <SectionHeader eyebrow="MODEL LABORATORY" title="Local model readiness" description="Candidates are listed from verified Ollama tags. Installed and benchmark-ready are separate states." />
      <div className={`readiness-banner ${models?.ollama_ready ? "ready" : "offline"}`}><span>{models?.ollama_ready ? <CheckCircle2 /> : <TriangleAlert />}</span><div><b>{models?.ollama_ready ? "Ollama is reachable" : "Ollama is not running"}</b><p>{models?.ollama_ready ? `Connected to ${models.endpoint}` : "The simulator remains available. No model result will be invented or shown as ready."}</p></div></div>
      <div className="model-grid">{models?.candidates.map((model) => <article key={model.tag}><div className="model-card-head"><Bot /><span className={model.installed ? "tag installed" : "tag"}>{model.installed ? "Installed" : "Not installed"}</span></div><h3>{model.family}</h3><code>{model.tag}</code><p>{model.rationale}</p><dl><div><dt>Download</dt><dd>≈ {model.approximate_size_mb} MB</dd></div><div><dt>Context</dt><dd>{model.context}</dd></div></dl><a href={model.source_url} target="_blank" rel="noreferrer">{model.license_summary} · official model page</a></article>)}</div>
    </div>
  );

  if (section === "Benchmark Studio") return (
    <div className="research-page">
      <SectionHeader eyebrow="BENCHMARK STUDIO" title="Baseline versus optimized" description="Models run sequentially against the same versioned scenarios. Failures stay in the evidence." />
      <div className="benchmark-card"><h3>Experiment configuration</h3><p>2 versioned scenarios · baseline + optimized prompts · sequential execution</p><div className="check-list">{models?.candidates.map((model) => <label key={model.tag}><input type="checkbox" checked={selectedModels.includes(model.tag)} onChange={() => setSelectedModels((current) => current.includes(model.tag) ? current.filter((item) => item !== model.tag) : [...current, model.tag])} /> <span>{model.tag}</span><i>{model.installed ? "installed" : "missing"}</i></label>)}</div><button className="section-primary" disabled={!models?.ollama_ready || !selectedModels.length || job?.status === "running"} onClick={() => api.startBenchmark(selectedModels, 3).then(setJob)}><FlaskConical size={16} /> {job?.status === "running" ? "Benchmark running…" : "Run verified benchmark"}</button>{!models?.ollama_ready && <div className="inline-note"><Info size={15} /> Start Ollama and install selected models before running. The button is intentionally disabled.</div>}{job && <p className="job-state">Job {job.id.slice(0, 8)} · {job.status}{job.error ? ` · ${job.error}` : ""}</p>}</div>
    </div>
  );

  if (section === "Results & Analysis") return (
    <div className="research-page">
      <SectionHeader eyebrow="RESULTS & ANALYSIS" title="Stored experimental evidence" description="Historical runs remain available after restart. Empty state is evidence too." />
      {!experiments.length ? <div className="no-evidence"><Database /><h3>No benchmark evidence yet</h3><p>Run a real local-model experiment to populate comparisons. Deterministic tests are kept separate.</p></div> : <>
        <div className="analysis-grid">{latestSummary.map((group) => { const rate = group.runs ? (group.successes / group.runs) * 100 : 0; return <article key={group.key}><div className="analysis-head"><div><b>{group.model}</b><span>{group.prompt} prompt</span></div><strong>{rate.toFixed(0)}%</strong></div><div className="bar"><i style={{ width: `${rate}%` }} /></div><dl><div><dt>Verified success</dt><dd>{group.successes}/{group.runs}</dd></div><div><dt>Mean wall latency</dt><dd>{group.meanLatency.toFixed(0)} ms</dd></div><div><dt>Mean path</dt><dd>{group.meanPath.toFixed(1)} moves</dd></div><div><dt>Cache hits</dt><dd>{group.cacheHits}</dd></div></dl></article>; })}</div>
        <h3 className="history-title">Experiment history</h3>
        <div className="experiment-list">{experiments.map((item) => <article key={item.id}><div><b>{item.name}</b><span>{new Date(item.created_at).toLocaleString()}</span></div><div><strong>{item.results.length}</strong><span>recorded runs</span></div><span className={`tag ${item.status}`}>{item.status}</span></article>)}</div>
      </>}
    </div>
  );

  if (section === "Research Report") return (
    <div className="research-page">
      <SectionHeader eyebrow="RESEARCH REPORT" title="Evidence-based exports" description="Exports are generated from SQLite records. With no run, the system produces no unsupported finding." />
      <div className="export-card"><Download /><h3>{experiments.length ? experiments[0].name : "No experiment selected"}</h3><p>{experiments.length ? `${experiments[0].results.length} raw observations available.` : "Complete a real benchmark before exporting findings."}</p><div><button disabled={!experiments.length} onClick={() => exportLatest("json")}>Export JSON</button><button disabled={!experiments.length} onClick={() => exportLatest("csv")}>Export CSV</button><button disabled={!experiments.length} onClick={() => exportLatest("html")}>HTML report</button><button disabled={!experiments.length} onClick={() => exportLatest("pdf")}>PDF report</button></div>{message && <small>{message}</small>}</div>
    </div>
  );

  return (
    <div className="research-page">
      <SectionHeader eyebrow="SETTINGS & HELP" title="Runtime and storage" description="All project-specific state is configured beneath D:\Robot_Navigation_FYP." />
      <div className="settings-list"><div><span>Project root</span><code>{health?.project_root ?? "Unavailable"}</code></div><div><span>Model storage</span><code>D:\Robot_Navigation_FYP\models\ollama</code></div><div><span>Experiment database</span><code>D:\Robot_Navigation_FYP\backend\data\experiments.db</code></div><div><span>Reports</span><code>{health?.report_dir ?? "Unavailable"}</code></div><div><span>Ollama runtime</span><code>{models?.ollama_version ? `v${models.ollama_version}` : "Unavailable"}</code></div><div><span>Ollama endpoint</span><code>{models?.endpoint ?? "http://127.0.0.1:11434"}</code></div></div>
    </div>
  );
}

