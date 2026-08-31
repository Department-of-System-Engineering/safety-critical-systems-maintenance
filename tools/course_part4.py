from course_common import md, code, notebook, write_notebook, exercise, summary


def build():
    nb=notebook(
        "10 – Hibadiagnosztika és szenzoradat-alapú állapotbecslés", "11",
        ["process/sensor/actuator fault elkülönítése", "residual képzése referenciajelből", "threshold és EWMA detektor felépítése", "sensitivity/specificity és detection delay értelmezése", "diagnosztikai evidencia Bayes-frissítéshez előkészítése"],
        [
            md("""## 1. Detection – isolation – identification

A diagnosztika három egymásra épülő kérdése: **van-e fault? hol van? milyen típusú/mértékű?**

Példák: process fault (betáplálási rendellenesség), sensor fault (LT-101 bias/drift/stuck), actuator fault (XV-101 nem zár), illetve model fault (a referencia-modell nem írja le jól a valós folyamatot)."""),
            md("""## 2. TK-101 szintetikus adatsor

A repository `sensor_data.csv` fájlja oktatási célú szintetikus adat. A `true_level_pct` referencia csak demonstráció; valós rendszerben ‘true’ állapot tipikusan nem ismert közvetlenül."""),
            code("""path=ROOT/'data'/'pundit_case'/'sensor_data.csv'; df=pd.read_csv(path); df.head()"""),
            code("""plt.plot(df.time_min,df.true_level_pct,label='reference'); plt.plot(df.time_min,df.lt101_measured_pct,label='LT-101',alpha=.8); plt.xlabel('time [min]'); plt.ylabel('level [%]'); plt.legend(); plt.grid(alpha=.3); plt.show()"""),
            md("""## 3. Residual

Egyszerű residual: $r(t)=y_{measured}(t)-y_{expected}(t)$. Negatív, növekvő abszolút residual failed-low/bias jellegű hibára utalhat, de residual önmagában nem bizonyítja az okot."""),
            code("""df['residual']=df.lt101_measured_pct-df.true_level_pct
plt.plot(df.time_min,df.residual); plt.axhline(0,ls='--'); plt.xlabel('time [min]'); plt.ylabel('residual'); plt.grid(alpha=.3); plt.show()"""),
            md("""## 4. Threshold detector

Első detektor: fault evidence, ha $r(t)\le -3$. A küszöb szintetikus oktatási paraméter."""),
            code("""threshold=-3.; df['detected']=df.residual<=threshold
pd.crosstab(df.fault_active.astype(bool),df.detected,rownames=['fault'],colnames=['detected'])"""),
            md("""## 5. Diagnosztikai metrikák

$TPR=TP/(TP+FN)$ (sensitivity/recall), $TNR=TN/(TN+FP)$ (specificity). Safety esetben a false negative és false positive költsége nem azonos."""),
            code("""def metrics(y,p):
 y=np.asarray(y,bool); p=np.asarray(p,bool); tp=np.sum(y&p); tn=np.sum(~y&~p); fp=np.sum(~y&p); fn=np.sum(y&~p)
 return {'TP':tp,'TN':tn,'FP':fp,'FN':fn,'sensitivity':tp/(tp+fn) if tp+fn else np.nan,'specificity':tn/(tn+fp) if tn+fp else np.nan}
metrics(df.fault_active,df.detected)"""),
            md("""## 6. Threshold trade-off

Sweepeljük a thresholdot: szigorúbb küszöb csökkentheti a false positive-okat, de növelheti a missed detectiont."""),
            code("""rows=[]
for th in np.linspace(-.5,-8,50): rows.append({'threshold':th,**metrics(df.fault_active,df.residual<=th)})
perf=pd.DataFrame(rows); plt.plot(perf.threshold,perf.sensitivity,label='sensitivity'); plt.plot(perf.threshold,perf.specificity,label='specificity'); plt.legend(); plt.grid(alpha=.3); plt.show()"""),
            md("""## 7. EWMA

$z_t=\\alpha r_t+(1-\\alpha)z_{t-1}$. Kisebb $\\alpha$ simább jelet ad, de késleltetheti a detektálást."""),
            code("""def ewma(x,alpha=.12):
 x=np.asarray(x,float); z=np.empty_like(x); z[0]=x[0]
 for i in range(1,len(x)): z[i]=alpha*x[i]+(1-alpha)*z[i-1]
 return z
df['ewma']=ewma(df.residual); plt.plot(df.time_min,df.residual,alpha=.35); plt.plot(df.time_min,df.ewma); plt.axhline(-3,ls='--'); plt.grid(alpha=.3); plt.show()"""),
            md("""## 8. Detection delay

A sensitivity mellett számít, hogy a fault kezdete után mikor születik evidencia."""),
            code("""fault_start=df.loc[df.fault_active.eq(1),'time_min'].min(); first=df.loc[df.ewma.le(-3),'time_min'].min(); print('fault start',fault_start,'first detection',first,'delay',first-fault_start)"""),
            md("""## 9. Diagnosztikai evidencia → Bayes likelihood

A detector sensitivity és false-positive rate lehet $P(E|F)$ és $P(E|\\neg F)$ becslés. Ugyanazon adaton kalibrált és értékelt detector optimista; kutatásban train/validation/test vagy független validáció szükséges."""),
            code("""m=metrics(df.fault_active,df.detected); sens=m['sensitivity']; fp=1-m['specificity']; prior=.02
post=sens*prior/(sens*prior+fp*(1-prior)) if fp>0 else 1.
print({'sensitivity':sens,'false_positive':fp,'posterior_if_alarm':post})"""),
            code("""from safetycourse.diagnosis import residual,threshold_detector,ewma as lib_ewma,binary_metrics
r=residual(df.lt101_measured_pct,df.true_level_pct); pred=threshold_detector(r,-3.,direction='low'); print(binary_metrics(df.fault_active,pred)); assert np.allclose(lib_ewma(r,.12),df.ewma)"""),
            exercise(["Állíts alpha=0.05, 0.2 és 0.5 értéket és hasonlíts detection delay-t.", "Válassz thresholdot legalább 0.90 sensitivity mellett, majd add meg specificity-t.", "Növeld a fault priort 0.10-re és számíts posteriort.", "Írd le, valós folyamatban mivel helyettesíthető a true_level referencia."]),
            summary("A diagnosztika szenzoradatból evidenciát állít elő. A következő tanegység ezt az evidenciát **időben változó kockázattá és maintenance decision inputtá** alakítja."),
        ])
    write_notebook("10_HIBADIAGNOSZTIKA.ipynb",nb)

    nb=notebook(
        "11 – Dinamikus kockázat és intelligens risk-based maintenance", "12",
        ["statikus és dinamikus risk estimate elkülönítése", "szenzorevidencia time-dependent probability-vá alakítása", "dynamic FTA risk trend számítása", "maintenance now/wait trigger expected-cost alapján"],
        [
            md("""## 1. Statikus prior → dinamikus risk

A 3. notebookban egyetlen $P(OVERFLOW)$ számot kaptunk. Üzem közben az evidencia változik, ezért $P(H|E_{0:t})$ időfüggő. A digitálisiker-alapú döntéstámogatás egyik lényege, hogy a modellállapot és evidence rendszeresen frissüljön."""),
            code("""df=pd.read_csv(ROOT/'data'/'pundit_case'/'sensor_data.csv'); df['residual']=df.lt101_measured_pct-df.true_level_pct"""),
            md("""## 2. Residual → probability mapping – explicit modellfeltevés

Oktatási demonstrációban sigmoid mappinget használunk: nagy negatív residual → magasabb sensor-fault probability.

**Ez nem univerzális fizikai törvény.** A mappinget valós alkalmazásban kalibrálni, validálni és uncertainty-vel ellátni kell."""),
            code("""def logistic(x): return 1/(1+np.exp(-x))
def residual_to_p(r,center=-2.5,scale=.8,p_min=.002,p_max=.6):
 score=logistic(-(r-center)/scale); return p_min+(p_max-p_min)*score
df['p_sensor']=residual_to_p(df.residual)
plt.plot(df.time_min,df.p_sensor); plt.xlabel('time [min]'); plt.ylabel('P(sensor fault | evidence)'); plt.grid(alpha=.3); plt.show()"""),
            md("""## 3. Kontextus: maintenance overdue

Oktatási modellben overdue állapot növelheti a prior oddsot. Ezt szintén explicit modellfeltevésként kezeljük, nem automatikus oksági igazságként."""),
            code("""overdue=np.asarray(df.maintenance_overdue,dtype=bool)
odds=df.p_sensor/(1-df.p_sensor); odds_adj=odds*np.where(overdue,2.0,1.0); df['p_sensor_context']=odds_adj/(1+odds_adj)
plt.plot(df.time_min,df.p_sensor,label='evidence only'); plt.plot(df.time_min,df.p_sensor_context,label='+ overdue context'); plt.legend(); plt.grid(alpha=.3); plt.show()"""),
            md("""## 4. Dynamic FTA

A statikus `LT101_LOW` probability helyére időfüggő posterior kerül. A többi input itt fix marad, így láthatóvá válik az evidence contribution."""),
            code("""p_ch=.08; p_lshh=.01; p_xv=.005; p_op=.04; p_auto=1-(1-p_lshh)*(1-p_xv)
def p_overflow(p_sensor): return p_ch*p_auto*(1-(1-p_sensor)*(1-p_op))
df['p_overflow']=p_overflow(df.p_sensor_context)
plt.semilogy(df.time_min,df.p_overflow); plt.xlabel('time [min]'); plt.ylabel('dynamic P(overflow)'); plt.grid(alpha=.3); plt.show()"""),
            md("""## 5. Risk = probability × consequence

Ha a consequence proxy 50 M HUF, a várható veszteség idősora csak monetáris döntési dimenzió. Safety constraints ettől függetlenül is előírhatnak azonnali beavatkozást."""),
            code("""C=50_000_000; df['expected_consequence']=df.p_overflow*C
plt.plot(df.time_min,df.expected_consequence); plt.ylabel('expected consequence proxy [HUF]'); plt.xlabel('time [min]'); plt.grid(alpha=.3); plt.show()"""),
            md("""## 6. Maintenance trigger

Maintain now vs next opportunity. A döntési küszöb abból adódik, mikor lesz a várakozás expected costja nagyobb."""),
            code("""Cm=250_000; prod_now=800_000; prod_window=100_000; p_after=.001
cost_now=Cm+prod_now+p_after*C
cost_wait=Cm+prod_window+df.p_overflow*C
df['maintain_now_cheaper']=cost_now<cost_wait
first=df.loc[df.maintain_now_cheaper,'time_min'].min(); print('first economic trigger [min]=',first,'cost now=',cost_now)"""),
            code("""plt.plot(df.time_min,cost_wait,label='wait'); plt.axhline(cost_now,ls='--',label='maintain now'); plt.xlabel('time [min]'); plt.ylabel('expected cost [HUF]'); plt.legend(); plt.grid(alpha=.3); plt.show()"""),
            md("""## 7. Döntési lánc és traceability

`sensor data → residual → diagnostic model → posterior fault probability → FTA/Markov risk → consequence model → maintenance decision`.

Minden nyílnál dokumentálni kell: modellverzió, kalibrációs adat, időbélyeg, uncertainty, assumption és responsible component."""),
            code("""pd.DataFrame([
 {'step':'sensor→residual','assumption':'reference level meaningful'},
 {'step':'residual→P(fault)','assumption':'calibrated evidence mapping'},
 {'step':'P(fault)→FTA','assumption':'static gate structure valid'},
 {'step':'risk→decision','assumption':'cost proxy and constraints valid'}])"""),
            md("""## 8. Amit nem szabad automatikusan állítani

ARIMA/ML forecast threshold-crossing probability nem válik automatikusan FMEA occurrence pontszámmá vagy Markov transition rate-té. Ehhez külön kalibrációs modell kell. Ugyanez igaz residual score → failure probability mappingre."""),
            exercise(["Változtasd a sigmoid center/scale paramétereit és figyeld a risk trendet.", "Kapcsold ki az overdue odds multipliert.", "Duplázd consequence értékét és keresd az új economic trigger időt.", "Tervezz validációs kísérletet a residual→P(fault) mapping kalibrálására."]),
            summary("A dinamikus risk pipeline a diagnosztikai evidenciát döntéstámogató kockázattá alakítja, de minden átalakítás modellfeltevés. A következő integrált tanegységben a teljes PUNDIT-oktatási láncot egyetlen workflow-ban járjuk végig."),
        ])
    write_notebook("11_DINAMIKUS_KOCKAZAT_RBM.ipynb",nb)

    nb=notebook(
        "12 – Integrált PUNDIT esettanulmány: TK-101", "13",
        ["a féléves módszereket egyetlen traceable workflow-ba integrálni", "qualitative → formal → dynamic → decision láncot végrehajtani", "eredmények és korlátok különválasztása", "önálló hallgatói projektet specifikálni"],
        [
            md("""## 1. Integrációs térkép

**system → hazards → failure modes → PHA/FMEA/HAZOP → FTA → Bayesian evidence / Markov dynamics → Monte Carlo uncertainty → diagnostic update → RBM decision.**

A cél nem az, hogy minden módszert egyszerre használjunk, hanem hogy megértsük, melyik milyen kérdésre válaszol és hogyan ad át információt a következőnek."""),
            md("""## 2. Rendszermodell és hazard

A TK-101 modell strukturált YAML-ból indul. A representation simplified SysML-derived exchange format; nem natív SysML parser."""),
            code("""import yaml
path=ROOT/'data'/'pundit_case'/'system_model.yaml'
with open(path,encoding='utf-8') as f: model=yaml.safe_load(f)
print(model.get('metadata',{})); print('components:',[c['id'] for c in model['components']]); print('hazards:',[h['id'] for h in model['hazards']])"""),
            md("""## 3. Kvalitatív lánc

PHA: overflow/fire. FMEA: LT failed low, LSHH/XV fail-on-demand, operator miss. HAZOP: MORE LEVEL, NO EFFECTIVE SHUTDOWN. Ezekből származik az FTA struktúra."""),
            code("""qual=pd.DataFrame([
 {'PHA':'Overflow','FMEA':'LT-101 failed low','HAZOP':'MORE LEVEL','formal':'FTA basic event'},
 {'PHA':'Overflow','FMEA':'LSHH fail on demand','HAZOP':'NO SHUTDOWN','formal':'FTA basic event'},
 {'PHA':'Overflow','FMEA':'XV fail on demand','HAZOP':'NO SHUTDOWN','formal':'FTA basic event'}]); qual"""),
            md("""## 4. Model → FTA → baseline risk

A repository tesztelt modulja generálja a fault tree-t, majd minimal cut seteket és top-event probability-t számít."""),
            code("""from safetycourse.model_io import load_yaml,validate_system_model,generate_fault_tree
from safetycourse.fta import top_event_probability,minimal_cut_sets
m=load_yaml(path); print(validate_system_model(m)); tree=generate_fault_tree(m,'OVERFLOW')
p0=top_event_probability(tree); print('baseline P(OVERFLOW)=',p0); print([sorted(x) for x in minimal_cut_sets(tree)])"""),
            md("""## 5. Szenzoradat → evidencia

A szintetikus LT-101 residual alapján diagnosztikai score-t készítünk. A score→probability mapping oktatási modell és kalibrációt igényelne."""),
            code("""df=pd.read_csv(ROOT/'data'/'pundit_case'/'sensor_data.csv'); r=df.lt101_measured_pct-df.true_level_pct
def sigmoid(x): return 1/(1+np.exp(-x))
p_sensor=.002+(.6-.002)*sigmoid(-((r+2.5)/.8))
plt.plot(df.time_min,p_sensor); plt.xlabel('time'); plt.ylabel('P(sensor fault | evidence)'); plt.grid(alpha=.3); plt.show()"""),
            md("""## 6. Evidence → dynamic overflow risk

A statikus LT basic-event prior helyére a time-dependent posterior proxy kerül. Ez egy közvetlen szemléltetés arra, hogyan válhat a risk estimate adatérzékennyé."""),
            code("""p_ch=.08; p_auto=1-(1-.01)*(1-.005); p_op=.04
p_dynamic=p_ch*p_auto*(1-(1-p_sensor)*(1-p_op))
plt.semilogy(df.time_min,p_dynamic); plt.axhline(p0,ls='--',label='baseline model'); plt.legend(); plt.xlabel('time'); plt.ylabel('P(overflow)'); plt.grid(alpha=.3); plt.show()"""),
            md("""## 7. Markov dinamikai nézőpont

A state model a degraded állapotokban töltött időt és recovery transitionöket kezeli. Nem ugyanazt a kérdést teszi fel, mint az FTA; a két modell eredménye csak jól definiált mapping mellett kombinálható."""),
            code("""from scipy.linalg import expm
states=['S0','S1','S2','S3','S4','S5']; Q=np.zeros((6,6))
def add(i,j,x): Q[i,j]+=x
add(0,1,.002); add(0,2,.001); add(0,3,.004); add(1,0,.08); add(1,3,.004); add(2,0,.05); add(2,3,.004); add(3,0,.2); add(3,4,.01); add(4,0,.1); add(4,5,.03)
for i in range(6): Q[i,i]=-Q[i].sum()
p=np.array([1,0,0,0,0,0.])@expm(Q*100); print(dict(zip(states,p))); print('P(S4 or S5)=',p[4]+p[5])"""),
            md("""## 8. Monte Carlo uncertainty

A baseline basic-event probability-k bizonytalanságát Beta eloszlással szemléltetjük. A paraméterek szintetikusak."""),
            code("""rng=np.random.default_rng(9); N=20_000
pch=rng.beta(8,92,N); pl=rng.beta(2,198,N); px=rng.beta(1,199,N); ps=rng.beta(4,196,N); po=rng.beta(8,192,N)
p_mc=pch*(1-(1-pl)*(1-px))*(1-(1-ps)*(1-po))
print('5/50/95%=',np.quantile(p_mc,[.05,.5,.95]))"""),
            md("""## 9. Risk-based maintenance döntés

Ugyanaz a kérdés zárja a workflow-t, amellyel a projekt motivációja indult: **karbantartsuk az LT-101-et most, vagy várjunk a következő opportunity window-ig?**"""),
            code("""Cc=50_000_000; Cm=250_000; prod_now=800_000; prod_window=100_000; p_after=.001
cost_now=Cm+prod_now+p_after*Cc; current=float(p_dynamic.iloc[-1] if hasattr(p_dynamic,'iloc') else p_dynamic[-1]); cost_wait=Cm+prod_window+current*Cc
pd.DataFrame([{'option':'maintain now','expected_cost':cost_now},{'option':'wait','expected_cost':cost_wait}])"""),
            md("""## 10. Traceability és PUNDIT educational exploitation

Dokumentálandó: source artifact, model version, synthetic/real data flag, assumptions, generated artifact, validation, chapter, project ID és `technical_deliverable_claim: false`. A repository `project/pundit_traceability.yml` ezt a szétválasztást szolgálja."""),
            code("""trace=pd.read_csv(ROOT/'data'/'pundit_case'/'sensor_data.csv').head(1)
print('PUNDIT project: 2020-1.2.3-EUREKA-2022-00021')
print('use: educational_exploitation')
print('technical_deliverable_claim: false')"""),
            md("""## 11. Féléves hallgatói projekt

Válassz egy safety-critical alrendszert. Minimum: system boundary; PHA/FMEA/HAZOP; egy formal risk model; legalább egy paraméterezhető Python notebook; uncertainty/assumption dokumentáció; egy maintenance/mitigation decision; traceability. Nem a modell mérete, hanem az érvelés minősége számít."""),
            exercise(["Válassz egy TK-101 basic eventet és tervezz adatforrást a probability kalibrálására.", "Hasonlítsd össze, mit jelent a baseline FTA probability és a Markov S4+S5 probability; miért nem azonos mennyiség?", "Adj common-cause eseményt a modelhez és dokumentáld a traceability-t.", "Írj 5 mondatos decision memo-t a maintain now / wait döntésről, feltételezésekkel együtt."]),
            summary("A kurzus végére a kockázatelemzés nem különálló módszerek listája, hanem traceable mérnöki lánc: **rendszermodell → veszély → formális modell → evidencia → dinamikus risk → döntés**. A PUNDIT kapcsolódás ennek oktatási hasznosítása, nem technikai deliverable-igazolás."),
        ])
    write_notebook("12_PUNDIT_INTEGRALT_ESET.ipynb",nb)


if __name__=='__main__': build()
