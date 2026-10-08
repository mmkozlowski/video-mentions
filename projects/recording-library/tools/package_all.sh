#!/bin/zsh
# Wszystkie storyboardy × formaty × palety: kontrola + render do final/samples/.
#   tools/package_all.sh            # wszystko
#   tools/package_all.sh ad-11 ad-28
cd "${0:A:h}/.."
boards=("$@")
[[ ${#boards} -eq 0 ]] && boards=(packaging/storyboards/*.json(:t:r))
for b in $boards; do
  python3 tools/package.py "$b" --check --render 2>&1 | grep -E "▣|error\(s\)|Check (passed|failed)|✗|Traceback|Error" | cut -c1-240
done
