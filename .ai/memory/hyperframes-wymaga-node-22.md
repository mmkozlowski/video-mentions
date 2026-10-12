---
name: hyperframes-wymaga-node-22
description: hyperframes@latest odmawia startu na Node 20 (domyślny w nvm) — wołać z PATH na v22.22.2
metadata:
  type: reference
---

`npx hyperframes@latest …` od wersji 0.8.14x kończy się komunikatem
„HyperFrames requires Node.js >= 22 (current: 20.19.4)”. Domyślny `node` w nvm na tej
maszynie to 20.19.4; obok są v22.22.2 i v24.14.1.

Wołaj z `PATH=$HOME/.nvm/versions/node/v22.22.2/bin:$PATH` — tak robi `hf()`
w `projects/recording-library/tools/package.py`. Nie przestawiaj globalnie `nvm alias default`,
bo inne repo (np. adresflow-v2) mogą trzymać się 20.

**Why:** skrypty z `screens/render.sh` w starszych projektach wołają `npx hyperframes@latest`
bez wersji — po aktualizacji CLI przestaną działać bez żadnej zmiany w repo.

**How to apply:** przy błędzie „requires Node.js >= 22” dopisz PATH w skrypcie, nie zmieniaj
wersji globalnej. Powiązane: [[ekran-produktu-hyperframes]].
