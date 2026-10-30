/** Frontend diagnostic contracts: TypeScript only, no runtime dependency. */
export type AgentStatus = "ok" | "error" | "retry" | "accepted" | "rejected" | "revise" | "accept" | "unknown";
export interface TraceEvent {
  sequence: number;
  attempt: number | null;
  agent: string;
  status: string;
  duration_ms: number | null;
  error_type: string | null;
  violations: string[];
}
export interface Observability {
  schema_version: number;
  mode: string;
  accepted: boolean | null;
  event_count: number;
  truncated: boolean;
  agents: Record<string, number>;
  failure_count: number;
  events: TraceEvent[];
  suspected_causes: Array<{ agent:string; attempt:number|null; category:string; error_type:string|null; violations:string[] }>;
}
export interface RunRecord {
  accepted: boolean;
  observability?: Observability;
  run_id?: string;
  trace?: unknown[];
}
