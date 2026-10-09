import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Dignity Accessibility Index", page_icon="🚻", layout="wide")

DIMS = [
    ("Equitable entry", 15, True, "Can women workers enter without asking permission, segregation or discriminatory restriction?"),
    ("Privacy", 15, True, "Does the facility provide a functioning door/lock and adequate visual privacy?"),
    ("Safety & lighting", 12, True, "Is the route and facility sufficiently safe and lit for intended hours?"),
    ("Water", 12, True, "Is usable water reliably available?"),
    ("Cleanliness", 12, False, "Is the facility clean enough to use without avoidable exposure to waste?"),
    ("Menstrual support", 10, False, "Are basic menstrual-management needs supported, including disposal?"),
    ("Affordability", 8, False, "Can intended users access the facility without a prohibitive fee?"),
    ("Proximity & hours", 10, False, "Is it reasonably close and open when workers need it?"),
    ("Reliability & inclusion", 6, False, "Is access/functioning dependable and inclusive in routine use?"),
]
SCENARIOS = {
    "A — Segregated society-worker washroom": [0,1,1,1,0,0,2,2,1],
    "B — Paid market toilet": [2,2,1,2,1,0,1,1,1],
    "C — Construction-site toilet": [2,0,0,0,0,0,2,2,0],
    "D — Scenario A after fixes": [2,2,1,2,2,1,2,2,1],
    "E — Clean facility, broken lock": [2,0,2,2,2,2,2,2,2],
}
LABEL = {0:"Failing", 1:"Partial", 2:"Adequate"}

st.markdown("""
<style>
:root { --dai-border: rgba(128,128,128,.28); --dai-muted: rgba(128,128,128,.9); }
.block-container {padding-top:1.4rem; padding-bottom:3rem; max-width:1280px;}
.hero {padding:1.8rem 2rem; border:1px solid var(--dai-border); border-radius:20px;
background:rgba(128,128,128,.07); margin-bottom:1rem;}
.hero h1 {font-size:2.35rem; margin:0 0 .3rem 0; letter-spacing:-.035em; color:inherit;}
.hero p {font-size:1.05rem; margin:0; color:inherit; opacity:.82;}
.kicker {font-size:.76rem; letter-spacing:.13em; text-transform:uppercase; font-weight:800; opacity:.65;}
.notice {padding:.9rem 1rem;border:1px solid var(--dai-border);border-left:4px solid currentColor;
background:rgba(128,128,128,.06);border-radius:10px;margin:.55rem 0 1.15rem;color:inherit;}
.gate {font-size:.70rem;font-weight:800;border:1px solid currentColor;border-radius:999px;
padding:.14rem .48rem;margin-left:.35rem;opacity:.8;}
div[data-testid="stMetric"] {border:1px solid var(--dai-border);padding:1rem 1.05rem;
border-radius:16px;background:rgba(128,128,128,.06);}
div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricValue"] {color:inherit !important;}
div[data-testid="stTabs"] button {font-weight:650;}
.result-card {border:1px solid var(--dai-border);border-radius:16px;padding:1rem 1.15rem;
background:rgba(128,128,128,.06);margin:.6rem 0 1rem;}
.result-title {font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;font-weight:800;opacity:.6;}
.result-main {font-size:1.65rem;font-weight:800;margin:.15rem 0;}
.small {font-size:.84rem;opacity:.72;}
hr {border-color:var(--dai-border);}
</style>
""", unsafe_allow_html=True)

def calc(r):
    score = sum(w*x/2 for (_,w,_,_),x in zip(DIMS,r))
    failed = [n for (n,_,g,_),x in zip(DIMS,r) if g and x == 0]
    raw = "Usable" if score >= 70 else ("Conditional" if score >= 50 else "Nominal")
    final = "Nominal" if failed else raw
    return score, raw, final, failed

def next_actions(r):
    actions=[]
    mapping={
      "Equitable entry":"Remove permission/segregation barriers and establish equal-access rules.",
      "Privacy":"Repair the door/lock and confirm privacy with users.",
      "Safety & lighting":"Restore lighting and address unsafe approach/access conditions.",
      "Water":"Restore a reliable water supply before treating the facility as usable.",
      "Cleanliness":"Introduce a documented cleaning and re-check schedule.",
      "Menstrual support":"Provide a covered disposal bin and reliable emptying arrangement.",
      "Affordability":"Remove or subsidise fees that deter intended users.",
      "Proximity & hours":"Align opening hours/access with workers’ schedules.",
      "Reliability & inclusion":"Address recurring breakdowns and exclusion in routine access."
    }
    # gates first, then lower scores by weight
    order = sorted(range(9), key=lambda i: (not DIMS[i][2], r[i], -DIMS[i][1]))
    for i in order:
        if r[i] < 2:
            actions.append((DIMS[i][0], mapping[DIMS[i][0]], DIMS[i][2] and r[i]==0))
    return actions

st.markdown("""<div class="hero"><div class="kicker">Social Work × Working with AI</div>
<h1>Dignity Accessibility Index <span style="opacity:.55">(DAI)</span></h1>
<p>From counting toilets to assessing <b>usable, safe and dignified access</b>.</p></div>""", unsafe_allow_html=True)
st.markdown('<div class="notice"><b>Academic prototype.</b> This tool evaluates sanitation facilities, not people. The five built-in scenarios are illustrative and are <b>not real facility audits</b>.</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Facility Evaluator", "Scenario Lab", "Portfolio View", "Method & Ethics"])

with tab1:
    left, right = st.columns([1.05,.95], gap="large")
    with left:
        st.subheader("Evaluate a facility")
        st.caption("Choose 0 (failing), 1 (partial), or 2 (adequate). Essential dignity gates are marked.")
        if "ratings" not in st.session_state: st.session_state.ratings=[2]*9
        for i,(name,w,gate,desc) in enumerate(DIMS):
            st.markdown(f"**{name}** · {w}% " + ("<span class='gate'>ESSENTIAL GATE</span>" if gate else ""), unsafe_allow_html=True)
            st.caption(desc)
            st.session_state.ratings[i] = st.radio(
                name, [0,1,2], index=st.session_state.ratings[i],
                format_func=lambda x:f"{x} — {LABEL[x]}", horizontal=True, key=f"r{i}", label_visibility="collapsed"
            )
        if st.button("Reset to all adequate", use_container_width=True):
            for i in range(9): st.session_state[f"r{i}"]=2
            st.rerun()
    with right:
        r=st.session_state.ratings
        score,raw,final,failed=calc(r)
        label={"Usable":"USABLE","Conditional":"CONDITIONALLY USABLE","Nominal":"NOMINAL ONLY"}[final]
        a,b=st.columns(2)
        a.metric("DAI score", f"{score:.1f} / 100")
        b.metric("Final classification", label)
        c,d=st.columns(2)
        c.metric("Score-only class", raw)
        d.metric("Essential gates failed", len(failed))
        st.markdown(f"""<div class="result-card">
          <div class="result-title">Decision rule</div>
          <div class="result-main">{label}</div>
          <div class="small">Weighted score: {score:.1f}/100 · Gate override: {"ACTIVE" if failed else "not triggered"}</div>
        </div>""", unsafe_allow_html=True)
        if failed:
            st.error("Essential gate failure: " + ", ".join(failed))
        elif final=="Usable": st.success("No dignity gate has failed and the score is ≥70.")
        else: st.warning("No gate has failed, but the weighted score remains below the usable threshold.")
        st.subheader("Dignity profile")
        fig=go.Figure(go.Bar(x=[x[0] for x in DIMS], y=[x*50 for x in r], text=[LABEL[x] for x in r], textposition="auto"))
        fig.update_layout(yaxis=dict(range=[0,100],title="Dimension rating (%)"), xaxis_tickangle=-35,
height=390, margin=dict(l=20,r=10,t=10,b=90), showlegend=False,
paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=None))
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Priority remediation")
        acts=next_actions(r)
        if not acts: st.success("No immediate remediation is generated. Re-audit routinely and confirm usability with women users.")
        else:
            for j,(dim,txt,urgent) in enumerate(acts[:4],1):
                st.markdown(f"**{j}. {dim}** {'— GATE FIRST' if urgent else ''}  \n{txt}")
        with st.expander("Explain this result"):
            if failed:
                st.write(f"The facility scores **{score:.1f}/100**, but {', '.join(failed)} received 0. Because these are non-compensatory dignity gates, the final classification is **Nominal only** regardless of the aggregate score.")
            else:
                st.write(f"The facility scores **{score:.1f}/100** and no dignity gate is rated 0. Under the prototype rules, it is **{final}**.")
            st.caption("The score is decision support, not a substitute for women users’ own judgement of whether a facility is usable.")

with tab2:
    st.subheader("Scenario Lab")
    choice=st.selectbox("Load an illustrative scenario", list(SCENARIOS))
    r=SCENARIOS[choice]
    score,raw,final,failed=calc(r)
    cols=st.columns(4)
    cols[0].metric("DAI",f"{score:.1f}")
    cols[1].metric("Without gates",raw)
    cols[2].metric("With gates",final)
    cols[3].metric("Failed gates",len(failed))
    if choice.startswith("E"):
        st.markdown("### Why 85/100 can still mean nominal access")
        st.write("Scenario E performs strongly on eight dimensions but privacy is rated 0. The privacy gate prevents a high average from compensating for an essential dignity failure.")
        if st.toggle("Repair the privacy lock — simulate one targeted fix"):
            fixed=r.copy(); fixed[1]=2
            s2,_,f2,_=calc(fixed)
            st.success(f"PRIVACY 0 → 2   ·   DAI {score:.1f} → {s2:.1f}   ·   NOMINAL → {f2.upper()}")
            st.caption("Illustrative intervention only. This is not a measured before–after result.")
    df=pd.DataFrame({"Dimension":[x[0] for x in DIMS],"Weight":[x[1] for x in DIMS],"Gate":[x[2] for x in DIMS],"Rating":r,"Status":[LABEL[x] for x in r]})
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.caption("Illustrative prototype — not a real facility audit.")

with tab3:
    st.subheader("Illustrative portfolio dashboard")
    st.caption("Demonstration using scenarios A–E only. These are not observations of five real toilets.")
    rows=[]
    for n,r in SCENARIOS.items():
        s,raw,final,failed=calc(r)
        rows.append({"Scenario":n.split(" — ")[0],"Toilet count":1,"DAI":s,"Gate failure":", ".join(failed) or "None","Classification":final})
    pdf=pd.DataFrame(rows)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Facilities in view",5)
    c2.metric("Usable",sum(pdf.Classification=="Usable"))
    c3.metric("Conditional",sum(pdf.Classification=="Conditional"))
    c4.metric("Nominal only",sum(pdf.Classification=="Nominal"))
    fig=go.Figure()
    fig.add_trace(go.Bar(x=pdf["Scenario"],y=pdf["DAI"],text=pdf["Classification"],textposition="auto"))
    fig.add_hline(y=50,line_dash="dot",annotation_text="50")
    fig.add_hline(y=70,line_dash="dash",annotation_text="70")
    fig.update_layout(height=390,yaxis_title="DAI score",xaxis_title="Illustrative scenario",showlegend=False,
paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(pdf,hide_index=True,use_container_width=True)
    st.info("Conventional infrastructure count: 5 toilets. DAI outcome: only 1 of the 5 illustrative facilities is classified usable. This is a conceptual demonstration, not a prevalence estimate.")

with tab4:
    st.subheader("Method")
    st.markdown("""
**Formula:** DAI = Σ(weight × rating ÷ 2), with weights summing to 100.

**Classification:**  
• **Usable:** score ≥70 and no essential gate rated 0  
• **Conditionally usable:** score 50–69 and no essential gate rated 0  
• **Nominal only:** score <50 **or any essential gate is 0**

**Essential gates:** Equitable entry, Privacy, Safety & lighting, Water.

The prototype is designed to make failures visible that a simple toilet count can miss. Its weights and thresholds are transparent judgement rules, not validated population parameters.
""")
    st.subheader("Participatory safeguard")
    st.write("Before real-world use, women users should co-define usability, rate facilities alongside auditors, and have disagreements recorded rather than overwritten. Real validation would require diverse participatory co-design, real facility audits, inter-rater testing, comparison with user-reported usability, threshold/weight testing and repeat audits.")
    st.subheader("Data minimisation")
    st.write("A real implementation should store facility-level observations only. It should not collect names, phone numbers, facial images, health diagnoses, unnecessary sensitive characteristics, or records tracking which individual used which toilet.")
    st.caption("Prototype developed for an academic Social Work project. Built-in data are illustrative.")

st.divider()
st.caption("DAI academic prototype · Facility-level decision support · Built-in scenarios A–E are illustrative, not real audits · The index is not a validated national measure.")
