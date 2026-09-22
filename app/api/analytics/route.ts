import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

const allowed = ["batting","batting_consistency","bowling","phase_analysis","team_season","venue_analysis","toss_analysis","match_summary","season_overview"];

function parseCsvLine(line: string) {
  const out: string[] = [];
  let cur = "";
  let quoted = false;
  for (const c of line) {
    if (c === '"') quoted = !quoted;
    else if (c === "," && !quoted) { out.push(cur); cur = ""; }
    else cur += c;
  }
  out.push(cur);
  return out.map((x) => x.replace(/^"|"$/g, ""));
}

async function readCsv(filePath: string) {
  const raw = await fs.readFile(filePath, "utf8");
  const lines = raw.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = parseCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const values = parseCsvLine(line);
    return Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ""]));
  });
}

async function loadDataset(name: string) {
  if (!allowed.includes(name)) throw new Error("Invalid dataset");
  try {
    const dir = path.join(process.cwd(), "data", "processed", name);
    const files = await fs.readdir(dir);
    const csv = files.find((file) => file.endsWith(".csv"));
    if (csv) return { data: await readCsv(path.join(dir, csv)), source: "spark" };
  } catch {}
  const demoPath = path.join(process.cwd(), "data", "demo", "processed", name + ".csv");
  return { data: await readCsv(demoPath), source: "demo-snapshot" };
}

export async function GET(req: Request) {
  try {
    const name = new URL(req.url).searchParams.get("dataset") || "season_overview";
    const result = await loadDataset(name);
    return NextResponse.json({ dataset: name, count: result.data.length, source: result.source, data: result.data });
  } catch (error) {
    return NextResponse.json({ error: "Analytics dataset unavailable", detail: String(error) }, { status: 500 });
  }
}
