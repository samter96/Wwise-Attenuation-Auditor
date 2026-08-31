import { invoke } from "@tauri-apps/api/core";
import type { AuditResult, ScopeNode } from "./types";

const isTauri = () => "__TAURI_INTERNALS__" in window;

const demoResults: AuditResult[] = [
  {
    id: "demo-river",
    name: "AMB_River_Wide_Loop",
    type: "Sound",
    spat: "Position",
    att: "—",
    issue: "miss",
    wu: "Ambience",
    path: "\\Actor-Mixer Hierarchy\\Default Work Unit\\AMB\\River\\AMB_River_Wide_Loop",
  },
  {
    id: "demo-ui",
    name: "UI_Notification_Confirm",
    type: "Sound",
    spat: "None",
    att: "ATT_Generic_Medium",
    issue: "extra",
    wu: "UI",
    path: "\\Actor-Mixer Hierarchy\\Default Work Unit\\UI\\UI_Notification_Confirm",
  },
  {
    id: "demo-vehicle",
    name: "VEH_Engine_Player",
    type: "BlendContainer",
    spat: "Position + Orientation",
    att: "—",
    issue: "miss",
    wu: "Vehicles",
    path: "\\Actor-Mixer Hierarchy\\Default Work Unit\\Vehicles\\VEH_Engine_Player",
  },
];

const demoScope: ScopeNode[] = [
  { id: "wu-default", name: "Default Work Unit", path: "\\Actor-Mixer Hierarchy\\Default Work Unit", type: "WorkUnit", expandable: true },
  { id: "wu-music", name: "DX_MUSIC", path: "\\Actor-Mixer Hierarchy\\DX_MUSIC", type: "WorkUnit", expandable: true },
  { id: "wu-sound", name: "DX_SOUND", path: "\\Actor-Mixer Hierarchy\\DX_SOUND", type: "WorkUnit", expandable: true },
  { id: "wu-test", name: "DX_SOUND_TEST", path: "\\Actor-Mixer Hierarchy\\DX_SOUND_TEST", type: "WorkUnit", expandable: true },
];

let demoExceptions: AuditResult[] = [];
let demoCurrentResults = [...demoResults];

async function demoRequest<T>(command: string, payload: Record<string, unknown>): Promise<T> {
  await new Promise((resolve) => setTimeout(resolve, command === "scan" ? 1300 : 180));
  switch (command) {
    case "ping":
      return { version: "V.2.0.0", ready: true } as T;
    case "connect":
      return { connected: true, projectName: "DX_Wwise", exceptionCount: demoExceptions.length } as T;
    case "status":
      return { connected: true, projectName: "DX_Wwise" } as T;
    case "scope_children":
      return { path: payload.path, children: demoScope } as T;
    case "scan":
      demoCurrentResults = [...demoResults];
      return { results: demoCurrentResults, totalChecked: 847, exceptions: demoExceptions, invalidated: [] } as T;
    case "get_exceptions":
      return { exceptions: demoExceptions } as T;
    case "add_exceptions": {
      const ids = new Set((payload.ids as string[]) ?? []);
      const added = demoCurrentResults.filter((result) => ids.has(result.id));
      demoExceptions = [...demoExceptions, ...added];
      demoCurrentResults = demoCurrentResults.filter((result) => !ids.has(result.id));
      return { results: demoCurrentResults, exceptions: demoExceptions, totalChecked: 847 } as T;
    }
    case "remove_exceptions": {
      const ids = new Set((payload.ids as string[]) ?? []);
      demoExceptions = demoExceptions.filter((result) => !ids.has(result.id));
      return { exceptions: demoExceptions } as T;
    }
    case "select_in_wwise":
      return { selected: payload.ids } as T;
    case "export_csv":
      return { path: payload.path, count: demoCurrentResults.length } as T;
    default:
      throw new Error(`Unknown demo command: ${command}`);
  }
}

export async function backendRequest<T>(
  command: string,
  payload: Record<string, unknown> = {},
): Promise<T> {
  if (!isTauri()) return demoRequest<T>(command, payload);
  return invoke<T>("backend_request", { command, payload });
}

export { isTauri };
