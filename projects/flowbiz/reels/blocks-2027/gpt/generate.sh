#!/bin/bash
# Grafiki do rolek tekstowych „System z klocków 2027" — GPT Image przez Codex (image_gen).
# TREŚĆ GENEROWANA AI → rolka z nimi wymaga oznaczenia (art. 50 ust. 4 AI Act).
# Użycie: ./generate.sh [nazwa ...]   (bez argumentów: wszystkie)
set -uo pipefail
cd "$(dirname "$0")"
# Wzór stylu bierzemy z istniejących grafik (kopia tymczasowa, poza gitem)
[ -f style.png ] || cp ../../../assets/higgsfield-grafiki/izometria-biurko-po-orange.png style.png

COMMON='Użyj wbudowanego narzędzia image_gen (nie CLI fallback). Obraz PIONOWY 1024x1536. style.png w bieżącym katalogu = wzór stylu (NIE treści): czyste renderowanie 3D w lekkiej izometrii, matowe materiały, miękkie studyjne światło, prawie czarne tło #0B0B0D z ciepłą pomarańczową poświatą, akcent pomarańczowy #FF6A1A, ciemne grafitowe bryły #1D1D22, premium, minimalizm. BEZWZGLĘDNIE: zero tekstu, zero liter, zero cyfr, zero logotypów i znaków firm w obrazie. Bez ludzi. Główny obiekt w DOLNYCH 60% kadru, górna 1/3 kadru pusta i ciemna (tam pójdzie tekst). Scena:'

prompt() {
  case "$1" in
    a1-tower-collapsing) echo 'krzywa wieża z kilku niepasujących do siebie bloków różnej szerokości i różnego materiału (szary plastik, matowy grafit, przyciemniona czerwień #B8443C), ustawionych jeden na drugim bez podstawy, przechylona, w momencie gdy zaczyna się rozpadać — kilka bloków odrywa się w powietrzu; złącza między blokami nie pasują, z jednego sypią się czerwone iskry.' ;;
    a2-foundation) echo 'jedna szeroka, gruba, idealnie płaska płyta-fundament świecąca od środka pomarańczem #FF6A1A, z czterema równymi wypustkami na górnej powierzchni (jak w klocku), leży na ciemnej posadzce, pod nią mocna pomarańczowa poświata; reszta kadru pusta.' ;;
    a3-tower-on-foundation) echo 'równa, stabilna wieża z pięciu identycznej szerokości ciemnych grafitowych bloków z cienką pomarańczową krawędzią, stojąca na szerszej świecącej pomarańczowej płycie-fundamencie; przez wszystkie bloki od fundamentu do szczytu biegnie pionowa świetlna linia pomarańczowa (połączenie); nad szczytem unosi się szósty blok narysowany tylko przerywanym konturem.' ;;
    b1-premium-stack) echo 'wysoka, smukła, chwiejna wieża z błyszczących, drogich, pięknie wykonanych bloków — każdy z innego luksusowego materiału (szczotkowane aluminium, szkło, czarna ceramika, miedź, karbon), ale każdy innego kształtu i rozmiaru, ustawione na gołej posadzce bez podstawy, wyraźnie przechylone, napięcie tuż przed upadkiem.' ;;
    b2-explosion) echo 'te same luksusowe bloki (aluminium, szkło, ceramika, miedź, karbon) rozlatują się w powietrzu w dramatycznej eksplozji, odłamki i iskry w ciepłej pomarańczy, zatrzymane w ruchu jak w kadrze z szybkiej kamery, ciemne tło.' ;;
    b3-reassembled) echo 'te same luksusowe bloki (aluminium, szkło, ceramika, miedź, karbon) poukładane teraz równo, jeden na drugim, wszystkie tej samej szerokości, zatrzaśnięte na jednym szerokim świecącym pomarańczowym fundamencie; spokojna, stabilna kompozycja, poświata od fundamentu.' ;;
    c1-simple-flow) echo 'kilka (trzy-cztery) eleganckich ciemnych bloczków połączonych cienkimi świecącymi pomarańczowymi liniami w prosty, czytelny przepływ od lewej do prawej, leżących na płaskiej powierzchni; dużo wolnego miejsca; porządek i spokój.' ;;
    c2-tangled-mess) echo 'te same ciemne bloczki rozmnożone w dziesiątki, połączone setkami splątanych, krzyżujących się pomarańczowych linii — przerośnięta, nieczytelna plątanina, która zaczyna przypominać kłębowisko; nadmiar.' ;;
    c3-code-floor) echo 'przekrój: na górze kilka eleganckich bloczków połączonych prostym pomarańczowym przepływem, a pod nimi, pod przeciętą posadzką, widoczna niższa warstwa — gęsta, uporządkowana siatka cienkich świecących linii i ścieżek jak płytka drukowana; obie warstwy stoją na jednym szerokim pomarańczowym fundamencie.' ;;
  esac
}
ALL="a1-tower-collapsing a2-foundation a3-tower-on-foundation b1-premium-stack b2-explosion b3-reassembled c1-simple-flow c2-tangled-mess c3-code-floor"

for n in ${@:-$ALL}; do
  [ -f "$n.png" ] && { echo "skip $n"; continue; }
  ( codex exec --skip-git-repo-check -s workspace-write -C "$PWD" \
      "$COMMON $(prompt "$n") Zapisz wynik w bieżącym katalogu jako $n.png" < /dev/null > "$n.log" 2>&1
    echo "done $n: $( [ -f "$n.png" ] && echo OK || echo BRAK )" ) &
done
wait
