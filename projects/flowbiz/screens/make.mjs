#!/usr/bin/env node
// Generuje projekty HyperFrames z jednego źródła na klocek.
//
// Źródło:  screens/<klocek>/scene.html  (jeden HTML, układ zależny od klasy fmt-land / fmt-port)
//          screens/shared/               (arkusz, helpery, fonty, logo — wspólne dla wszystkich)
// Wynik:   build/hf/<klocek>-<format>/   (index.html + assets/ — odtwarzalne, poza gitem)
//
// Dlaczego generator, a nie dwie kopie HTML-a: `check` i `snapshot` widzą tylko index.html
// projektu, a korzeń kompozycji ma stałe data-width/height. Dwa formaty = dwa projekty;
// trzymanie dwóch ręcznych kopii każdej sceny rozjechałoby je przy pierwszej poprawce.
//
// Użycie:  node screens/make.mjs [klocek ...]

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PROJECT = path.resolve(HERE, "..");
const OUT = path.join(PROJECT, "build", "hf");
const SHARED = path.join(HERE, "shared");

export const FORMATS = {
  "16x9": { w: 1920, h: 1080, fmt: "land" },
  "9x16": { w: 1080, h: 1920, fmt: "port" },
};

// Klocki, które mają sens jako nakładka na inny materiał → dodatkowy wariant z alfą.
export const ALPHA = {
  "agent-ai-duplikuje-oferte": ["16x9", "9x16"],
  "stoper-40-do-5": ["16x9", "9x16"],
};

export function scenes() {
  return fs
    .readdirSync(HERE)
    .filter((d) => fs.existsSync(path.join(HERE, d, "scene.html")))
    .sort();
}

export function variants(only) {
  const list = [];
  for (const scene of only && only.length ? only : scenes()) {
    for (const f of Object.keys(FORMATS)) {
      list.push({ scene, f, alpha: false, name: `${scene}-${f}` });
      if ((ALPHA[scene] || []).includes(f)) list.push({ scene, f, alpha: true, name: `${scene}-${f}-alpha` });
    }
  }
  return list;
}

function build(v) {
  const { w, h, fmt } = FORMATS[v.f];
  const src = fs.readFileSync(path.join(HERE, v.scene, "scene.html"), "utf8");
  const html = src
    .replaceAll("__W__", String(w))
    .replaceAll("__H__", String(h))
    .replaceAll("__FMT__", fmt)
    .replaceAll("__HTMLCLASS__", v.alpha ? "alpha-mode" : "")
    .replaceAll("__ID__", v.scene);
  const dir = path.join(OUT, v.name);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "index.html"), html);
  fs.cpSync(SHARED, path.join(dir, "assets"), { recursive: true });
  const local = path.join(HERE, v.scene, "assets");
  if (fs.existsSync(local)) fs.cpSync(local, path.join(dir, "assets"), { recursive: true });
  fs.writeFileSync(
    path.join(dir, "hyperframes.json"),
    JSON.stringify(
      {
        $schema: "https://hyperframes.heygen.com/schema/hyperframes.json",
        registry: "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        paths: { blocks: "compositions", components: "compositions/components", assets: "assets" },
        media: { autoProxy: true },
        authoringSkill: "motion-graphics",
      },
      null,
      2,
    ) + "\n",
  );
  return dir;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const only = process.argv.slice(2);
  for (const v of variants(only)) console.log(path.relative(PROJECT, build(v)));
}
