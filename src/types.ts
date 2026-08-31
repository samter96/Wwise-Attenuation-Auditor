export type Language = "ko" | "en";
export type ConnectionState = "connecting" | "connected" | "error";
export type AuditState = "idle" | "scanning" | "complete" | "error";
export type Issue = "miss" | "extra";

export interface AuditResult {
  id: string;
  name: string;
  type: string;
  spat: string;
  att: string;
  issue: Issue;
  wu: string;
  path: string;
}

export interface ScopeNode {
  id: string;
  name: string;
  path: string;
  type: string;
  expandable: boolean;
  loaded?: boolean;
  loading?: boolean;
  expanded?: boolean;
  children?: ScopeNode[];
}

export interface ScanResponse {
  results: AuditResult[];
  totalChecked: number;
  exceptions: AuditResult[];
  invalidated: string[];
}
