from course_common import md, code, notebook, write_notebook, exercise, summary


def build():
    nb = notebook(
        "01 – Biztonságkritikus rendszerek, megbízhatóság és kockázat", "1",
        ["hazard, risk, fault és failure fogalmak elkülönítése", "megbízhatóság és rendelkezésre állás számítása", "soros és párhuzamos rendszer értelmezése", "a TK-101 veszélylánc első felépítése"],
        [
            md("""## 1. Mi a mérnöki kérdés?

Egy safety-critical rendszerben nem elég azt kérdezni, hogy működik-e. Négy kérdésből indulunk: **mi romolhat el, milyen valószínűséggel, mi a következmény, és mivel csökkenthető a kockázat?**

Munkadefiníciók:
- **fault:** hibaok vagy hibaállapot;
- **error:** eltérés a kívánt belső állapottól;
- **failure:** a kívánt funkció elvesztése;
- **hazard:** potenciálisan veszélyes állapot;
- **risk:** a bizonytalan események és következményeik mérnöki jellemzése.

Egyszerű oktatási közelítés: $R=P(H)C$. Ez nem univerzális definíció, hanem belépő modell."""),
            md("""## 2. Megbízhatóság kézzel

Legyen $T$ a meghibásodásig eltelt idő. $R(t)=P(T>t)$ és $F(t)=1-R(t)$. Állandó meghibásodási intenzitás esetén:

$$R(t)=e^{-\\lambda t},\qquad F(t)=1-e^{-\\lambda t},\qquad MTTF=1/\\lambda.$$

Számítsuk ki $\\lambda=2\\cdot10^{-4}\,h^{-1}$ mellett az 1000 órás megbízhatóságot."""),
            code("""from math import exp
failure_rate = 2e-4
t = 1000
R_t = exp(-failure_rate*t)
F_t = 1-R_t
print(f"R({t} h)={R_t:.4f}")
print(f"F({t} h)={F_t:.4f}")
print(f"MTTF={1/failure_rate:.0f} h")"""),
            md("""### Mit jelent az eredmény?

Az exponenciális modell **memoryless** és állandó $\\lambda$-t feltételez. Kopás, öregedés vagy periodikus terhelés esetén ez lehet hibás modellfeltevés. A képlet használata előtt ezért mindig a modellérvényességet kell vizsgálni."""),
            code("""times=np.linspace(0,5000,200)
for lam in [1e-4,2e-4,5e-4]:
    plt.plot(times,np.exp(-lam*times),label=f"lambda={lam:g} 1/h")
plt.xlabel("Idő [h]"); plt.ylabel("R(t)"); plt.grid(alpha=.3); plt.legend(); plt.show()"""),
            md("""## 3. Javítható rendszer és rendelkezésre állás

Kétállapotú exponenciális hiba–javítás modellben $A_\\infty=\\mu/(\\lambda+\\mu)$. MTTF/MTTR alakban közelítőleg:

$$A=\\frac{MTTF}{MTTF+MTTR}.$$"""),
            code("""MTTF=2000
MTTR=8
A=MTTF/(MTTF+MTTR)
print(f"Availability={A:.6f} = {A*100:.3f}%")
print(f"Várható nem-rendelkezésre állás évente={(1-A)*8760:.1f} h")"""),
            md("""## 4. Soros és párhuzamos szerkezet

Független komponenseknél: $R_s=R_1R_2$, míg két párhuzamos, azonos funkciót ellátó elemnél $R_p=1-(1-R_1)(1-R_2)$. A párhuzamos képlet csak akkor írja le jól a redundanciát, ha a hibafüggőségeket nem hagyjuk figyelmen kívül."""),
            code("""R1,R2=.98,.97
pd.DataFrame({"struktúra":["soros","párhuzamos"],"R":[R1*R2,1-(1-R1)*(1-R2)]})"""),
            md("""## 5. TK-101: első veszélylánc

A közös esettanulmány egy éghető folyadék fogadó- és tárolórendszere. Fő elemek: **TK-101 tartály, LT-101 szinttávadó, LSHH-101 védelem, XV-101 elzáró, HMI/operator, CMMS/karbantartás, containment és tűzvédelem**.

Első narratív veszélylánc:

**szenzor degradáció → karbantartás elhalasztása → védelem degradáció → high-level challenge → leállítási/beavatkozási hiba → túlfolyás → gyújtás → tűz.**"""),
            code("""p_challenge=.08
p_auto_fail=.015
p_manual_fail=.0592
p_overflow=p_challenge*p_auto_fail*p_manual_fail
print(f"Durva, függetlenséget feltételező P(overflow)={p_overflow:.8f}")"""),
            exercise(["Növeld a failure rate-et 5e-4-re és értelmezd R(1000)-et.", "Számíts két R=0.95 elem soros és párhuzamos konfigurációját.", "Sorolj fel két okot, amiért a TK-101 durva függetlenségi feltételezése hibás lehet."]),
            summary("A megbízhatóság a funkció teljesítését, a rendelkezésre állás a javíthatóságot is figyelembe veszi; a kockázat pedig valószínűséget és következményt kapcsol össze. A következő tanegységben a **mi romolhat el?** kérdést PHA, FMEA és HAZOP segítségével strukturáljuk."),
        ])
    write_notebook("01_BIZTONSAGKRITIKUS_ALAPOK.ipynb", nb)

    nb = notebook(
        "02 – PHA, FMEA és HAZOP: strukturált veszélyazonosítás", "2",
        ["PHA hazard list készítése", "FMEA failure mode–effect–cause lánc felépítése", "RPN kiszámítása és korlátainak felismerése", "HAZOP guideword alapú eltérések létrehozása"],
        [
            md("""## 1. Három módszer – három nézőpont

- **PHA:** magas szinten milyen veszélyek vannak?
- **FMEA:** hogyan hibásodhat meg egy elem/funkció, és mi a hatás?
- **HAZOP:** milyen tervezési szándéktól való eltérések jöhetnek létre, mi okozza őket és mi a következmény?

A cél nem három független lista, hanem később összekapcsolható traceability."""),
            md("""## 2. PHA – TK-101 első hazard list

A PHA korai, magas szintű elemzés. Példák: overflow, ignition/fire, loss of containment. A prioritási kategóriák szervezetspecifikusak; itt csak oktatási címkéket használunk."""),
            code("""pha=pd.DataFrame([
 {"hazard":"Overflow","cause":"Level protection ineffective","consequence":"Release","safeguard":"LSHH+XV+operator","priority":"high"},
 {"hazard":"Fire","cause":"Release + ignition","consequence":"Fire escalation","safeguard":"containment+fire protection","priority":"high"},
 {"hazard":"Loss of containment","cause":"Tank/connection integrity loss","consequence":"Release","safeguard":"inspection+containment","priority":"medium"}])
pha"""),
            md("""## 3. FMEA és RPN

Az FMEA tipikus lánca: **function → failure mode → effect → cause → control → rating → action**. Klasszikus oktatási RPN:

$$RPN=S\\times O\\times D.$$

A skálákat előre definiálni kell. **Fix RPN elfogadási küszöböt nem tekintünk univerzálisnak.** Azonos RPN mögött eltérő severity profil lehet."""),
            code("""def rpn(S,O,D):
    if not all(1<=int(x)<=10 for x in [S,O,D]): raise ValueError("S/O/D: 1..10")
    return int(S)*int(O)*int(D)

examples=pd.DataFrame([
 {"mode":"A","S":10,"O":2,"D":4},
 {"mode":"B","S":5,"O":4,"D":4},
 {"mode":"C","S":8,"O":5,"D":2}])
examples["RPN"]=examples.apply(lambda r:rpn(r.S,r.O,r.D),axis=1)
examples"""),
            md("""### Azonos RPN ≠ azonos kockázati profil

`10×2×4` és `5×4×4` egyaránt 80. Safety kontextusban a severity sokszor önálló prioritást érdemel. Mutassuk meg a severity-first rendezést."""),
            code("""examples.sort_values(["S","O","D","RPN"],ascending=False)"""),
            md("""## 4. TK-101 FMEA

Az S/O/D értékek itt **szintetikus oktatási értékek**, nem üzemi bizonyítékok."""),
            code("""fmea=pd.DataFrame([
 {"component":"LT-101","failure_mode":"failed low / bias","effect":"high level detected late","S":9,"O":4,"D":6},
 {"component":"LSHH-101","failure_mode":"fail on demand","effect":"trip not initiated","S":10,"O":2,"D":7},
 {"component":"XV-101","failure_mode":"fail on demand","effect":"inflow continues","S":10,"O":2,"D":6},
 {"component":"HMI/operator","failure_mode":"alarm missed","effect":"no timely manual recovery","S":9,"O":3,"D":5}])
fmea["RPN"]=fmea.apply(lambda r:rpn(r.S,r.O,r.D),axis=1)
fmea.sort_values("RPN",ascending=False)"""),
            md("""## 5. HAZOP: guideword + parameter → deviation

A `TK-101 filling` node-on a `LEVEL` és `FLOW` paramétereket vizsgáljuk. Guideword példák: NO, MORE, LESS, REVERSE, OTHER THAN. Nem minden kombináció értelmes; a módszer célja a strukturált mérnöki gondolkodás."""),
            code("""hazop=pd.DataFrame([
 {"node":"TK-101 filling","parameter":"LEVEL","guideword":"MORE","deviation":"High level","causes":"excess inflow; LT failed low; shutdown failure","consequences":"overflow/release","safeguards":"LAH; LSHH; XV; operator"},
 {"node":"TK-101 filling","parameter":"FLOW","guideword":"MORE","deviation":"Excess feed flow","causes":"pump/control fault","consequences":"level rises faster","safeguards":"flow/level monitoring; trip"},
 {"node":"TK-101 shutdown","parameter":"SHUTDOWN","guideword":"NO","deviation":"No effective shutdown","causes":"LSHH/XV fail on demand","consequences":"inflow continues at high level","safeguards":"operator intervention"}])
hazop"""),
            md("""## 6. Traceability a három módszer között

A következő lánc már közvetlen bemenetet adhat a Fault Tree Analysishez:

**PHA: Overflow → FMEA: LT failed low / LSHH FOD / XV FOD → HAZOP: MORE LEVEL / NO SHUTDOWN → FTA basic events.**"""),
            code("""trace=pd.DataFrame([
 {"PHA hazard":"Overflow","FMEA mode":"LT-101 failed low","HAZOP deviation":"MORE LEVEL","next":"FTA basic event"},
 {"PHA hazard":"Overflow","FMEA mode":"LSHH fail on demand","HAZOP deviation":"NO SHUTDOWN","next":"FTA basic event"},
 {"PHA hazard":"Overflow","FMEA mode":"XV fail on demand","HAZOP deviation":"NO SHUTDOWN","next":"FTA basic event"}])
trace"""),
            exercise(["Adj FMEA-sort a maintenance overdue állapothoz: komponenshiba vagy szervezeti/process failure mode?", "Keress két azonos RPN-jű, de eltérő severity-jű sort.", "Adj új HAZOP sort LESS FLOW vagy REVERSE FLOW guideworddal, ha mérnökileg értelmes.", "Jelöld, mely safeguardok jelenjenek meg a következő FTA-ban."]),
            summary("PHA veszélyeket, FMEA failure mode-okat, HAZOP eltéréseket strukturál. A következő lépés a kombinációs logika: **mely eseménykombinációk elegendők az overflow top eventhez?**"),
        ])
    write_notebook("02_PHA_FMEA_HAZOP.ipynb", nb)

    nb = notebook(
        "03 – Fault Tree Analysis: a logikai modelltől a minimal cut setig", "3",
        ["AND/OR kapuk valószínűségi értelmezése", "fault tree reprezentálása Pythonban", "rekurzív kiértékelő felépítése", "minimal cut set és Birnbaum importance értelmezése"],
        [
            md("""## 1. FTA gondolkodás

A kérdés: **mely alap-események vagy eseménykombinációk elegendők a top event bekövetkezéséhez?**

Független bemenetek esetén: AND → $\\prod p_i$, OR → $1-\\prod(1-p_i)$. A függetlenség itt explicit modellfeltevés."""),
            code("""def AND(*p): return float(np.prod(p))
def OR(*p): return 1-float(np.prod([1-x for x in p]))
p_lshh,p_xv=.01,.005
print("AND",AND(p_lshh,p_xv)); print("OR",OR(p_lshh,p_xv))"""),
            md("""## 2. Első explicit fault tree

Először nem használunk kész libraryt. A teljes logika látható `dict` struktúrában."""),
            code("""tree={"top_event":"AUTO_FAIL","nodes":{
 "AUTO_FAIL":{"type":"OR","children":["LSHH_FOD","XV_FOD"]},
 "LSHH_FOD":{"type":"BASIC","probability":.01},
 "XV_FOD":{"type":"BASIC","probability":.005}}}
tree"""),
            md("""## 3. Rekurzív evaluator

BASIC esetén probability-t adunk vissza; gate esetén előbb a gyermekeket értékeljük ki."""),
            code("""def evaluate(tree,node_id=None):
    node_id=node_id or tree["top_event"]
    node=tree["nodes"][node_id]
    typ=node["type"]
    if typ=="BASIC": return float(node["probability"])
    ps=[evaluate(tree,c) for c in node["children"]]
    if typ=="AND": return float(np.prod(ps))
    if typ=="OR": return 1-float(np.prod([1-p for p in ps]))
    raise ValueError(typ)
print(evaluate(tree))"""),
            md("""## 4. TK-101 overflow tree

Oktatási modell:

`OVERFLOW = HIGH_LEVEL_CHALLENGE AND AUTO_FAIL AND MANUAL_FAIL`

`AUTO_FAIL = LSHH_FOD OR XV_FOD`

`MANUAL_FAIL = LT101_LOW OR OPERATOR_MISS`"""),
            code("""tk={"top_event":"OVERFLOW","nodes":{
 "OVERFLOW":{"type":"AND","children":["CHALLENGE","AUTO_FAIL","MANUAL_FAIL"]},
 "AUTO_FAIL":{"type":"OR","children":["LSHH_FOD","XV_FOD"]},
 "MANUAL_FAIL":{"type":"OR","children":["LT101_LOW","OPERATOR_MISS"]},
 "CHALLENGE":{"type":"BASIC","probability":.08},
 "LSHH_FOD":{"type":"BASIC","probability":.01},
 "XV_FOD":{"type":"BASIC","probability":.005},
 "LT101_LOW":{"type":"BASIC","probability":.02},
 "OPERATOR_MISS":{"type":"BASIC","probability":.04}}}
print(f"P(OVERFLOW)={evaluate(tk):.8f}")"""),
            md("""## 5. Minimal cut set kézzel és algoritmikusan

OR kapunál a gyermekek cut setjeit egyesítjük; AND kapunál a gyermekek cut setjeinek kombinációit képezzük, majd eltávolítjuk a nem minimális szuperszetteket."""),
            code("""from itertools import product
def cut_sets(tree,node_id=None):
    node_id=node_id or tree["top_event"]; node=tree["nodes"][node_id]
    if node["type"]=="BASIC": return [frozenset([node_id])]
    groups=[cut_sets(tree,c) for c in node["children"]]
    cand=[s for g in groups for s in g] if node["type"]=="OR" else [frozenset().union(*x) for x in product(*groups)]
    uniq=sorted(set(cand),key=lambda s:(len(s),sorted(s))); out=[]
    for s in uniq:
        if not any(x<=s for x in out): out.append(s)
    return out
for s in cut_sets(tk): print(sorted(s))"""),
            md("""## 6. Birnbaum importance

Oktatási érzékenységi mérő: az adott basic eventet egyszer biztosan hibásnak (`p=1`), egyszer biztosan működőnek (`p=0`) állítjuk, és vesszük a top-event probability különbségét."""),
            code("""from copy import deepcopy
def birnbaum(tree):
    out={}
    for e,n in tree["nodes"].items():
        if n["type"]!="BASIC": continue
        a,b=deepcopy(tree),deepcopy(tree)
        a["nodes"][e]["probability"]=1.; b["nodes"][e]["probability"]=0.
        out[e]=evaluate(a)-evaluate(b)
    return pd.Series(out).sort_values(ascending=False)
imp=birnbaum(tk); display(imp)
imp.plot(kind="barh"); plt.xlabel("Birnbaum importance"); plt.show()"""),
            md("""## 7. Ellenőrzés a tesztelt `safetycourse.fta` modullal

Most, hogy az algoritmust felépítettük, a közös modul az automatizálást és a későbbi integrációt szolgálja."""),
            code("""from safetycourse.fta import top_event_probability,minimal_cut_sets
print(top_event_probability(tk))
print([sorted(x) for x in minimal_cut_sets(tk)])"""),
            md("""## 8. Korlátok

A statikus FTA nem kezeli természetesen az eseménysorrendet és az időt. A gate-inputok függetlensége nem általános: shared basic event és common-cause failure külön modellezést igényel."""),
            exercise(["Növeld LT101_LOW értékét 0.10-re és számítsd újra a top eventet.", "Mely basic event Birnbaum importance-a a legnagyobb és miért?", "Adj COMMON_POWER_FAIL eseményt, amely egyszerre érintheti LSHH és XV funkciót; miért nem helyes két független ágra másolni?", "Rajzold fel a négy minimal cut setet kézzel."]),
            summary("Az FTA formalizálja a kvalitatív veszélyelemzésből származó kombinációs logikát. A következő tanegység azt vizsgálja, hogyan származtatható ez a struktúra **rendszermodellből**, determinisztikus és validálható szabályokkal."),
        ])
    write_notebook("03_FTA.ipynb", nb)


if __name__ == "__main__":
    build()
