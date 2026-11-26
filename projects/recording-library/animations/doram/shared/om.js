// Powłoka Open Mercato — odpowiednik shell()/table()/btn()/status() z tools/om_screens.py (ten sam HTML, te same klasy .omx-*).
(function () {
  const I = (n, c) => window.omIcon(n, c);
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  window.OM = {
    I, esc,
    status: (text, kind, cls = "") => `<span class="omx-st ${kind}${cls ? " " + cls : ""}">${esc(text)}</span>`,
    btn: (text, ic, primary, cls = "", id = "") =>
      `<span ${id ? `id="${id}"` : ""} class="omx-btn${primary ? " pri" : ""}${cls ? " " + cls : ""}">${ic ? I(ic) : ""}${esc(text)}</span>`,
    shell({ tenant, role, groups, active, crumbs, body, who = "", extra = "" }) {
      let nav = "";
      groups.forEach(([title, links], i) => {
        if (i) nav += '<div class="omx-sep"></div>';
        if (title) nav += `<div class="omx-grp">${esc(title)}${I("chevdown")}</div>`;
        nav += links.map(([ic, label]) => `<div class="omx-link${label === active ? " on" : ""}">${I(ic)}${esc(label)}</div>`).join("");
      });
      const trail = I("home") + crumbs.map((c, k) => `${I("chevright")}${k === crumbs.length - 1 ? `<b>${esc(c)}</b>` : esc(c)}`).join("");
      const initials = who.split(" ").slice(0, 2).map((w) => w[0]).join("").toUpperCase();
      return `<div class="omx-win"><div class="omx-side"><div class="omx-org"><i>${esc(tenant[0])}</i><div><b>${esc(tenant)}</b><span>${esc(role)}</span></div></div>` +
        `<div class="omx-find">${I("search")}Szukaj…</div>${nav}</div><div class="omx-main"><div class="omx-top">${trail}` +
        `<span class="r"><span class="omx-ai">${I("sparkles")}AI <kbd>⌘L</kbd></span>${I("bell")}${who ? `<span class="omx-who"><i>${initials}</i>${esc(who)}</span>` : ""}</span></div>` +
        `<div class="omx-body">${body}</div>${extra}</div></div>`;
    },
    GROUPS: [["Sprzedaż", [["cart", "Zamówienia"], ["users", "Kontrahenci"]]],
             ["Produkcja", [["factory", "Zlecenia"], ["tag", "Etykiety"]]],
             ["Katalog", [["package", "Produkty"], ["book", "Słownik nazw"]]]],
  };
})();
