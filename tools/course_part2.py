from course_common import md, code, notebook, write_notebook, exercise, summary


def build():
    nb = notebook(
        "04 – Modellalapú kockázatelemzés: rendszermodelltől a hibafáig", "4",
        ["rendszermodell és kockázati modell szerepének elkülönítése", "simplified SysML-derived exchange representation értelmezése", "strukturális és referencia-validáció", "determinista model-to-FTA transzformáció és traceability"],
        [
            md("""## 1. Miért model-based?

A kézzel karbantartott FTA gyorsan inkonzisztenssé válhat, ha a rendszerstruktúra változik. A cél ezért explicit kapcsolat a **rendszerleírás** és a **kockázati modell** között.

Ebben a tanegységben nem natív SysML parserrel dolgozunk. Egy **simplified SysML-derived YAML/JSON exchange representation** szerepel: komponensek, funkciók, failure mode-ok, hazard logic és kapcsolatok. Ez oktatási reprezentáció, nem a teljes SysML szemantika."""),
            md("""## 2. Minimális rendszermodell

Két safety funkció: LSHH-101 indítja a shutdown-t, XV-101 zárja a betáplálást. Mindkettő failure-on-demand eseménnyel rendelkezik. A hazard logic azt mondja: bármelyik hiba elég az automatikus leállítás sikertelenségéhez."""),
            code("""model={
 "components":[
  {"id":"LSHH101","type":"high_high_switch","function":"initiate_shutdown","failure_modes":[{"id":"LSHH101_FOD","mode":"fail_on_demand","probability":.01}]},
  {"id":"XV101","type":"shutdown_valve","function":"stop_inflow","failure_modes":[{"id":"XV101_FOD","mode":"fail_on_demand","probability":.005}]}
 ],
 "hazards":[{"id":"AUTO_FAIL","logic":{"gate":"OR","inputs":[{"event":"LSHH101_FOD"},{"event":"XV101_FOD"}]}}]
}
model"""),
            md("""## 3. YAML csak csereformátum

A tudományos tartalom nem a YAML szintaxis, hanem a mezők definíciója, a validálási szabályok és a transzformáció. A formátum később natív SysML/AADL/Simulink adapterrel cserélhető."""),
            code("""import yaml
print(yaml.safe_dump(model,sort_keys=False,allow_unicode=True))"""),
            md("""## 4. Validáció generálás előtt

Legalább: unique ID, minden hazardnak logic, minden `event` referencia létező failure mode-ra mutat, és csak támogatott gate szerepel."""),
            code("""def catalog(m):
    return {fm["id"]:{**fm,"component":c["id"]} for c in m.get("components",[]) for fm in c.get("failure_modes",[])}

def validate(m):
    errors=[]; ids=[c.get("id") for c in m.get("components",[])]
    if len(ids)!=len(set(ids)): errors.append("duplicate component id")
    cat=catalog(m)
    def check(x):
        if "event" in x:
            if x["event"] not in cat: errors.append("unknown event: "+x["event"])
            return
        if str(x.get("gate","")).upper() not in {"AND","OR"}: errors.append("unsupported gate")
        for y in x.get("inputs",[]): check(y)
    for h in m.get("hazards",[]):
        if "logic" not in h: errors.append("hazard without logic")
        else: check(h["logic"])
    return errors
print(validate(model))"""),
            code("""from copy import deepcopy
bad=deepcopy(model)
bad["hazards"][0]["logic"]["inputs"].append({"event":"DOES_NOT_EXIST"})
print(validate(bad))"""),
            md("""## 5. Determinisztikus transzformáció: hazard logic → FTA

Szabály: event → BASIC node; gate → FTA gate; a hazard ID → top event. A transzformáció nem LLM-döntés, hanem explicit algoritmus."""),
            code("""def model_to_fta(m,hazard_id):
    errs=validate(m)
    if errs: raise ValueError("; ".join(errs))
    h=next(x for x in m["hazards"] if x["id"]==hazard_id); cat=catalog(m); nodes={}; k=0
    def conv(expr,preferred=None):
        nonlocal k
        if "event" in expr:
            e=expr["event"]; nodes[e]={"type":"BASIC","probability":float(cat[e]["probability"]),"source_component":cat[e]["component"]}; return e
        k+=1; gid=preferred or f"G{k:02d}"; children=[conv(x) for x in expr["inputs"]]
        nodes[gid]={"type":expr["gate"].upper(),"children":children,"source":"hazard_logic"}; return gid
    top=conv(h["logic"],hazard_id)
    return {"top_event":top,"nodes":nodes}
fta=model_to_fta(model,"AUTO_FAIL")
fta"""),
            md("""## 6. Teljes TK-101 modell betöltése

A közös `system_model.yaml` ugyanilyen elven tartalmazza az oktatási rendszerkomponenseket és hazard logic-ot."""),
            code("""path=ROOT/'data'/'pundit_case'/'system_model.yaml'
with open(path,encoding='utf-8') as f: tk_model=yaml.safe_load(f)
print(tk_model.get('metadata',{})); print('validation:',validate(tk_model))"""),
            code("""tk_fta=model_to_fta(tk_model,'OVERFLOW')
trace=pd.DataFrame([{"fta_node":nid,"type":n['type'],"source_component":n.get('source_component')} for nid,n in tk_fta['nodes'].items()])
trace"""),
            md("""## 7. Mit nem állítunk?

Nem olvasunk natív SysML v2 repository/API modellt; nem értelmezzük a teljes SysML szemantikát; és nem állítjuk, hogy pusztán komponenskapcsolatokból automatikusan helyes failure propagation származik. A formális transzformáció minősége a forrásmodell és a szabályok minőségétől függ."""),
            code("""from safetycourse.model_io import load_yaml,validate_system_model,generate_fault_tree
lib_model=load_yaml(path); lib_tree=generate_fault_tree(lib_model,'OVERFLOW')
print(validate_system_model(lib_model)); print(lib_tree['top_event'],len(lib_tree['nodes']))"""),
            exercise(["Tegyél nem létező event referenciát a modellbe és ellenőrizd a validátort.", "Adj új komponens failure mode-ot és használd hazard logicban.", "Bővítsd a traceability táblát `hazard_id` és `gate_path` mezővel.", "Írd le, milyen információ hiányzik egy valódi SysML-v2 → FTA adapterhez."]),
            summary("A modellalapú kockázatelemzés lényege a reprodukálható **model → validation → transformation → risk model → traceability** lánc. A következő tanegységben a statikus valószínűségi modellt Bayes-hálóval evidenciára érzékennyé tesszük."),
        ])
    write_notebook("04_MODELLALAPU_KOCKAZAT.ipynb", nb)

    nb = notebook(
        "05 – Bayes-hálók: predikció, diagnózis és FTA → BN gondolkodás", "5",
        ["Bayes-tétel numerikus alkalmazása", "prior–likelihood–posterior elkülönítése", "prediktív és diagnosztikai következtetés", "TK-101 szenzorevidenciával történő risk update"],
        [
            md("""## 1. Miért Bayes?

Az FTA tipikusan előrefelé kérdez: basic eventekből mekkora a top event valószínűsége? Üzem közben gyakran fordított a kérdés: **evidenciát láttam; mekkora most egy fault valószínűsége?** Ez diagnosztikai inference."""),
            md("""## 2. Bayes-tétel kézzel

$$P(F|E)=\\frac{P(E|F)P(F)}{P(E|F)P(F)+P(E|\\neg F)P(\\neg F)}.$$

Legyen $P(F)=0.02$, detector sensitivity 0.90 és false-positive rate 0.05."""),
            code("""prior=.02; sens=.90; fp=.05
posterior=sens*prior/(sens*prior+fp*(1-prior))
print(f"Prior={prior:.3f}; posterior={posterior:.3f}")"""),
            md("""A posterior közel 27%. A pozitív jel jelentősen növeli a fault valószínűségét, de nem teszi bizonyossá. A base rate számít."""),
            code("""priors=np.linspace(.001,.2,100)
posts=sens*priors/(sens*priors+fp*(1-priors))
plt.plot(priors,posts); plt.plot(priors,priors,'--'); plt.xlabel('prior'); plt.ylabel('posterior'); plt.grid(alpha=.3); plt.show()"""),
            md("""## 3. Prediktív vs diagnosztikai irány

Prediktív: $P(E|F)$ – ha fault van, mit várunk látni? Diagnosztikai: $P(F|E)$ – ha evidenciát látunk, mekkora fault valószínűség? A kettő általában nem azonos."""),
            md("""## 4. Mini Bayes-háló enumerációval

`SensorFault → BadMeasurement → MissedIntervention`. A joint eloszlás faktorizálható: $P(F,M,I)=P(F)P(M|F)P(I|M)$."""),
            code("""P_F=.02
P_M_given_F={False:.03,True:.90}
P_I_given_M={False:.04,True:.70}
def joint(f,m,i):
    pf=P_F if f else 1-P_F
    pm=P_M_given_F[f] if m else 1-P_M_given_F[f]
    pi=P_I_given_M[m] if i else 1-P_I_given_M[m]
    return pf*pm*pi
rows=[]
for f in [False,True]:
 for m in [False,True]:
  for i in [False,True]: rows.append({'F':f,'M':m,'I':i,'P':joint(f,m,i)})
jt=pd.DataFrame(rows); print('sum=',jt.P.sum()); jt"""),
            code("""subset=jt[jt.M]
print('P(F=True | M=True)=',subset[subset.F].P.sum()/subset.P.sum())"""),
            md("""## 5. FTA → BN gondolkodás

FTA gate-ek determinisztikus vagy közel determinisztikus CPT-kkel reprezentálhatók. A BN hozzáadott értéke: evidenciát rögzíthetünk köztes változón, majd diagnosztikai inference-t végzünk. Nem minden FTA→BN konverzió triviális shared events és függőségek mellett."""),
            md("""## 6. TK-101: posterior szenzorhiba → dinamikusan módosított overflow risk

Az FTA `MANUAL_FAIL = LT101_LOW OR OPERATOR_MISS`. Ha a statikus `P(LT101_LOW)=0.02` helyére a diagnosztikai posterior kerül, a top-event probability evidenciától függővé válik."""),
            code("""p_ch=.08; p_auto=1-(1-.01)*(1-.005); p_op=.04
def overflow(p_sensor):
    p_manual=1-(1-p_sensor)*(1-p_op)
    return p_ch*p_auto*p_manual
print('prior risk    ',overflow(prior))
print('evidence risk ',overflow(posterior))"""),
            md("""## 7. Kalibráció

A sensitivity, false-positive rate és prior nem tetszőleges. Forrásuk lehet proof-test, historikus adat, szakértői elicitation vagy validált diagnosztikai kísérlet. A posterior csak annyira megbízható, mint ezek az inputok."""),
            code("""from safetycourse.bayes import BinaryNode,BinaryBayesNet
nodes=[BinaryNode('Fault',[],{():.02}),BinaryNode('Evidence',['Fault'],{(False,):.05,(True,):.90})]
bn=BinaryBayesNet(nodes)
print(bn.query('Fault',{'Evidence':True}))"""),
            exercise(["Csökkentsd a sensitivity-t 0.70-re.", "Növeld a false-positive rate-et 0.15-re.", "Számítsd P(F|M=False)-t enumerációval.", "Adj MaintenanceOverdue változót, amely a prior fault probability-t befolyásolja, és jelöld egyértelműen modellfeltevésként."]),
            summary("A Bayes-háló a statikus prior modellt evidenciával frissíthető diagnosztikai modellé teszi. A következő tanegységben az **idő és állapotátmenet** kerül a középpontba Markov-modellekkel és Dynamic HAZOP-pal."),
        ])
    write_notebook("05_BAYES_HALOK.ipynb", nb)

    nb = notebook(
        "06 – Markov-modellek és Dynamic HAZOP", "6",
        ["DTMC és CTMC megkülönböztetése", "generator matrix létrehozása és ellenőrzése", "failure–repair CTMC kiértékelése", "TK-101 állapotmodell és Dynamic HAZOP összekötése"],
        [
            md("""## 1. Mi hiányzik a statikus FTA-ból?

A statikus fault tree nem mondja meg természetesen az eseménysorrendet, a degraded állapotban töltött időt vagy a javítás dinamikáját. Markov-modellben **állapotok** és **átmeneti intenzitások/valószínűségek** írják le az időbeli viselkedést."""),
            md("""## 2. DTMC

Két állapot: OK és FAILED. Egy lépéshez $P=\\begin{bmatrix}.98&.02\\\\.20&.80\\end{bmatrix}$. Sorösszeg = 1."""),
            code("""P=np.array([[.98,.02],[.20,.80]])
p=np.array([1.,0.]); hist=[p.copy()]
for _ in range(20): p=p@P; hist.append(p.copy())
hist=np.array(hist)
plt.plot(hist[:,0],label='OK'); plt.plot(hist[:,1],label='FAILED'); plt.legend(); plt.grid(alpha=.3); plt.show()"""),
            md("""## 3. CTMC és generator matrix

Kétállapotú failure–repair modell:

$$Q=\\begin{bmatrix}-\\lambda&\\lambda\\\\\\mu&-\\mu\\end{bmatrix},\qquad p(t)=p(0)e^{Qt}.$$

Off-diagonal elemek nemnegatívak, minden sor összege 0."""),
            code("""from scipy.linalg import expm
lam=.002; mu=.08
Q=np.array([[-lam,lam],[mu,-mu]])
p0=np.array([1.,0.]); times=np.linspace(0,200,200)
probs=np.vstack([p0@expm(Q*t) for t in times])
plt.plot(times,probs[:,0],label='OK'); plt.plot(times,probs[:,1],label='FAILED'); plt.axhline(mu/(lam+mu),ls='--',label='A∞'); plt.legend(); plt.grid(alpha=.3); plt.show()"""),
            md("""## 4. TK-101 oktatási állapotok

S0 Normal; S1 Sensor degraded; S2 Protection degraded/maintenance overdue; S3 High-level challenge; S4 Overflow; S5 Fire. Nem bontunk ki minden barrier-kombinációt külön state-ként, mert gyors state-space explosionhoz vezetne."""),
            code("""states=['S0_normal','S1_sensor_degraded','S2_protection_degraded','S3_challenge','S4_overflow','S5_fire']; n=len(states)
Q=np.zeros((n,n))
def rate(i,j,x): Q[i,j]+=x
rate(0,1,.002); rate(0,2,.001); rate(0,3,.004)
rate(1,0,.08); rate(1,3,.004); rate(2,0,.05); rate(2,3,.004)
rate(3,0,.20); rate(3,4,.01); rate(4,0,.10); rate(4,5,.03)
for i in range(n): Q[i,i]=-Q[i].sum()
pd.DataFrame(Q,index=states,columns=states)"""),
            code("""p0=np.array([1,0,0,0,0,0.],float); ts=np.linspace(0,300,301); P=np.vstack([p0@expm(Q*t) for t in ts])
for j,s in enumerate(states): plt.plot(ts,P[:,j],label=s)
plt.xlabel('h'); plt.ylabel('state probability'); plt.legend(fontsize=8); plt.grid(alpha=.3); plt.show()"""),
            md("""## 5. Dynamic HAZOP

A HAZOP `MORE LEVEL` eltérése dinamikus útvonalként értelmezhető: **normal/degraded → high-level challenge → overflow → fire**. A safeguard vagy maintenance visszavezető átmenetet hozhat létre. Dynamic HAZOP itt nem pusztán új táblázat, hanem a deviation időbeli fejlődésének modellezése."""),
            code("""pd.DataFrame([
 {'deviation':'MORE LEVEL','from':'S0/S1/S2','to':'S3','barrier':'alarm/trip/operator'},
 {'deviation':'NO EFFECTIVE SHUTDOWN','from':'S3','to':'S4','barrier':'LSHH+XV+manual recovery'},
 {'deviation':'IGNITION AFTER RELEASE','from':'S4','to':'S5','barrier':'containment+fire protection'}])"""),
            md("""## 6. Maintenance sensitivity

Növeljük a sensor repair rate-et és számítsuk a 100 órán belüli overflow+fire állapotvalószínűséget."""),
            code("""def with_repair(r):
    q=Q.copy(); q[1,0]=r; q[1,1]=-q[1,np.arange(n)!=1].sum(); return q
rows=[]
for r in [.02,.05,.08,.15]:
    p100=p0@expm(with_repair(r)*100); rows.append({'repair_rate':r,'P_S4_or_S5_100h':p100[4]+p100[5]})
pd.DataFrame(rows)"""),
            code("""from safetycourse.markov import validate_generator,transient_probabilities
validate_generator(Q); transient_probabilities(Q,p0,[0,10,100])"""),
            md("""## 7. Korlátok

A Markov-tulajdonság szerint a jövő a jelenlegi állapottól függ. Ha a komponens ‘kora’ vagy a degraded állapotban töltött idő lényeges, azt state-be kell emelni vagy más modellt kell választani. Exponenciális tartózkodási idők sem minden folyamatra megfelelőek."""),
            exercise(["Növeld az S3→S4 rátát 0.03-ra.", "Csökkentsd S3→S0 recovery-t 0.05-re.", "Tedd S5-öt javíthatóvá S5→S0 átmenettel és indokold fizikailag.", "Adj explicit S1+S2 combined state-et, és figyeld a state-space növekedését."]),
            summary("A Markov-modell időbeli állapotdinamikát ad a kockázati elemzéshez, a Dynamic HAZOP pedig a veszélyes eltérések fejlődését kapcsolja ehhez. A következő tanegység Monte Carlo-val bizonytalanságot és ritka eseményeket vizsgál."),
        ])
    write_notebook("06_MARKOV_DYNAMIC_HAZOP.ipynb", nb)


if __name__ == "__main__":
    build()
