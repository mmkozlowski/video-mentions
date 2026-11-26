// Wspólne klocki „makiety, która sama się klika” — kursor, kliknięcie, pisanie, klawisze, arkusz.
// Wszystko jest funkcją czasu jednej, zapauzowanej osi (seek-safe): pozycje liczone z offsetLeft/offsetTop
// (bez transformów), więc wynik nie zależy od tego, w którym momencie osi liczymy układ.
(function () {
  const CURSOR_SVG =
    '<svg viewBox="0 0 24 24"><path d="M4 2 L4 19 L8.6 14.8 L11.6 21.4 L14.6 20 L11.7 13.6 L18 13.4 Z" fill="#fff" stroke="#0e1f1a" stroke-width="1.6" stroke-linejoin="round"/></svg>';

  function sheet(target, { cols, rows, widths, header = true, startRow = 1 }) {
    // Arkusz z literami kolumn i numerami wierszy. rows[0] to wiersz nagłówka kontrahenta.
    const letters = "ABCDEFGHIJKLMNOP";
    let html = '<table class="grid"><colgroup><col style="width:46px">';
    widths.forEach((w) => (html += `<col style="width:${w}px">`));
    html += "</colgroup><tr><th class='rn'></th>";
    cols.forEach((_, i) => (html += `<th data-col="${i}">${letters[i]}</th>`));
    html += "</tr>";
    rows.forEach((r, ri) => {
      const cls = header && ri === 0 ? "h" : "";
      html += `<tr class="${cls}" data-row="${ri}"><td class="rn">${ri + startRow}</td>`;
      r.forEach((c, ci) => {
        const spec = cols[ci] || "";
        html += `<td class="${spec}" data-r="${ri}" data-c="${ci}">${c}</td>`;
      });
      html += "</tr>";
    });
    html += "</table>";
    const holder = document.createElement("div");
    holder.innerHTML = html;
    const table = holder.firstChild;
    target.insertBefore(table, target.firstChild);
    return table;
  }

  function create(tl, stage) {
    const q = (s) => (typeof s === "string" ? stage.querySelector(s) : s);
    const box = (sel) => {
      const el = q(sel);
      if (!el) throw new Error("brak elementu: " + sel);
      let x = 0, y = 0, e = el;
      while (e && e !== stage) { x += e.offsetLeft; y += e.offsetTop; e = e.offsetParent; }
      return { x, y, w: el.offsetWidth, h: el.offsetHeight };
    };
    const at = (sel, dx = 0.5, dy = 0.5) => { const b = box(sel); return { x: b.x + b.w * dx, y: b.y + b.h * dy }; };

    const cursor = document.createElement("div");
    cursor.id = "cursor";
    cursor.innerHTML = CURSOR_SVG + '<div class="ripple"></div>';
    stage.appendChild(cursor);

    const api = {
      q, box, at,
      cell: (win, r, c) => `${win} td[data-r="${r}"][data-c="${c}"]`,
      place(sel, t = 0, dx, dy) { const p = typeof sel === "object" && "x" in sel ? sel : at(sel, dx, dy); tl.set(cursor, { x: p.x, y: p.y }, t); },
      move(sel, t, d = 0.55, dx, dy) {
        const p = typeof sel === "object" && sel !== null && "x" in sel ? sel : at(sel, dx, dy);
        tl.to(cursor, { x: p.x, y: p.y, duration: d, ease: "power2.inOut" }, t);
        return t + d;
      },
      click(t) {
        tl.to(cursor.firstChild, { scale: 0.84, duration: 0.07, transformOrigin: "20% 10%", ease: "power2.out" }, t);
        tl.to(cursor.firstChild, { scale: 1, duration: 0.12, ease: "power2.out" }, t + 0.07);
        tl.fromTo(cursor.querySelector(".ripple"), { scale: 0.3, opacity: 0.9 }, { scale: 1.5, opacity: 0, duration: 0.42, ease: "power2.out", immediateRender: false }, t);
        return t + 0.15;
      },
      moveClick(sel, t, d = 0.55, dx, dy) { api.move(sel, t, d, dx, dy); api.click(t + d); return t + d + 0.15; },
      // pisanie litera po literze; tekst w data-text, element startowo pusty
      type(sel, t, cps = 16) {
        const el = q(sel);
        const text = el.dataset.text != null ? el.dataset.text : el.textContent;
        el.dataset.text = text;
        el.textContent = "";
        const proxy = { n: 0 };
        const d = Math.max(0.05, text.length / cps);
        tl.to(proxy, { n: text.length, duration: d, ease: "none",
          onUpdate() { el.textContent = text.slice(0, Math.round(proxy.n)); } }, t);
        tl.set(proxy, { n: 0 }, 0);
        return t + d;
      },
      // klawisz w lewym dolnym rogu: show(id, t, dur)
      key(sel, t, d = 0.9) {
        tl.fromTo(sel, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.14, ease: "power2.out", immediateRender: false }, t);
        tl.to(sel, { opacity: 0, duration: 0.18 }, t + d);
        return t + d;
      },
      // okno na wierzch + delikatny „pop”
      front(sel, t, z) {
        tl.set(sel, { zIndex: z }, t);
        tl.fromTo(sel, { scale: 0.985 }, { scale: 1, duration: 0.22, ease: "power2.out", immediateRender: false }, t);
      },
      // zaznaczenie komórki: obramowanie dopasowane do komórki (każde .selbox jest własnym elementem)
      selectBox(boxSel, cellSel, t, hold) {
        const b = box(cellSel), host = q(boxSel).offsetParent;
        let hx = 0, hy = 0, e = host; while (e && e !== stage) { hx += e.offsetLeft; hy += e.offsetTop; e = e.offsetParent; }
        tl.set(boxSel, { x: b.x - hx - 1, y: b.y - hy - 1, width: b.w + 2, height: b.h + 2, opacity: 1 }, t);
        if (hold) tl.set(boxSel, { opacity: 0 }, t + hold);
      },
      // wartość pokazana w pasku formuły
      text(sel, value, t) { tl.set(q(sel), { textContent: value }, t); },
      counter(sel, from, to, t, d, fmt = (v) => Math.round(v).toString(), ease = "none") {
        const el = q(sel); const proxy = { v: from };
        tl.to(proxy, { v: to, duration: d, ease, onUpdate() { el.textContent = fmt(proxy.v); } }, t);
        tl.set(proxy, { v: from }, 0);
      },
    };
    return api;
  }

  // kod kreskowy z tekstu — deterministyczny wzór szerokości kresek (bez Math.random)
  function barcode(target, text, height, unit = 2) {
    let seed = 0; for (const ch of text) seed = (seed * 31 + ch.charCodeAt(0)) >>> 0;
    const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
    let html = '<div class="bars" style="height:' + height + 'px">';
    const pattern = [2, 1, 2, 1];
    for (let i = 0; i < 46; i++) {
      const w = i < 3 || i > 42 ? pattern[i % 4] : 1 + Math.floor(rnd() * 4);
      const gap = 1 + Math.floor(rnd() * 3);
      html += `<u style="width:${w * unit}px;margin-right:${gap * unit}px"></u>`;
    }
    html += "</div>";
    target.innerHTML = html;
    return target.querySelectorAll("u");
  }


  // arkusz z kolumn-bloków: cols = [{key, title, w, cls, cells}], prefix → id kolumn: <prefix>-col-<key>, komórek: <prefix>-<key>-<r>
  function colsheet(target, prefix, cols, rows) {
    const letters = "ABCDEFGHIJKLMNOP";
    let html = `<div class="cs-col rn" style="left:0;width:50px"><div class="L"></div>`;
    for (let r = 0; r <= rows; r++) html += `<div>${r + 1}</div>`;
    html += "</div>";
    let x = 50;
    cols.forEach((c, i) => {
      html += `<div class="cs-col ${c.cls || ""}" id="${prefix}-col-${c.key}" style="left:${x}px;width:${c.w}px">`;
      html += `<div class="L" id="${prefix}-L-${c.key}">${c.letter || letters[i]}</div><div class="H" id="${prefix}-${c.key}-h">${c.title}</div>`;
      for (let r = 0; r < rows; r++) html += `<div id="${prefix}-${c.key}-${r + 1}">${(c.cells && c.cells[r]) || ""}</div>`;
      html += "</div>";
      if (!c.overlay) x += c.w;
    });
    const holder = document.createElement("div");
    holder.innerHTML = html;
    while (holder.firstChild) target.appendChild(holder.firstChild);
  }

  window.Kit = { create, sheet, colsheet, barcode };
})();
