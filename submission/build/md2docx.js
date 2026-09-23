// Minimal Markdown -> .docx converter for the submission documents.
//
// Supports: # headings (1-4), paragraphs, **bold**, *italic*, `code`, [FILL: ...]
// (highlighted), - and 1. lists (nested by indent), | tables |, ``` code fences,
// --- rules, and directives: ::title, ::center, ::noindent, ::pagebreak,
// ::figure <name> | <alt text>, ::refs ... ::endrefs (hanging-indent references).
"use strict";
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow,
  TableCell, WidthType, BorderStyle, ShadingType, ImageRun, Header, PageNumber,
  LevelFormat, TabStopType, LineNumberRestartFormat, PageBreak,
} = require("docx");

const FONT = "Times New Roman";
const MONO = "Courier New";
const TEXT_WIDTH = 9360;            // 6.5 in between 1 in margins (US Letter)
const IMAGE_WIDTH_PX = 624;         // 6.5 in at 96 px/in
const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const RULE = { style: BorderStyle.SINGLE, size: 6, color: "000000" };

function inline(text, base = {}) {
  const runs = [];
  const re = /(\*\*(?:[^*]|\*[^*]+\*)+?\*\*|\*[^*\s][^*]*?\*|`[^`]+`|\[FILL:[^\]]*\])/g;
  let last = 0;
  for (const m of text.matchAll(re)) {
    if (m.index > last) runs.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const tok = m[0];
    if (tok.startsWith("**")) runs.push(...inline(tok.slice(2, -2), { ...base, bold: true }));
    else if (tok.startsWith("*")) runs.push(...inline(tok.slice(1, -1), { ...base, italics: true }));
    else if (tok.startsWith("`")) runs.push(new TextRun({ text: tok.slice(1, -1), ...base, font: MONO,
                                                           size: base.size ? base.size - 2 : undefined }));
    else runs.push(new TextRun({ text: tok, ...base, bold: true,        // yellow marker, schema-valid
                                 shading: { type: ShadingType.CLEAR, fill: "FFFF00", color: "auto" } }));
    last = m.index + tok.length;
  }
  if (last < text.length) runs.push(new TextRun({ text: text.slice(last), ...base }));
  return runs;
}

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { data: b, w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function splitRow(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
}

function makeTable(rows, opts) {
  const header = rows[0];
  const body = rows.slice(2);              // rows[1] is the |---| separator
  const all = [header, ...body];
  const n = header.length;
  const weight = [...Array(n).keys()].map((j) =>
    Math.max(6, Math.min(42, ...all.map((r) => (r[j] || "").replace(/[*`]/g, "").length))));
  const total = weight.reduce((a, b) => a + b, 0);
  const widths = weight.map((w) => Math.floor((w / total) * TEXT_WIDTH));
  widths[n - 1] += TEXT_WIDTH - widths.reduce((a, b) => a + b, 0);
  const cell = (text, j, isHead, isLast) => new TableCell({
    width: { size: widths[j], type: WidthType.DXA },
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    borders: { top: isHead ? RULE : NONE, bottom: isHead || isLast ? RULE : NONE, left: NONE, right: NONE },
    children: [new Paragraph({
      spacing: { line: 240, before: 0, after: 0 },
      children: inline(text || "", { size: opts.tableSize, font: FONT, bold: isHead || undefined }),
    })],
  });
  return new Table({
    width: { size: TEXT_WIDTH, type: WidthType.DXA },
    columnWidths: widths,
    rows: all.map((r, i) => new TableRow({
      tableHeader: i === 0,
      cantSplit: true,
      children: [...Array(n).keys()].map((j) => cell(r[j], j, i === 0, i === all.length - 1)),
    })),
  });
}

function convert(md, opts) {
  opts = { lineSpacing: 480, indentFirst: true, tableSize: 20, size: 24, embedDir: ".", ...opts };
  const out = [];
  const sp = { line: opts.lineSpacing, before: 0, after: 0 };
  let para = [];
  let listInstance = 0;
  let inList = false;
  let refs = false;
  const lines = md.replace(/\r/g, "").split("\n");

  const flush = () => {
    if (!para.length) return;
    const text = para.join(" ");
    para = [];
    const caption = /^\*\*(Table|Figure|Supplementary Table|Table S)\s*[\dS]/.test(text);
    out.push(new Paragraph({
      spacing: sp,
      keepNext: caption && text.startsWith("**Table"),
      indent: opts.indentFirst && !caption ? { firstLine: 720 } : undefined,
      children: inline(text),
    }));
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const t = line.trim();
    if (refs) {
      if (t === "::endrefs") { refs = false; continue; }
      if (t) out.push(new Paragraph({ spacing: sp, indent: { left: 720, hanging: 720 }, children: inline(t) }));
      continue;
    }
    if (!t) { flush(); inList = false; continue; }
    if (t.startsWith("```")) {
      flush();
      for (i++; i < lines.length && !lines[i].trim().startsWith("```"); i++) {
        out.push(new Paragraph({ spacing: { line: 240, before: 0, after: 0 }, indent: { left: 360 },
                                 children: [new TextRun({ text: lines[i] || " ", font: MONO, size: 18 })] }));
      }
      continue;
    }
    if (t === "::refs") { flush(); refs = true; continue; }
    if (t === "::pagebreak") { flush(); out.push(new Paragraph({ children: [new PageBreak()] })); continue; }
    if (t.startsWith("::title ")) {
      flush();
      out.push(new Paragraph({ spacing: { ...sp, before: 1440, after: 480 }, alignment: AlignmentType.CENTER,
                               children: inline(t.slice(8), { bold: true, size: 28 }) }));
      continue;
    }
    if (t.startsWith("::center ")) {
      flush();
      out.push(new Paragraph({ spacing: sp, alignment: AlignmentType.CENTER, children: inline(t.slice(9)) }));
      continue;
    }
    if (t.startsWith("::noindent ")) {
      flush();
      out.push(new Paragraph({ spacing: sp, children: inline(t.slice(11)) }));
      continue;
    }
    if (t.startsWith("::figure ")) {
      flush();
      const [name, alt] = t.slice(9).split("|").map((s) => s.trim());
      const img = pngSize(path.join(opts.embedDir, `${name}.png`));
      const w = IMAGE_WIDTH_PX;
      const h = Math.round((w * img.h) / img.w);
      out.push(new Paragraph({
        spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER, keepNext: true,
        children: [new ImageRun({ type: "png", data: img.data, transformation: { width: w, height: h },
                                  altText: { name, title: name, description: alt } })],
      }));
      continue;
    }
    if (/^!\[/.test(t)) {        // image links in included reports: point to the repository file
      flush();
      const m = t.match(/^!\[([^\]]*)\]\(([^)]+)\)/);
      out.push(new Paragraph({ spacing: sp, children: inline(`*[Figure file in the repository: ${m ? m[2] : t}]*`) }));
      continue;
    }
    if (/^---+$/.test(t)) {
      flush();
      out.push(new Paragraph({ spacing: { before: 120, after: 120 },
                               border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "999999", space: 1 } } }));
      continue;
    }
    const h = t.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      flush();
      const level = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3,
                     HeadingLevel.HEADING_4][h[1].length - 1];
      out.push(new Paragraph({ heading: level, keepNext: true, children: inline(h[2]) }));
      continue;
    }
    if (t.startsWith("|")) {
      flush();
      const rows = [];
      for (; i < lines.length && lines[i].trim().startsWith("|"); i++) rows.push(splitRow(lines[i]));
      i--;
      out.push(makeTable(rows, opts));
      out.push(new Paragraph({ spacing: { before: 0, after: 240 }, children: [] }));
      continue;
    }
    const li = line.match(/^(\s*)([-*]|\d+\.)\s+(.*)$/);
    if (li) {
      flush();
      if (!inList) { listInstance++; inList = true; }
      const level = Math.min(2, Math.floor(li[1].length / 2));
      let text = li[3];
      while (i + 1 < lines.length && /^\s{2,}\S/.test(lines[i + 1]) &&
             !/^\s*([-*]|\d+\.)\s+/.test(lines[i + 1])) text += " " + lines[++i].trim();
      const numbered = /\d/.test(li[2]);
      out.push(new Paragraph({
        spacing: sp,
        numbering: numbered ? { reference: "numbers", level, instance: listInstance }
                            : { reference: "bullets", level },
        children: inline(text),
      }));
      continue;
    }
    if (inList && /^\s{2,}\S/.test(line)) continue;   // stray continuation already consumed
    inList = false;
    para.push(t);
  }
  flush();
  return out;
}

function numbering() {
  const lvl = (level, format, text) => ({
    level, format, text, alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720 * (level + 1), hanging: 360 } } },
  });
  return {
    config: [
      { reference: "bullets", levels: [lvl(0, LevelFormat.BULLET, "•"), lvl(1, LevelFormat.BULLET, "–"),
                                       lvl(2, LevelFormat.BULLET, "•")] },
      { reference: "numbers", levels: [lvl(0, LevelFormat.DECIMAL, "%1."), lvl(1, LevelFormat.LOWER_LETTER, "%2."),
                                       lvl(2, LevelFormat.LOWER_ROMAN, "%3.")] },
    ],
  };
}

function styles(size, lineSpacing) {
  const heading = (id, name, italics) => ({
    id, name, basedOn: "Normal", next: "Normal", quickFormat: true,
    run: { font: FONT, size, bold: true, italics, color: "000000" },
    paragraph: { spacing: { before: 240, after: 0, line: lineSpacing }, outlineLevel: Number(id.slice(-1)) - 1 },
  });
  return {
    default: { document: { run: { font: FONT, size } } },
    paragraphStyles: [heading("Heading1", "Heading 1", false), heading("Heading2", "Heading 2", false),
                      heading("Heading3", "Heading 3", true), heading("Heading4", "Heading 4", true)],
  };
}

async function build(md, file, opts = {}) {
  const o = { lineSpacing: 480, size: 24, ...opts };
  const header = o.runningHead ? {
    default: new Header({ children: [new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: TEXT_WIDTH }],
      children: [new TextRun({ text: o.runningHead, size: 20 }),
                 new TextRun({ children: ["\t", PageNumber.CURRENT], size: 20 })],
    })] }),
  } : undefined;
  const doc = new Document({
    creator: o.creator || "",
    title: o.title || "",
    styles: styles(o.size, o.lineSpacing),
    numbering: numbering(),
    sections: [{
      properties: {
        page: { size: { width: 12240, height: 15840 },
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440, header: 720, footer: 720 } },
        lineNumbers: o.lineNumbers ? { countBy: 1, restart: LineNumberRestartFormat.CONTINUOUS, distance: 360 }
                                   : undefined,
      },
      headers: header,
      children: convert(md, o),
    }],
  });
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, await Packer.toBuffer(doc));
}

module.exports = { build, convert };
