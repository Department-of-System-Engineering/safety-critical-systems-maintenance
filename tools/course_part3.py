from course_common import md, code, notebook, write_notebook, exercise, summary


def build():
    nb=notebook(
        "07 – Monte Carlo, bizonytalanság és ritka események", "8",
        ["Monte Carlo becslés és standard error értelmezése", "FTA eredmény szimulációs validálása", "paraméterbizonytalanság propagálása", "rare-event probléma és splitting/RESTART gondolat felismerése"],
        [
            md("""## 1. Monte Carlo alapötlet

Sok véletlen realizációt generálunk, minden realizációban kiértékeljük a rendszert, majd a kimenetek gyakoriságából becslünk. Bernoulli eseménynél $\\hat p=N_{event}/N$, és nagy mintánál $SE(\\hat p)\\approx\\sqrt{\\hat p(1-\\hat p)/N}$."""),
            code("""rng=np.random.default_rng(42); N=10_000; p=.02
x=rng.random(N)<p; phat=x.mean(); se=np.sqrt(phat*(1-phat)/N)
print(phat,se,x.sum())"""),
            md("""## 2. Konvergencia

A mintaszám növelése nem monoton javulást jelent minden futásban, de a bizonytalanság nagyságrendje $1/\\sqrt N$ szerint csökken."""),
            code("""rows=[]
for n in [100,500,1_000,5_000,10_000,50_000,100_000]:
 r=np.random.default_rng(100+n); rows.append({'N':n,'estimate':(r.random(n)<p).mean()})
conv=pd.DataFrame(rows); plt.semilogx(conv.N,conv.estimate,'o-'); plt.axhline(p,ls='--'); plt.grid(alpha=.3); plt.show(); conv"""),
            md("""## 3. TK-101 FTA Monte Carlo-val

A static FTA eseményeit független Bernoulli változókként generáljuk. Ez szándékosan ugyanazt a függetlenségi feltevést használja, mint az analitikus FTA, így validációs összehasonlításra alkalmas."""),
            code("""prob={'CHALLENGE':.08,'LSHH_FOD':.01,'XV_FOD':.005,'LT_LOW':.02,'OP_MISS':.04}
def simulate(n=500_000,seed=42):
 r=np.random.default_rng(seed); s={k:r.random(n)<v for k,v in prob.items()}
 auto=s['LSHH_FOD']|s['XV_FOD']; manual=s['LT_LOW']|s['OP_MISS']; over=s['CHALLENGE']&auto&manual
 ph=over.mean(); return ph,np.sqrt(ph*(1-ph)/n),int(over.sum())
ph,se,events=simulate(); print(ph,se,events)
p_auto=1-(1-.01)*(1-.005); p_manual=1-(1-.02)*(1-.04); exact=.08*p_auto*p_manual
print('exact=',exact,'z=',(ph-exact)/se)"""),
            md("""## 4. Paraméterbizonytalanság

Az input probability-k sem pontos számok. Oktatási példában Beta-eloszlást használunk. A Beta-paraméterek **szintetikusak**, nem üzemi bizonyítékok."""),
            code("""r=np.random.default_rng(7); M=20_000
p_ch=r.beta(8,92,M); p_lshh=r.beta(2,198,M); p_xv=r.beta(1,199,M); p_lt=r.beta(4,196,M); p_op=r.beta(8,192,M)
p_auto=1-(1-p_lshh)*(1-p_xv); p_manual=1-(1-p_lt)*(1-p_op); p_over=p_ch*p_auto*p_manual
print(np.quantile(p_over,[.05,.5,.95])); plt.hist(p_over,bins=60); plt.xlabel('P(overflow)'); plt.show()"""),
            md("""## 5. Ritka esemény probléma

Ha $p=10^{-7}$, akkor $N=10^6$ futásban a várható eseményszám csak 0.1. A nulla megfigyelés nem jelenti azt, hogy a valós probability nulla."""),
            code("""rare_p=1e-7
for n in [10**4,10**5,10**6,10**7]: print(f'N={n:,}, várható eseményszám={n*rare_p:.3f}')"""),
            md("""## 6. Splitting / RESTART gondolat

Ha a ritka végállapot felé vezető trajektórián vannak köztes ‘közeledési’ szintek, a szinteket elérő realizációkat újra felhasználhatjuk/sokszorozhatjuk. Így a számítási erőforrást a releváns trajektóriákra koncentráljuk. Az itt használt repository-függvény **pedagógiai multilevel splitting demo**, nem production-grade RESTART implementation."""),
            code("""from safetycourse.simulation import random_walk_exceedance,multilevel_splitting_random_walk
crude,se=random_walk_exceedance(n=20_000,steps=50,drift=-.05,sigma=1.,threshold=20,seed=1)
split=multilevel_splitting_random_walk(particles=2_000,steps=50,drift=-.05,sigma=1.,levels=[8,14,20],seed=1)
print('crude',crude,'SE',se); print('splitting demo',split)"""),
            exercise(["Csökkentsd az összes basic-event probability-t tizedére és figyeld az 500 000 futás eseményszámát.", "Növeld N-t és figyeld a standard errort.", "Változtasd a Beta-eloszlások koncentrációját azonos átlag mellett.", "Módosítsd a splitting szinteket és hasonlítsd a stabilitást."]),
            summary("Monte Carlo általános, de ritka eseménynél drága. A következő tanegységben azt vizsgáljuk, hogyan ronthatják le a redundancia előnyeit a **függőségek és common-cause failure** események."),
        ])
    write_notebook("07_MONTE_CARLO_RITKA_ESEMENYEK.ipynb",nb)

    nb=notebook(
        "08 – Redundancia, függőségek és kaszkádhatások", "9",
        ["soros, párhuzamos és k-out-of-n struktúra számítása", "redundancia függetlenségi feltételének kritikája", "common-cause failure hatásának szemléltetése", "függőségi és kaszkád gráf értelmezése"],
        [
            md("""## 1. Redundancia: nem pusztán több komponens

Redundancia csak akkor növeli a rendszer megbízhatóságát a várt mértékben, ha a redundáns elemeket nem ugyanaz a hibaok éri. Közös táp, azonos környezet, shared software vagy közös karbantartási hiba könnyen megsérti a függetlenségi feltevést."""),
            code("""R=.95
print('2 soros',R**2); print('2 párhuzamos',1-(1-R)**2)"""),
            md("""## 2. k-out-of-n

Azonos, független komponenseknél $R_{k|n}=\\sum_{i=k}^n {n\\choose i}R^i(1-R)^{n-i}$. Példa: 2oo3 voting."""),
            code("""from math import comb
def k_out_of_n(R,k,n): return sum(comb(n,i)*R**i*(1-R)**(n-i) for i in range(k,n+1))
for r in [.8,.9,.95,.99]: print(r,k_out_of_n(r,2,3))"""),
            code("""Rs=np.linspace(.5,.999,150)
plt.plot(Rs,Rs,label='1oo1'); plt.plot(Rs,[k_out_of_n(r,1,2) for r in Rs],label='1oo2'); plt.plot(Rs,[k_out_of_n(r,2,3) for r in Rs],label='2oo3'); plt.xlabel('component R'); plt.ylabel('system R'); plt.legend(); plt.grid(alpha=.3); plt.show()"""),
            md("""## 3. Common-cause failure – egyszerű beta-factor szemléltetés

Nagyon leegyszerűsített oktatási modell: a failure probability $q$ egy $\\beta q$ common-cause részből és $(1-\\beta)q$ független részből áll. Két elem együttes failure probability-jére: $P_{dual}\\approx\\beta q+(1-\\beta)q^2$. Ez nem teljes CCF standardmodell, csak nagyságrendi szemléltetés."""),
            code("""q=.01
pd.DataFrame([{'beta':b,'P_dual':b*q+(1-b)*q*q,'ratio_vs_independent':(b*q+(1-b)*q*q)/(q*q)} for b in [0,.01,.05,.1,.2]])"""),
            md("""## 4. Függőségi gráf

Nem minden dependency logikai gate. Például common power supply több funkciót érinthet, míg kommunikációs vagy emberi függőség downstream következményeket okozhat."""),
            code("""import networkx as nx
G=nx.DiGraph([('PowerSupply','LT-101'),('PowerSupply','LSHH-101'),('PowerSupply','XV actuator'),('LT-101','HMI'),('HMI','Operator'),('LSHH-101','TripLogic'),('TripLogic','XV actuator')])
print('PowerSupply downstream:',sorted(nx.descendants(G,'PowerSupply')))
pos=nx.spring_layout(G,seed=3); nx.draw_networkx(G,pos,node_size=1800,font_size=8); plt.axis('off'); plt.show()"""),
            md("""## 5. TK-101: common power failure

Az automatikus shutdown független FTA-ja $1-(1-p_{LSHH})(1-p_{XV})$. Ha `COMMON_POWER_FAIL` egyszerre veszélyezteti mindkettőt, azt **egy közös okként** kell reprezentálni, nem két független basic event másolatként."""),
            code("""p_lshh=.01; p_xv=.005; p_common=.002
ind=1-(1-p_lshh)*(1-p_xv)
with_common=1-(1-p_common)*(1-p_lshh)*(1-p_xv)
print(ind,with_common,'relative increase',with_common/ind-1)"""),
            md("""## 6. Kaszkádhatás

Egy strukturális gráf szemléltetheti a propagation útvonalat: SensorBias → LateDetection → HighLevelDuration → OverflowDemand → LossOfContainment → IgnitionOpportunity → FireEscalation. A valószínűségek és időzítés miatt később BN/Markov/szimuláció lehet célszerűbb."""),
            code("""prop=nx.DiGraph([('SensorBias','LateDetection'),('LateDetection','HighLevelDuration'),('HighLevelDuration','OverflowDemand'),('OverflowDemand','LossOfContainment'),('LossOfContainment','IgnitionOpportunity'),('IgnitionOpportunity','FireEscalation')])
print(list(nx.topological_sort(prop)))"""),
            exercise(["Számíts 2oo3 reliability-t R=0.90 mellett és hasonlíts 1oo2-höz.", "q=0.001, beta=0.01 mellett hányszoros a dual failure az independence-hez képest?", "Adj NetworkSwitch common dependency-t a gráfhoz.", "Azonosíts két TK-101 függőséget, amely inkább szervezeti, mint műszaki."]),
            summary("A redundancia értékét csak a függőségek ismeretében lehet értelmezni. A következő tanegység a rendszerkockázatot már **karbantartási döntési stratégiákhoz** kapcsolja."),
        ])
    write_notebook("08_REDUNDANCIA_FUGGOSEGEK.ipynb",nb)

    nb=notebook(
        "09 – Karbantartási stratégiák és kockázatalapú szemlélet", "10",
        ["corrective/preventive/CBM/PdM/RBM elkülönítése", "TBM és UBM rövidítések helyes használata", "állapotindikátor és egyszerű RUL becslés", "expected-cost alapú RBM döntés"],
        [
            md("""## 1. Karbantartási érettségi ív

- Corrective: hiba után.
- Preventive TBM: időalapon (**Time-Based Maintenance**).
- Preventive UBM: használatalapon (**Usage-Based Maintenance**).
- CBM: mért állapot alapján.
- PdM: előrejelzett állapot/RUL alapján.
- RBM: kockázat, következmény, költség és opportunity együtt.

A stratégiák nem feltétlenül ‘jobbak’ egymásnál; a megfelelő információ és döntési cél határozza meg a választást."""),
            md("""## 2. Preventive interval – első trade-off

Állandó $\\lambda$ esetén $F(T)=1-e^{-\\lambda T}$. Egyszerű oktatási költség: $C(T)=C_{PM}+F(T)C_F$. Ez még nem teljes renewal-reward optimalizáció."""),
            code("""lam=1/3000; C_PM=150_000; C_F=2_000_000
T=np.linspace(50,5000,200); F=1-np.exp(-lam*T); C=C_PM+F*C_F
plt.plot(T,C); plt.xlabel('preventive interval [h]'); plt.ylabel('simplified cost [HUF/cycle]'); plt.grid(alpha=.3); plt.show()"""),
            md("""## 3. CBM: indikátor és threshold

Szintetikus sensor-bias indikátort generálunk. Threshold crossing esetén condition-based action indítható."""),
            code("""rng=np.random.default_rng(4); t=np.arange(120); bias=np.maximum(0,.04*(t-40))+rng.normal(0,.15,len(t)); threshold=2.
alarm=bias>=threshold
plt.plot(t,bias); plt.axhline(threshold,ls='--'); plt.xlabel('time'); plt.ylabel('bias indicator'); plt.grid(alpha=.3); plt.show()
print('first crossing:',t[np.argmax(alarm)] if alarm.any() else None)"""),
            md("""## 4. PdM: egyszerű RUL gondolat

Az utolsó 30 ponton lineáris trendet illesztünk és becsüljük a threshold crossing idejét. Ez tanulópélda; valódi prognosztikában uncertainty, drift, covariates és model diagnostics szükséges."""),
            code("""w=30; slope,intercept=np.polyfit(t[-w:],bias[-w:],1); crossing=(threshold-intercept)/slope if slope>0 else np.inf; RUL=crossing-t[-1]
print('predicted crossing',crossing,'RUL',RUL)"""),
            md("""## 5. RBM: maintain now vs wait

Egyszerű döntési költség:

$$C_{expected}=C_{maintenance}+C_{production}+P(H)C_{consequence}.$$

Két opciót hasonlítunk, de hangsúly: safety constraint/ALARP/standard minimum requirement nem monetizálható egyszerűen ki."""),
            code("""def expected(Cm,Cp,p,Cc): return Cm+Cp+p*Cc
opts=pd.DataFrame([
 {'option':'Maintain now','cost':expected(250_000,800_000,.001,50_000_000)},
 {'option':'Wait for opportunity','cost':expected(250_000,100_000,.02,50_000_000)}])
opts"""),
            md("""## 6. Break-even probability

Mekkora várakozási hazard probability mellett azonos a két expected cost?"""),
            code("""Cc=50_000_000; p_now=.001; prod_now=800_000; prod_window=100_000
p_break=(prod_now-prod_window+p_now*Cc)/Cc
print('break-even p_wait=',p_break)"""),
            code("""from safetycourse.maintenance import compare_maintenance_options
compare_maintenance_options([
 {'name':'Maintain now','maintenance_cost':250_000,'production_loss':800_000,'hazard_probability':.001,'consequence_cost':50_000_000},
 {'name':'Wait','maintenance_cost':250_000,'production_loss':100_000,'hazard_probability':.02,'consequence_cost':50_000_000}])"""),
            exercise(["Duplázd a consequence costot és számíts új break-even értéket.", "Csökkentsd a production loss now értékét 300 000 HUF-ra.", "Írd le, milyen adat kellene ahhoz, hogy p_wait ne kézi input legyen.", "Hova sorolnád a proof-test alapú karbantartást, és miért nem mindig egyetlen címke elég?"]),
            summary("A karbantartási stratégia a rendelkezésre álló információtól és döntési céltól függ. A következő tanegységben a **szenzoradatból diagnosztikai evidenciát** képezünk, amely később dinamikus kockázati input lesz."),
        ])
    write_notebook("09_KARBANTARTASI_STRATEGIAK.ipynb",nb)


if __name__=='__main__': build()
