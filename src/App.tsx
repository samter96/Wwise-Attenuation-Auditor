import { useCallback, useEffect, useMemo, useState } from "react";
import { save } from "@tauri-apps/plugin-dialog";
import { AlertTriangle, Check, CircleHelp, LoaderCircle, Radar, ScanSearch, Volume2, X } from "lucide-react";
import { backendRequest, isTauri } from "./bridge";
import { copy } from "./i18n";
import type { AuditResult, AuditState, ConnectionState, Language, ScanResponse, ScopeNode } from "./types";
import AttenuationOrbit from "./components/AttenuationOrbit";
import ResultsTable from "./components/ResultsTable";
import ScopeTree from "./components/ScopeTree";
import WindowChrome from "./components/WindowChrome";
import PrecisionCheck from "./components/PrecisionCheck";

function updateNode(nodes: ScopeNode[], path: string, updater: (node: ScopeNode) => ScopeNode): ScopeNode[] {
  return nodes.map((node) => {
    if (node.path === path) return updater(node);
    if (!node.children) return node;
    return { ...node, children: updateNode(node.children, path, updater) };
  });
}

export default function App() {
  const [language, setLanguage] = useState<Language>("ko");
  const [connection, setConnection] = useState<ConnectionState>("connecting");
  const [projectName, setProjectName] = useState("");
  const [auditState, setAuditState] = useState<AuditState>("idle");
  const [results, setResults] = useState<AuditResult[]>([]);
  const [exceptions, setExceptions] = useState<AuditResult[]>([]);
  const [totalChecked, setTotalChecked] = useState(0);
  const [scopeNodes, setScopeNodes] = useState<ScopeNode[]>([]);
  const [selectedPaths, setSelectedPaths] = useState<Set<string>>(new Set());
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [includeSounds, setIncludeSounds] = useState(true);
  const [includeContainers, setIncludeContainers] = useState(true);
  const [activeTab, setActiveTab] = useState<"violations" | "exceptions">("violations");
  const [message, setMessage] = useState<{ tone: "error" | "success"; text: string } | null>(null);
  const [helpOpen, setHelpOpen] = useState(false);
  const t = copy(language);

  const showMessage = useCallback((tone: "error" | "success", text: string) => {
    setMessage({ tone, text });
    window.setTimeout(() => setMessage(null), 3600);
  }, []);

  const loadRootScope = useCallback(async () => {
    const data = await backendRequest<{ children: ScopeNode[] }>("scope_children", { path: "\\Actor-Mixer Hierarchy" });
    setScopeNodes(data.children);
  }, []);

  const connect = useCallback(async () => {
    setConnection("connecting");
    try {
      const data = await backendRequest<{ connected: boolean; projectName: string }>("connect");
      setConnection(data.connected ? "connected" : "error");
      setProjectName(data.projectName);
      await loadRootScope();
      const exceptionData = await backendRequest<{ exceptions: AuditResult[] }>("get_exceptions");
      setExceptions(exceptionData.exceptions);
    } catch (error) {
      setConnection("error");
      setProjectName("");
      showMessage("error", error instanceof Error ? error.message : String(error));
    }
  }, [loadRootScope, showMessage]);

  useEffect(() => { void connect(); }, [connect]);

  const toggleScope = async (node: ScopeNode) => {
    if (node.expanded) {
      setScopeNodes((current) => updateNode(current, node.path, (item) => ({ ...item, expanded: false })));
      return;
    }
    if (node.loaded) {
      setScopeNodes((current) => updateNode(current, node.path, (item) => ({ ...item, expanded: true })));
      return;
    }
    setScopeNodes((current) => updateNode(current, node.path, (item) => ({ ...item, loading: true })));
    try {
      const data = await backendRequest<{ children: ScopeNode[] }>("scope_children", { path: node.path });
      setScopeNodes((current) => updateNode(current, node.path, (item) => ({ ...item, loading: false, loaded: true, expanded: true, children: data.children })));
    } catch (error) {
      setScopeNodes((current) => updateNode(current, node.path, (item) => ({ ...item, loading: false })));
      showMessage("error", error instanceof Error ? error.message : String(error));
    }
  };

  const selectScope = (path: string) => {
    if (!path) {
      setSelectedPaths(new Set());
      return;
    }
    setSelectedPaths((current) => {
      const next = new Set(current);
      if (next.has(path)) next.delete(path); else next.add(path);
      return next;
    });
  };

  const runScan = async () => {
    if (connection !== "connected") {
      showMessage("error", t.disconnected);
      return;
    }
    if (!includeSounds && !includeContainers) {
      showMessage("error", language === "ko" ? "오브젝트 타입을 하나 이상 선택하세요." : "Select at least one object type.");
      return;
    }
    setAuditState("scanning");
    setSelectedIds(new Set());
    try {
      const data = await backendRequest<ScanResponse>("scan", {
        includeSounds,
        includeContainers,
        scopePaths: Array.from(selectedPaths),
      });
      setResults(data.results);
      setExceptions(data.exceptions);
      setTotalChecked(data.totalChecked);
      setAuditState("complete");
      setActiveTab("violations");
    } catch (error) {
      setAuditState("error");
      showMessage("error", `${t.scanFailed} ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const currentRows = activeTab === "violations" ? results : exceptions;
  const selectRow = (id: string, additive: boolean) => {
    setSelectedIds((current) => {
      if (!additive) return new Set([id]);
      const next = new Set(current);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const requireSelection = () => {
    const ids = Array.from(selectedIds).filter((id) => currentRows.some((row) => row.id === id));
    if (!ids.length) showMessage("error", t.selectionNeeded);
    return ids;
  };

  const viewInWwise = async () => {
    const ids = requireSelection();
    if (!ids.length) return;
    try { await backendRequest("select_in_wwise", { ids }); }
    catch (error) { showMessage("error", error instanceof Error ? error.message : String(error)); }
  };

  const addException = async () => {
    const ids = requireSelection();
    if (!ids.length) return;
    try {
      const data = await backendRequest<{ results: AuditResult[]; exceptions: AuditResult[] }>("add_exceptions", { ids });
      setResults(data.results); setExceptions(data.exceptions); setSelectedIds(new Set()); setActiveTab("exceptions");
    } catch (error) { showMessage("error", error instanceof Error ? error.message : String(error)); }
  };

  const removeException = async () => {
    const ids = requireSelection();
    if (!ids.length) return;
    try {
      const data = await backendRequest<{ exceptions: AuditResult[] }>("remove_exceptions", { ids });
      setExceptions(data.exceptions); setSelectedIds(new Set());
    } catch (error) { showMessage("error", error instanceof Error ? error.message : String(error)); }
  };

  const exportCsv = async () => {
    if (!results.length) return;
    const path = isTauri() ? await save({ defaultPath: "attenuation_audit.csv", filters: [{ name: "CSV", extensions: ["csv"] }] }) : "attenuation_audit.csv";
    if (!path) return;
    try {
      await backendRequest("export_csv", { path, language });
      showMessage("success", t.exportDone);
    } catch (error) { showMessage("error", error instanceof Error ? error.message : String(error)); }
  };

  const integrityScore = totalChecked ? Math.max(0, ((totalChecked - results.length) / totalChecked) * 100) : 100;
  const scoreDisplay = integrityScore < 100 && integrityScore >= 99
    ? integrityScore.toFixed(1)
    : Math.round(integrityScore).toString();
  const hero = useMemo(() => {
    if (auditState === "scanning") return { title: t.scanTitle, body: t.scanBody };
    if (auditState === "complete") return { title: results.length ? t.issueTitle(results.length) : t.cleanTitle, body: t.resultBody };
    if (auditState === "error") return { title: t.scanFailed, body: t.scanBody };
    return { title: t.idleTitle, body: t.idleBody };
  }, [auditState, results.length, t]);

  return (
    <main className="app-shell">
      <WindowChrome language={language} onLanguageChange={setLanguage} onReconnect={connect} onHelp={() => setHelpOpen(true)} />

      <section className="project-bar">
        <div className={`connection-badge ${connection}`}><i />{connection === "connecting" ? t.connecting : connection === "connected" ? t.connected : t.disconnected}</div>
        {projectName && <><span className="project-name">{projectName}</span><span className="project-separator">/</span><span className="project-location">Actor-Mixer Hierarchy</span></>}
        <span className="local-note">{t.local}</span>
      </section>

      <section className="hero-section">
        <div className="hero-copy">
          <span className="eyebrow">{t.eyebrow}</span>
          <h1>{hero.title}</h1>
          <p>{hero.body}</p>
          <button className="criteria-button" onClick={() => setHelpOpen(true)}><CircleHelp size={13} />{t.confidence}</button>
        </div>
        <AttenuationOrbit state={auditState} issueCount={results.length} />
        <div className="score-block">
          <span>{t.score}</span>
          <strong>{auditState === "complete" ? scoreDisplay : "—"}<small>{auditState === "complete" ? "/100" : ""}</small></strong>
          <div className="score-track"><i style={{ width: auditState === "complete" ? `${integrityScore}%` : "0%" }} /></div>
          <div className="score-axis"><span>0</span><span>100</span></div>
        </div>
      </section>

      <section className="control-strip panel">
        <div className="control-group object-options">
          <span className="section-label">{t.objectTypes}</span>
          <label><input type="checkbox" checked={includeSounds} onChange={(event) => setIncludeSounds(event.target.checked)} /><i><PrecisionCheck /></i><Volume2 size={14} />{t.sounds}</label>
          <label><input type="checkbox" checked={includeContainers} onChange={(event) => setIncludeContainers(event.target.checked)} /><i><PrecisionCheck /></i><Radar size={14} />{t.containers}</label>
        </div>
        <div className="legend-group"><span><i className="miss" />{t.miss}</span><span><i className="extra" />{t.extra}</span></div>
        <button className="scan-button" onClick={runScan} disabled={auditState === "scanning" || connection !== "connected"}>
          {auditState === "scanning" ? <LoaderCircle className="spin" size={15} /> : <ScanSearch size={15} />}
          {auditState === "scanning" ? t.scanning : t.runScan}
        </button>
      </section>

      <section className="metrics-strip">
        <div><span>{t.checked}</span><strong>{auditState === "complete" ? totalChecked.toLocaleString() : "—"}</strong><small>{language === "ko" ? "선택 범위 기준" : "SELECTED SCOPE"}</small></div>
        <div className={results.length ? "danger" : auditState === "complete" ? "clean" : ""}><span>{t.violations}</span><strong>{auditState === "complete" ? results.length : "—"}</strong><small>{auditState === "complete" ? (results.length ? t.issueTitle(results.length) : t.noViolations) : "MISS + EXTRA"}</small></div>
        <div className="violet"><span>{t.exceptions}</span><strong>{exceptions.length}</strong><small>{language === "ko" ? "의도적으로 제외됨" : "INTENTIONALLY EXCLUDED"}</small></div>
      </section>

      <section className="workspace">
        <ScopeTree nodes={scopeNodes} selectedPaths={selectedPaths} allLabel={t.scopeAll} hint={t.scopeHint} onToggle={toggleScope} onSelect={selectScope} onRefresh={loadRootScope} />
        <ResultsTable language={language} activeTab={activeTab} results={results} exceptions={exceptions} selectedIds={selectedIds} scanned={auditState === "complete"} onTabChange={(tab) => { setActiveTab(tab); setSelectedIds(new Set()); }} onSelect={selectRow} onView={viewInWwise} onExport={exportCsv} onAddException={addException} onRemoveException={removeException} />
      </section>

      {message && <div className={`toast ${message.tone}`}>{message.tone === "error" ? <AlertTriangle size={15} /> : <Check size={15} />}{message.text}</div>}
      {helpOpen && (
        <div className="modal-backdrop" onMouseDown={() => setHelpOpen(false)}>
          <section className="criteria-modal" onMouseDown={(event) => event.stopPropagation()}>
            <button className="modal-close" onClick={() => setHelpOpen(false)}><X size={15} /></button>
            <span className="eyebrow">ATTENUATION CONTRACT</span>
            <h2>{t.helpTitle}</h2>
            <p>{t.helpBody}</p>
            <div className="criteria-grid">
              <div><span className="criteria-index">01</span><strong>3D SOUND</strong><code>LRR = ON</code><code>Spatialization ∈ {"{1, 2}"}</code></div>
              <div><span className="criteria-index">02</span><strong>EFFECTIVE ATT</strong><code>EnableAttenuation = ON</code><code>Attenuation.name ≠ null</code></div>
              <div className="miss"><span className="criteria-index">MISS</span><strong>3D ∧ ¬ ATT</strong><p>{t.miss}</p></div>
              <div className="extra"><span className="criteria-index">EXTRA</span><strong>2D ∧ ATT</strong><p>{t.extra}</p></div>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
