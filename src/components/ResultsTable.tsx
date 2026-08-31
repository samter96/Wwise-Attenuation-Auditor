import { ArrowDownToLine, ExternalLink, FileSearch, ShieldCheck, ShieldMinus } from "lucide-react";
import type { AuditResult, Language } from "../types";
import { copy } from "../i18n";

interface Props {
  language: Language;
  activeTab: "violations" | "exceptions";
  results: AuditResult[];
  exceptions: AuditResult[];
  selectedIds: Set<string>;
  scanned: boolean;
  onTabChange: (tab: "violations" | "exceptions") => void;
  onSelect: (id: string, additive: boolean) => void;
  onView: () => void;
  onExport: () => void;
  onAddException: () => void;
  onRemoveException: () => void;
}

export default function ResultsTable({ language, activeTab, results, exceptions, selectedIds, scanned, onTabChange, onSelect, onView, onExport, onAddException, onRemoveException }: Props) {
  const t = copy(language);
  const rows = activeTab === "violations" ? results : exceptions;
  const emptyTitle = activeTab === "exceptions" ? t.noExceptions : scanned ? t.noViolations : t.noResults;
  const emptyBody = !scanned && activeTab === "violations" ? t.noResultsBody : "";

  return (
    <section className="results-panel panel">
      <div className="results-tabs">
        <button className={activeTab === "violations" ? "active" : ""} onClick={() => onTabChange("violations")}>{t.violationsTab}<span>{results.length}</span></button>
        <button className={activeTab === "exceptions" ? "active" : ""} onClick={() => onTabChange("exceptions")}>{t.exceptionsTab}<span>{exceptions.length}</span></button>
      </div>
      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>{t.name}</th><th>{t.type}</th><th>{t.spatialization}</th><th>{t.attenuation}</th><th>{t.issue}</th><th>{t.workunit}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className={`${row.issue} ${selectedIds.has(row.id) ? "selected" : ""}`} onClick={(event) => onSelect(row.id, event.ctrlKey || event.metaKey)} onDoubleClick={onView} title={row.path}>
                <td><span className="asset-name">{row.name}</span><span className="asset-path">{row.path}</span></td>
                <td>{row.type}</td><td>{row.spat}</td><td>{row.att}</td>
                <td><span className={`issue-badge ${row.issue}`}><i />{row.issue === "miss" ? t.miss : t.extra}</span></td>
                <td>{row.wu}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && (
          <div className="empty-results">
            {scanned && activeTab === "violations" ? <ShieldCheck size={26} /> : <FileSearch size={26} />}
            <strong>{emptyTitle}</strong>
            {emptyBody && <span>{emptyBody}</span>}
          </div>
        )}
      </div>
      <footer className="results-actions">
        <div>
          <button className="secondary-button" onClick={onView}><ExternalLink size={13} />{t.viewWwise}</button>
          <button className="secondary-button" onClick={onExport} disabled={!results.length}><ArrowDownToLine size={13} />{t.exportCsv}</button>
        </div>
        <div>
          {activeTab === "violations" ? (
            <button className="exception-button" onClick={onAddException}><ShieldCheck size={13} />{t.addException}</button>
          ) : (
            <button className="remove-button" onClick={onRemoveException}><ShieldMinus size={13} />{t.removeException}</button>
          )}
        </div>
      </footer>
    </section>
  );
}
