// Builds the three submission documents from Markdown sources in this folder:
//   ../01_manuscript/Manuscript.docx              (manuscript.md)
//   ../03_cover_letter/Cover_Letter.docx          (cover_letter.md)
//   ../04_supplementary/Supplementary_Material.docx (supplementary.md + repository reports)
// Run `python submission/build/make_figures.py` first (it writes build/embed/*.png).
// Usage (from this folder): node build_docs.js
"use strict";
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const { build } = require("./md2docx");

const HERE = __dirname;
const ROOT = path.resolve(HERE, "..", "..");
const SUB = path.resolve(HERE, "..");
const EMBED = path.join(HERE, "embed");
const TITLE = "Which Behavioural Markers of Sentience and Self-Awareness Can a Simple Mechanism Fake? " +
              "Pre-Registered Tests With Homeostatic Agents";

const read = (p) => fs.readFileSync(p, "utf8").replace(/\r/g, "");

// Main-text words: Introduction to Conclusion, without tables, figures, captions or displayed equations.
function mainTextWords(md) {
  const start = md.indexOf("# 1 Introduction");
  const end = md.indexOf("# Use of Generative AI");
  return md.slice(start, end).split("\n")
    .filter((l) => !/^\s*(\||::figure|::center|\*\*(Table|Figure) \d)/.test(l))
    .join(" ").replace(/[#*`]/g, " ").split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length;
}

function csvRows(file) {
  const [head, ...rows] = read(file).trim().split("\n").map((l) => l.split(","));
  return rows.map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}

function metricTable(file, agents, metrics) {
  const rows = csvRows(file);
  const get = (agent, metric) => rows.find((r) => r.agent === agent && r.metric === metric);
  const fmt = (r, signed) => {
    if (!r || r.n === "0") return "n/a";
    const f = (x) => (signed && Number(x) > 0 ? "+" : "") + Number(x).toFixed(2);
    return `${f(r.mean)} [${Number(r.ci_low).toFixed(2)}, ${Number(r.ci_high).toFixed(2)}] (n = ${r.n})`;
  };
  const lines = [`| Metric | ${agents.map((a) => a[1]).join(" | ")} |`, `|---|${agents.map(() => "---").join("|")}|`];
  for (const [metric, label, signed] of metrics) {
    lines.push(`| ${label} | ${agents.map(([a]) => fmt(get(a, metric), signed)).join(" | ")} |`);
  }
  return lines.join("\n");
}

function study1Tables() {
  const base = [["random", "Random walker"], ["reflex_nociceptive", "Nociceptive reflex"],
                ["reflex_thermotactic", "Thermotactic reflex"]];
  const markers = [
    ["survived_frac", "Survival (fraction of 90 s episodes)"],
    ["anticipation_rate", "Anticipatory avoidance (per-episode rate)"],
    ["damage_taken", "Damage taken per episode"],
    ["tradeoff_score", "Trade-off score", true],
    ["sensitization_c", "Sensitization (°C)", true],
    ["sensitization_nonharmful_c", "Sensitization, like-for-like (°C)", true],
  ];
  const energy = [];
  for (const e of ["0.08", "0.3", "0.5", "0.9"]) {
    energy.push([`crossing_rate@${e}`, `Crossed the wall, start energy ${e}`]);
    energy.push([`reached_charger@${e}`, `Reached the charger, start energy ${e}`]);
  }
  const literal = [["reflex_nociceptive_literal", "Nociceptive reflex (literal)"],
                   ["reflex_thermotactic_literal", "Thermotactic reflex (literal)"]];
  return [
    "## S9.1 Study 1 Markers at 100 Seeds",
    "::noindent Mean [95% CI] (n = episodes, encounters or episodes with the event). Source: `results/seeds100/summary.csv`.",
    metricTable(path.join(ROOT, "results/seeds100/summary.csv"), base, markers),
    "## S9.2 Trade-Off World by Start Energy (30 Seeds)",
    "::noindent Wilson 95% intervals. Source: `results/summary.csv`.",
    metricTable(path.join(ROOT, "results/summary.csv"), base, energy),
    "## S9.3 The Literal Reflex Specification (30 Seeds)",
    "::noindent Reflexes that reverse their *commanded* heading on every trigger, as first specified. " +
    "They oscillate inside heat sources (Section 3.6 of the article). Source: `results/literal_reflex/summary.csv`.",
    metricTable(path.join(ROOT, "results/literal_reflex/summary.csv"), literal, markers),
  ].join("\n\n");
}

function gitLog() {
  const out = execSync('git log --reverse --date=format:"%Y-%m-%d %H:%M" --format="%h|%ad|%s"',
                       { cwd: ROOT, encoding: "utf8" }).trim().split("\n");
  return ["| Commit | Time (UTC−7) | Message |", "|---|---|---|",
          ...out.map((l) => { const [h, d, ...m] = l.split("|"); return `| \`${h}\` | ${d} | ${m.join("|")} |`; }),
         ].join("\n");
}

// ::include <repo path>: demote headings by one level and point image links at the repository.
function expandIncludes(md) {
  return md.split("\n").map((line) => {
    let m = line.match(/^::include\s+(\S+)/);
    if (m) {
      const dir = path.posix.dirname(m[1]);
      return read(path.join(ROOT, m[1])).split("\n")
        .map((l) => (/^#{1,3}\s/.test(l) ? "#" + l : l))
        .map((l) => l.replace(/^!\[([^\]]*)\]\((?!http)([^)]+)\)/, (_, a, p) => `![${a}](${dir}/${p})`))
        .join("\n");
    }
    m = line.match(/^::code\s+(\S+)/);
    if (m) return "```\n" + read(path.join(ROOT, m[1])).trimEnd() + "\n```";
    return line;
  }).join("\n");
}

async function main() {
  let manuscript = read(path.join(HERE, "manuscript.md"));
  const words = mainTextWords(manuscript);
  manuscript = manuscript.replace("{{WORDCOUNT}}", words.toLocaleString("en-US"));
  await build(manuscript, path.join(SUB, "01_manuscript", "Manuscript.docx"), {
    embedDir: EMBED, lineNumbers: true, runningHead: "MARKERS VERSUS MINIMAL MECHANISMS", title: TITLE,
  });
  console.log(`Manuscript.docx: main text ${words} words`);

  // Preprint version (arXiv): same text, 1.15 spacing, no line numbers.
  await build(manuscript, path.join(SUB, "07_preprint_arxiv", "Preprint.docx"), {
    embedDir: EMBED, lineSpacing: 276, runningHead: "PREPRINT — MARKERS VERSUS MINIMAL MECHANISMS", title: TITLE,
  });
  const abstract = manuscript.split("# Abstract")[1].split("::pagebreak")[0]
    .replace("::noindent", "").replace(/[*\n]/g, " ").replace(/\s+/g, " ").trim();
  fs.writeFileSync(path.join(SUB, "07_preprint_arxiv", "abstract_plain.txt"), abstract + "\n");
  console.log(`Preprint.docx; abstract ${abstract.length} characters, ${abstract.split(" ").length} words`);

  await build(read(path.join(HERE, "cover_letter.md")), path.join(SUB, "03_cover_letter", "Cover_Letter.docx"), {
    lineSpacing: 264, indentFirst: false, size: 22, title: "Cover letter",
  });
  console.log("Cover_Letter.docx");

  const supp = expandIncludes(read(path.join(HERE, "supplementary.md")))
    .replace("{{STUDY1_TABLES}}", study1Tables()).replace("{{GITLOG}}", gitLog());
  fs.writeFileSync(path.join(HERE, "supplementary.expanded.md"), supp);
  await build(supp, path.join(SUB, "04_supplementary", "Supplementary_Material.docx"), {
    lineSpacing: 276, indentFirst: false, size: 22, tableSize: 16,
    runningHead: "SUPPLEMENTARY MATERIAL", title: `Supplementary Material: ${TITLE}`,
  });
  console.log("Supplementary_Material.docx");
}

main().catch((e) => { console.error(e); process.exit(1); });
