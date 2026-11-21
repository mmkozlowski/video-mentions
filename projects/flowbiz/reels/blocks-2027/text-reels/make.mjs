#!/usr/bin/env node
// Składa rolki tekstowe 9:16 (grafika GPT + jedno zdanie naraz) z variants.json do projektów HyperFrames.
//
// Źródło:  text-reels/template.html + variants.json, grafiki ../gpt/<nazwa>.png
// Wynik:   projects/flowbiz/build/hf/text-reel-<wariant>/ (poza gitem, odtwarzalne)
// Użycie:  node make.mjs [wariant ...]   → wypisuje katalogi projektów
//
// Grafiki 2:3 z GPT: skala do szerokości 1080, góra dopełniona kolorem tła obrazu (#070709) —
// bez przycinania boków i bez rozciągania (pamięć nigdy-nie-rozciagaj-kadru). Góra i tak idzie pod tekst.

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FLOWBIZ = path.resolve(HERE, "../../..");
const SHARED = path.join(FLOWBIZ, "screens", "shared");
const GPT = path.resolve(HERE, "../gpt");
const OUT = path.join(FLOWBIZ, "build", "hf");

const variants = JSON.parse(fs.readFileSync(path.join(HERE, "variants.json"), "utf8"));
const template = fs.readFileSync(path.join(HERE, "template.html"), "utf8");

function renderLine(line, index) {
  const eyebrow = line.eyebrow ? `<div class="eyebrow"><span class="dot"></span>${line.eyebrow}</div>` : "";
  const sub = line.sub ? `<p class="sub">${line.sub}</p>` : "";
  const chip = line.chip ? `<div class="chip">${line.chip}</div>` : "";
  return `<div class="line" id="r-line${index}">${eyebrow}<p class="big">${line.html}</p>${sub}${chip}</div>`;
}

function build(name) {
  const variant = variants[name];
  const id = `text-reel-${name}`;
  const dir = path.join(OUT, id);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(path.join(dir, "assets"), { recursive: true });
  fs.cpSync(SHARED, path.join(dir, "assets"), { recursive: true });

  for (const shot of variant.shots) {
    const source = path.join(GPT, `${shot.img}.png`);
    if (!fs.existsSync(source)) throw new Error(`Brak grafiki: ${source}`);
    execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", source, "-vf",
      "scale=1080:-2,pad=1080:1920:0:(oh-ih):0x070709", "-q:v", "2",
      path.join(dir, "assets", `${shot.img}.jpg`)]);
  }

  const shots = variant.shots
    .map((shot, i) => `<div class="shot" id="r-shot${i}"><img src="assets/${shot.img}.jpg" alt="" /></div>`)
    .join("\n        ");
  const html = template
    .replaceAll("__ID__", id)
    .replaceAll("__DUR__", String(variant.end.to))
    .replace("__SHOTS__", shots)
    .replace("__LINES__", variant.lines.map(renderLine).join("\n        "))
    .replace("__CTA__", variant.end.cta)
    .replace("__DATA__", JSON.stringify({ shots: variant.shots, lines: variant.lines, end: variant.end }));
  fs.writeFileSync(path.join(dir, "index.html"), html);
  fs.writeFileSync(path.join(dir, "hyperframes.json"), JSON.stringify({
    $schema: "https://hyperframes.heygen.com/schema/hyperframes.json",
    paths: { blocks: "compositions", components: "compositions/components", assets: "assets" },
    authoringSkill: "motion-graphics",
  }, null, 2) + "\n");
  return dir;
}

const only = process.argv.slice(2);
for (const name of only.length ? only : Object.keys(variants)) console.log(build(name));
