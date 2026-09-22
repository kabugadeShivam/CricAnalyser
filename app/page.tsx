"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity, BarChart3, ChevronDown, Database, LayoutDashboard, MapPin,
  RefreshCw, Search, Trophy, Wind
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, BarChart, Bar, Legend
} from "recharts";

type Row = Record<string, string>;
type PageName = "Overview" | "Batting" | "Bowling" | "Teams" | "Venues" | "Insights";

const seasons = ["All Seasons", "2025", "2024", "2023", "2022", "2021"];
const nav: [PageName, typeof LayoutDashboard][] = [
  ["Overview", LayoutDashboard], ["Batting", BarChart3], ["Bowling", Wind],
  ["Teams", Trophy], ["Venues", MapPin], ["Insights", Activity]
];

const pageConfig: Record<PageName, { dataset: string; title: string; subtitle: string; key: string; metric: string; seasonAware: boolean }> = {
  Overview: { dataset: "season_overview", title: "Run production by season", subtitle: "Season-level Spark aggregation", key: "season", metric: "total_runs", seasonAware: true },
  Batting: { dataset: "batting", title: "Top run scorers", subtitle: "All-time batting aggregation", key: "batter", metric: "runs", seasonAware: false },
  Bowling: { dataset: "bowling", title: "Top wicket takers", subtitle: "All-time bowling aggregation", key: "bowler", metric: "wickets", seasonAware: false },
  Teams: { dataset: "team_season", title: "Team season performance", subtitle: "Runs scored by team and season", key: "batting_team", metric: "runs_scored", seasonAware: true },
  Venues: { dataset: "venue_analysis", title: "Venue scoring", subtitle: "Venue-level Spark aggregation", key: "venue", metric: "runs", seasonAware: false },
  Insights: { dataset: "phase_analysis", title: "Scoring by innings phase", subtitle: "Powerplay, middle overs and death overs", key: "phase", metric: "runs", seasonAware: true }
};

async function getData(dataset: string) {
  const response = await fetch("/api/analytics?dataset=" + encodeURIComponent(dataset), { cache: "no-store" });
  if (!response.ok) throw new Error("Dataset unavailable");
  return response.json() as Promise<{ data: Row[]; source: string; count: number }>;
}

function Sidebar({ page, setPage }: { page: PageName; setPage: (page: PageName) => void }) {
  return (
    <aside className="sidebar">
      <div className="brand"><div className="logo">C</div><div><b>CricAnalyser</b><span>IPL BIG DATA</span></div></div>
      <nav>{nav.map(([name, Icon]) => (
        <button key={name} onClick={() => setPage(name)} className={page === name ? "nav active" : "nav"}><Icon size={18}/><span>{name}</span></button>
      ))}</nav>
      <div className="sideBottom"><Database size={17}/><span>Hadoop + Spark</span><small>Analytics pipeline</small></div>
    </aside>
  );
}

function Stat({ label, value, sub }: { label: string; value: string; sub: string }) {
  return <div className="stat"><span>{label}</span><strong>{value}</strong><small>{sub}</small></div>;
}

function formatNumber(value: unknown) {
  const n = Number(value);
  return Number.isFinite(n) ? n.toLocaleString("en-IN", { maximumFractionDigits: 2 }) : String(value ?? "0");
}

function TopBars({ rows, keyField, metric }: { rows: Row[]; keyField: string; metric: string }) {
  const top = rows.slice(0, 8);
  const max = Math.max(...top.map(r => Number(r[metric]) || 0), 1);
  return <div className="bars">{top.map((row, i) => {
    const value = Number(row[metric]) || 0;
    return <div className="barRow" key={String(row[keyField]) + i}>
      <div><span>{i + 1}</span><b>{row[keyField] || "Unknown"}</b></div>
      <strong>{formatNumber(value)}</strong>
      <div className="bar"><i style={{ width: Math.min(100, value / max * 100) + "%" }}/></div>
    </div>;
  })}</div>;
}

function DataTable({ rows, columns }: { rows: Row[]; columns: string[] }) {
  return <div className="tableWrap"><table><thead><tr>{columns.map(c => <th key={c}>{c.replaceAll("_", " ")}</th>)}</tr></thead>
    <tbody>{rows.slice(0, 12).map((row, i) => <tr key={i}>{columns.map(c => <td key={c}>{formatNumber(row[c])}</td>)}</tr>)}</tbody>
  </table></div>;
}

export default function Home() {
  const [page, setPage] = useState<PageName>("Overview");
  const [season, setSeason] = useState("All Seasons");
  const [search, setSearch] = useState("");
  const [rows, setRows] = useState<Row[]>([]);
  const [source, setSource] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const config = pageConfig[page];

  async function load() {
    setLoading(true);
    setError("");
    try {
      const result = await getData(config.dataset);
      setRows(result.data);
      setSource(result.source);
    } catch {
      setRows([]);
      setError("Analytics data could not be loaded. Check the Spark output or deployable demo snapshot.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    setSearch("");
    if (!config.seasonAware) setSeason("All Seasons");
    load();
  }, [page]);

  const filtered = useMemo(() => {
    let result = rows;
    if (config.seasonAware && season !== "All Seasons") {
      result = result.filter(row => String(row.season) === season);
    }
    const query = search.trim().toLowerCase();
    if (query) {
      result = result.filter(row => Object.values(row).some(value => String(value).toLowerCase().includes(query)));
    }
    return result;
  }, [rows, season, search, config]);

  const sorted = useMemo(() => [...filtered].sort((a, b) => (Number(b[config.metric]) || 0) - (Number(a[config.metric]) || 0)), [filtered, config.metric]);

  const chartRows = useMemo(() => {
    if (page === "Overview") return filtered;
    if (page === "Insights") return filtered;
    return sorted.slice(0, 12);
  }, [filtered, sorted, page]);

  return <div className="shell">
    <Sidebar page={page} setPage={setPage}/>
    <main>
      <header>
        <div>
          <p className="eyebrow">IPL PERFORMANCE INTELLIGENCE</p>
          <h1>{page}</h1>
          <p className="muted">{config.subtitle}. Source: {source === "spark" ? "Spark output" : "deployable demo snapshot"}.</p>
        </div>
        <div className="actions">
          <div className="search"><Search size={17}/><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search results"/></div>
          <div className={config.seasonAware ? "select" : "select disabled"}>
            <select value={season} onChange={e => setSeason(e.target.value)} disabled={!config.seasonAware}>
              {seasons.map(s => <option key={s}>{s}</option>)}
            </select><ChevronDown size={15}/>
          </div>
          <button className="refresh" onClick={load} aria-label="Refresh analytics"><RefreshCw size={15}/></button>
        </div>
      </header>

      {error ? <div className="notice"><Database size={18}/><div><b>Pipeline output unavailable</b><p>{error}</p></div></div> :
      loading ? <div className="loading">Loading Spark analytics…</div> : <>
        {page === "Overview" && <section className="stats">
          <Stat label="MATCHES ANALYSED" value="1,044" sub="2008 — 2025 dataset"/>
          <Stat label="DELIVERIES" value="251,951" sub="Ball-by-ball records"/>
          <Stat label="SEASONS" value={String(rows.length)} sub="Processed seasons"/>
          <Stat label="PROCESSING" value="SPARK" sub="Distributed analytics"/>
        </section>}

        {!config.seasonAware && <div className="filterNote">This view is an <b>all-time aggregate</b>; the season selector is disabled because this dataset is not season-indexed.</div>}
        <section className="grid">
          <div className="panel wide">
            <div className="panelHead"><div><h2>{config.title}</h2><p>{filtered.length} matching records</p></div><span className="tag">{source === "spark" ? "SPARK OUTPUT" : "DEMO SNAPSHOT"}</span></div>
            <div className="chart">
              <ResponsiveContainer width="100%" height={300}>
                {page === "Overview" ?
                  <LineChart data={chartRows}><CartesianGrid vertical={false} stroke="#e7eaf0"/><XAxis dataKey="season" tickLine={false} axisLine={false}/><YAxis tickLine={false} axisLine={false}/><Tooltip/><Line type="monotone" dataKey="total_runs" stroke="#111827" strokeWidth={2.5}/></LineChart> :
                page === "Insights" ?
                  <BarChart data={chartRows}><CartesianGrid vertical={false} stroke="#e7eaf0"/><XAxis dataKey="phase" tickLine={false} axisLine={false}/><YAxis tickLine={false} axisLine={false}/><Tooltip/><Legend/><Bar dataKey="runs" fill="#111827"/><Bar dataKey="wickets" fill="#8b929d"/></BarChart> :
                  <BarChart data={chartRows}><CartesianGrid vertical={false} stroke="#e7eaf0"/><XAxis dataKey={config.key} tickLine={false} axisLine={false} tick={{fontSize:10}} interval={0}/><YAxis tickLine={false} axisLine={false}/><Tooltip/><Bar dataKey={config.metric} fill="#111827" radius={[4,4,0,0]}/></BarChart>}
              </ResponsiveContainer>
            </div>
          </div>
          <div className="panel">
            <div className="panelHead"><div><h2>Top performers</h2><p>{search ? "Filtered by search" : season === "All Seasons" ? "Current selection: all seasons" : "Current season: " + season}</p></div></div>
            <TopBars rows={sorted} keyField={config.key} metric={config.metric}/>
          </div>
        </section>

        <section className="panel detailPanel">
          <div className="panelHead"><div><h2>Processed records</h2><p>Showing up to 12 rows from the current filters.</p></div></div>
          {page === "Batting" && <DataTable rows={sorted} columns={["batter","runs","fours","sixes","matches","runs_per_match"]}/>}
          {page === "Bowling" && <DataTable rows={sorted} columns={["bowler","wickets","runs_conceded","matches","economy"]}/>}
          {page === "Teams" && <DataTable rows={sorted} columns={["season","batting_team","runs_scored","wickets_lost","matches","runs_per_match"]}/>}
          {page === "Venues" && <DataTable rows={sorted} columns={["venue","matches","runs","wickets","avg_runs_per_delivery"]}/>}
          {page === "Insights" && <DataTable rows={sorted} columns={["season","phase","runs","wickets","deliveries","runs_per_delivery"]}/>}
          {page === "Overview" && <DataTable rows={filtered} columns={["season","total_runs","total_wickets","deliveries","matches","runs_per_match"]}/>}
        </section>

        <section className="insight"><div className="insightIcon"><Activity size={17}/></div><div><b>End-to-end pipeline</b><p>Raw data → HDFS → PySpark cleaning → Spark analytics → processed datasets → dashboard.</p></div><span className="live">CONNECTED</span></section>
      </>}
    </main>
  </div>;
}
