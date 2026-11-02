import json, sqlite3, datetime, io, os, uuid, hmac
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import requests

BASE=Path(__file__).parent
DATA=BASE/"data"
DB=DATA/"academy.db"
DOMAINS={"D1":"Solution Design & Architecture","D2":"Claude Models, Prompting & Context Engineering","D3":"Integration & Tool Use","D4":"Evaluation, Testing & Optimisation","D5":"Governance, Safety & Risk Management","D6":"Stakeholder Communication & Lifecycle Management","D7":"Developer Productivity & Operational Enablement"}

st.set_page_config(page_title="CCAR-P Intelligence Academy · Full Edition",page_icon="🧠",layout="wide")

def conn():
    DATA.mkdir(exist_ok=True)
    c=sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS progress(id TEXT PRIMARY KEY,status TEXT,confidence INTEGER,notes TEXT,updated TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY,item TEXT,response TEXT,reflection TEXT,created TEXT)")
    cols={r[1] for r in c.execute("PRAGMA table_info(attempts)").fetchall()}
    if "cloud_id" not in cols: c.execute("ALTER TABLE attempts ADD COLUMN cloud_id TEXT")
    if "learner_id" not in cols: c.execute("ALTER TABLE attempts ADD COLUMN learner_id TEXT NOT NULL DEFAULT 'legacy'")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_attempts_cloud_id ON attempts(cloud_id) WHERE cloud_id IS NOT NULL")
    c.execute("CREATE TABLE IF NOT EXISTS imported(id TEXT PRIMARY KEY,payload TEXT,source TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS audit_events(id TEXT PRIMARY KEY, learner_id TEXT NOT NULL, event_type TEXT NOT NULL, details TEXT, created TEXT NOT NULL)")
    c.commit()
    return c

def bank():
    items=json.loads((BASE/"content/seed_concepts.json").read_text(encoding="utf-8"))
    professional_dir=BASE/"content/professional_lessons"
    if professional_dir.exists():
        for lesson_file in professional_dir.glob("*.json"):
            if lesson_file.name != "lesson_template.json":
                try: items.append(json.loads(lesson_file.read_text(encoding="utf-8")))
                except Exception: pass
    c=conn()
    for (raw,) in c.execute("SELECT payload FROM imported"):
        try:
            x=json.loads(raw); items.extend(x if isinstance(x,list) else [x])
        except Exception: pass
    unique={str(x.setdefault("id",f"X{n}")):x for n,x in enumerate(items)}
    return list(unique.values())

def render_structured(value):
    """Render nested lesson content as readable headings, bullets and code-like text."""
    if isinstance(value, dict):
        for key, item in value.items():
            label = key.replace("_", " ").strip().title()
            st.markdown(f"**{label}**")
            render_structured(item)
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, (dict, list)):
                st.markdown("---")
                render_structured(item)
            else:
                st.markdown(f"- {item}")
    else:
        st.markdown(str(value))

def audit_event(event_type, details=None):
    """Record a learner/admin action locally and in Supabase. Never record passwords."""
    event_id=str(uuid.uuid4())
    created=datetime.datetime.now(datetime.timezone.utc).isoformat()
    details=details or {}
    c=conn()
    c.execute("INSERT INTO audit_events(id,learner_id,event_type,details,created) VALUES(?,?,?,?,?)",
              (event_id,LEARNER_ID,event_type,json.dumps(details,ensure_ascii=False),created))
    c.commit()
    if CLOUD_SYNC:
        try:
            response=requests.post(
                f"{SUPABASE_URL}/rest/v1/audit_logs",
                headers={**cloud_headers(),"Prefer":"return=minimal"},
                json={"event_id":event_id,"learner_id":LEARNER_ID,"event_type":event_type,
                      "details":details,"created_at":created},timeout=15)
            response.raise_for_status()
        except Exception as exc:
            st.warning(f"Audit event saved locally but cloud audit sync failed: {exc}")

def save_progress(cid,status,confidence,notes):
    stored_id=f"{LEARNER_ID}::{cid}"
    updated=datetime.datetime.now().isoformat(timespec="minutes")
    c=conn(); c.execute("""INSERT INTO progress VALUES(?,?,?,?,?)
    ON CONFLICT(id) DO UPDATE SET status=excluded.status,confidence=excluded.confidence,notes=excluded.notes,updated=excluded.updated""",
    (stored_id,status,confidence,notes,updated)); c.commit()
    cloud_upsert("progress:"+cid,{"id":cid,"status":status,"confidence":confidence,"notes":notes,"updated":updated})
    audit_event("progress_saved", {"lesson_id":cid,"status":status,"confidence":confidence})

def say(text,key):
    safe=json.dumps(text[:6000],ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    components.html(f"""<button id="p{key}">▶ Read aloud</button> <button id="s{key}">■ Stop</button><span id="m{key}"></span>
    <script>const t{key}={safe};const v{key}=window.speechSynthesis;
    document.getElementById('p{key}').onclick=()=>{{if(!v{key})return;v{key}.cancel();let u=new SpeechSynthesisUtterance(t{key});u.lang='en-US';u.rate=.95;u.onstart=()=>document.getElementById('m{key}').textContent=' Speaking…';u.onend=()=>document.getElementById('m{key}').textContent=' Finished';v{key}.speak(u)}};
    document.getElementById('s{key}').onclick=()=>{{v{key}&&v{key}.cancel();document.getElementById('m{key}').textContent=' Stopped'}};</script>""",height=45)


def secret_value(section, key, default=""):
    try:
        return st.secrets.get(section, {}).get(key, default)
    except Exception:
        return default

SUPABASE_URL = secret_value("supabase", "url", "").rstrip("/")
SUPABASE_KEY = secret_value("supabase", "service_role_key", "")
ACADEMY_PASSWORD = secret_value("app", "access_password", "")
CLOUD_SYNC = bool(SUPABASE_URL and SUPABASE_KEY)

def cloud_headers():
    # Supabase sb_secret_ keys are sent as apikey; do not use them as Bearer JWTs.
    return {"apikey": SUPABASE_KEY,
            "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=minimal"}

def cloud_upsert(record_key, payload):
    if not CLOUD_SYNC: return False
    try:
        response=requests.post(
            f"{SUPABASE_URL}/rest/v1/academy_records?on_conflict=record_key",
            headers=cloud_headers(),
            json={"record_key":f"{LEARNER_ID}:{record_key}","owner_key":LEARNER_ID,"payload":payload,
                  "updated_at":datetime.datetime.now(datetime.timezone.utc).isoformat()}
        ,timeout=15)
        response.raise_for_status()
        return True
    except Exception as exc:
        st.warning(f"Cloud sync did not complete. Your local change is saved. Details: {exc}")
        return False

def sync_cloud_to_local():
    if not CLOUD_SYNC: return
    try:
        response=requests.get(
            f"{SUPABASE_URL}/rest/v1/academy_records?owner_key=eq.{LEARNER_ID}&select=record_key,payload",
            headers=cloud_headers(),timeout=15)
        response.raise_for_status()
        c=conn()
        for row in response.json():
            key=row.get("record_key","").split(":",1)[-1]
            payload=row.get("payload",{})
            if key.startswith("progress:"):
                c.execute("""INSERT INTO progress(id,status,confidence,notes,updated) VALUES(?,?,?,?,?)
                    ON CONFLICT(id) DO UPDATE SET status=excluded.status,confidence=excluded.confidence,
                    notes=excluded.notes,updated=excluded.updated""",
                    (f"{LEARNER_ID}::{payload.get('id')}",payload.get("status","Learning"),int(payload.get("confidence",0)),
                     payload.get("notes",""),payload.get("updated","")))
            elif key.startswith("attempt:"):
                cloud_id=f"{LEARNER_ID}:{key}"
                c.execute("INSERT OR IGNORE INTO attempts(item,response,reflection,created,cloud_id,learner_id) VALUES(?,?,?,?,?,?)",
                    (payload.get("item",""),payload.get("response",""),payload.get("reflection",""),
                     payload.get("created",""),cloud_id,LEARNER_ID))
            elif key.startswith("import:"):
                imported_payload=payload.get("payload",{})
                c.execute("INSERT OR REPLACE INTO imported(id,payload,source) VALUES(?,?,?)",
                    (payload.get("id",key.split(":",1)[1]),json.dumps(imported_payload,ensure_ascii=False),payload.get("source","cloud")))
        c.commit()
    except Exception as exc:
        st.warning(f"Cloud data could not be loaded. Local content remains available. Details: {exc}")

# Five named learner accounts plus an administrator account are configured in Streamlit secrets.
# Accept both TOML layouts:
#   [learners]
#   accounts = { learner1 = "...", ... }
# and
#   [learners.accounts]
#   learner1 = "..."
# Also tolerate the earlier flat [learners] layout.
def load_learner_accounts():
    try:
        section = st.secrets.get("learners", {})
        if not hasattr(section, "get"):
            return {}
        nested = section.get("accounts", None)
        if hasattr(nested, "get"):
            return {f"learner{i}": str(nested.get(f"learner{i}", "") or "")
                    for i in range(1, 6)}
        # Backward compatibility with flat [learners] learner1=... entries.
        return {f"learner{i}": str(section.get(f"learner{i}", "") or "")
                for i in range(1, 6)}
    except Exception:
        return {}

LEARNERS = load_learner_accounts()
ADMIN_PASSWORD = secret_value("admin", "password", "")

def authenticate_user():
    if not CLOUD_SYNC:
        st.error("Multi-learner mode requires Supabase cloud sync. Configure [supabase] url and service_role_key in Streamlit secrets.")
        return False
    if st.session_state.get("academy_user"):
        return True
    st.title("🔐 CCAR-P Intelligence Academy")
    st.write("Sign in with your assigned learner account. Each learner has a separate progress record.")
    # Safe diagnostic: reports the number of configured accounts, never their passwords.
    configured_count = sum(bool(LEARNERS.get(f"learner{i}", "")) for i in range(1, 6))
    st.caption(f"Learner accounts loaded: {configured_count} of 5")
    role=st.radio("Sign in as",["Learner","Administrator"],horizontal=True)
    if role=="Learner":
        username=st.selectbox("Learner account",[f"learner{i}" for i in range(1,6)])
        password=st.text_input("Your personal password",type="password")
        if st.button("Sign in",type="primary"):
            # Streamlit Secrets may expose nested TOML tables as mapping-like
            # objects rather than plain dict instances. Use the mapping interface.
            try:
                expected_value = LEARNERS.get(username, "") if hasattr(LEARNERS, "get") else ""
            except Exception:
                expected_value = ""
            expected = str(expected_value) if expected_value is not None else ""
            if expected and hmac.compare_digest(password,expected):
                st.session_state["academy_user"]=username
                st.session_state["academy_role"]="learner"
                st.session_state["audit_login_pending"]=True
                st.rerun()
            st.error("Invalid learner account or password. Contact the Academy administrator.")
    else:
        password=st.text_input("Administrator password",type="password")
        if st.button("Administrator sign in",type="primary"):
            if ADMIN_PASSWORD and hmac.compare_digest(password,str(ADMIN_PASSWORD)):
                st.session_state["academy_user"]="admin"
                st.session_state["academy_role"]="admin"
                st.session_state["audit_login_pending"]=True
                st.rerun()
            st.error("Incorrect administrator password.")
    st.caption("Learner accounts are private. Do not share passwords. The administrator can issue or reset credentials.")
    return False

if not authenticate_user():
    st.stop()
LEARNER_ID=st.session_state["academy_user"]
IS_ADMIN=st.session_state.get("academy_role")=="admin"
if st.session_state.pop("audit_login_pending",False): audit_event("sign_in", {"role":st.session_state.get("academy_role")})
if not IS_ADMIN:
    sync_cloud_to_local()

items=bank()
st.markdown("""<style>.stApp{background:#171A1D;color:#F4F6F8}[data-testid="stSidebar"]{background:#20262B}div[data-testid="stMetric"]{background:#20262B;padding:12px;border-radius:10px}</style>""",unsafe_allow_html=True)
st.sidebar.title("🧠 CCAR-P Academy")
st.sidebar.caption("Multi-learner Edition · 29 professional lessons · 7 domains")
st.sidebar.write(f"Signed in: **{LEARNER_ID}**")
if st.sidebar.button("Sign out"):
    audit_event("sign_out", {"role":st.session_state.get("academy_role")})
    for k in ["academy_user","academy_role"]: st.session_state.pop(k,None)
    st.rerun()
st.sidebar.caption("Think like an Architect. Build like an Engineer.")
workspace=["Administrator Dashboard"] if IS_ADMIN else ["Dashboard","Learning Path","Learn by Domain","Assessment Centre","Practice Centre","Guided Tutor","Voice Reader","Question Bank","Progress & Backup","About"]
page=st.sidebar.radio("Workspace",workspace)
st.sidebar.success("Zero paid API keys required")

if page=="Administrator Dashboard":
    st.title("Academy Administrator Dashboard")
    st.caption("Five learner accounts · individual progress and assessment records")
    st.info("Learners cannot view one another's records. This dashboard provides cohort-level monitoring.")
    summaries=[]
    for learner in [f"learner{i}" for i in range(1,6)]:
        try:
            r=requests.get(f"{SUPABASE_URL}/rest/v1/academy_records?owner_key=eq.{learner}&select=record_key,payload",headers=cloud_headers(),timeout=15)
            r.raise_for_status(); records=r.json()
            prog=[x.get("payload",{}) for x in records if str(x.get("record_key","")).endswith(":progress:"+str(x.get("payload",{}).get("id","")))]
            attempts=[x for x in records if ":attempt:" in str(x.get("record_key", ""))]
            mastered=sum(x.get("status")=="Mastered" for x in prog)
            summaries.append({"Learner":learner,"Lessons tracked":len(prog),"Mastered":mastered,"Assessment attempts":len(attempts)})
        except Exception as exc:
            st.warning(f"Could not load {learner}: {exc}")
    if summaries: st.dataframe(summaries,use_container_width=True,hide_index=True)
    st.markdown("### Account management")
    st.write("Set or reset learner passwords in Streamlit → Manage app → Settings → Secrets, under the `[learners]` section. Never share the administrator password.")
    st.code('[learners]\naccounts = { learner1 = "SET_A_UNIQUE_PASSWORD", learner2 = "SET_A_UNIQUE_PASSWORD", learner3 = "SET_A_UNIQUE_PASSWORD", learner4 = "SET_A_UNIQUE_PASSWORD", learner5 = "SET_A_UNIQUE_PASSWORD" }\n\n[admin]\npassword = "SET_A_DIFFERENT_ADMIN_PASSWORD"',language="toml")
    st.subheader("Recent audit activity")
    try:
        audit_response=requests.get(f"{SUPABASE_URL}/rest/v1/audit_logs?select=learner_id,event_type,details,created_at&order=created_at.desc&limit=100",headers=cloud_headers(),timeout=15)
        audit_response.raise_for_status()
        audit_rows=audit_response.json()
        if audit_rows: st.dataframe(audit_rows,use_container_width=True,hide_index=True)
        else: st.caption("No audit events recorded yet.")
    except Exception as exc:
        st.warning(f"Audit log unavailable: {exc}")
    st.warning("The administrator dashboard reads cohort records and audit events from Supabase. Keep the Supabase secret key private and never put it in GitHub.")

if page=="Dashboard":
    st.title("CCAR-P Intelligence Academy")
    st.write("Your local-first preparation workspace for architecture judgement, Claude systems, integration, evaluation and governance.")
    c=conn(); mastered=c.execute("SELECT COUNT(*) FROM progress WHERE id LIKE ? AND status='Mastered'",(f"{LEARNER_ID}::%",)).fetchone()[0]
    tracked=c.execute("SELECT COUNT(*) FROM progress WHERE id LIKE ?",(f"{LEARNER_ID}::%",)).fetchone()[0]
    attempts=c.execute("SELECT COUNT(*) FROM attempts WHERE learner_id=?",(LEARNER_ID,)).fetchone()[0]
    pro_count=sum(x.get("schema_version")=="2.0" for x in items)
    question_count=sum(len(x.get("knowledge_check",[])) for x in items if x.get("schema_version")=="2.0")
    a,b,d,e,f=st.columns(5); a.metric("Curriculum records",len(items)); b.metric("Professional lessons",pro_count); d.metric("Mastered",mastered); e.metric("Tracked",tracked); f.metric("Assessment attempts",attempts)
    st.caption(f"{question_count} original professional knowledge checks across the seven domains.")
    st.subheader("Seven-domain curriculum")
    for code,name in DOMAINS.items():
        count=sum(x.get("domain")==code for x in items)
        st.write(f"**{code} · {name}** — {count} concepts"); st.progress(min(count/8,1.0))
    st.info("Starter material contains concept summaries, not verbatim official exam questions. Import your full question sets as you obtain them.")
    if CLOUD_SYNC:
        st.success("Cloud database configured: progress and assessment attempts sync across devices.")
    else:
        st.warning("Local storage mode: on a hosted deployment, progress may not survive app rebuilds or restarts. Configure the optional cloud database for durable cross-device progress.")

elif page=="Learning Path":
    st.title("Professional Architect Learning Path")
    st.write("A structured route through the seven domains. Work through the professional lessons, complete their laboratories, then defend your design decisions.")
    for code,name in DOMAINS.items():
        domain_items=[x for x in items if x.get("domain")==code]
        professional=[x for x in domain_items if x.get("schema_version")=="2.0"]
        st.subheader(f"{code} · {name}")
        st.caption(f"{len(professional)} professional lessons · {len(domain_items)} total curriculum records")
        for lesson in professional:
            st.markdown(f"- **{lesson['id']} — {lesson['title']}** · {lesson.get('estimated_minutes','—')} min")
    st.info("Suggested cadence: learn the first principles, work through the lab, complete the knowledge checks, then write a short architecture decision defence.")
elif page=="Assessment Centre":
    st.title("Professional Assessment Centre")
    st.caption("Original practice questions and rubric-based self-assessment. These are not official Anthropic examination questions.")
    professional=[x for x in items if x.get("schema_version")=="2.0"]
    if professional:
        selected=st.selectbox("Select professional lesson",professional,format_func=lambda x:f"{x['id']} · {x['title']}")
        st.subheader(selected["title"])
        questions=selected.get("knowledge_check",[])
        for q in questions:
            with st.container(border=True):
                st.markdown(f"**{q.get('id','')} · {q.get('difficulty','')} · {q.get('type','').replace('_',' ').title()}**")
                st.write(q.get("question",""))
                response=st.text_area("Your answer / reasoning",key=LEARNER_ID+"_assess_"+q.get("id",""),height=100)
                with st.expander("Reveal answer and explanation"):
                    st.markdown("**Expected answer / rubric**")
                    render_structured(q.get("answer",""))
                    st.markdown("**Why this matters**")
                    st.write(q.get("explanation",""))
                if st.button("Save assessment response",key=LEARNER_ID+"_save_"+q.get("id","")):
                    c=conn()
                    reflection=f"Lesson {selected['id']} · {q.get('difficulty','')} · Self-assess against the rubric."
                    created=datetime.datetime.now().isoformat(timespec="minutes")
                    cloud_id=str(uuid.uuid4())
                    c.execute("INSERT INTO attempts(item,response,reflection,created,cloud_id,learner_id) VALUES(?,?,?,?,?,?)",
                              (q.get("id",""),response,reflection,created,f"{LEARNER_ID}:{cloud_id}",LEARNER_ID))
                    c.commit()
                    cloud_upsert("attempt:"+cloud_id,{"item":q.get("id",""),"response":response,
                                  "reflection":reflection,"created":created})
                    audit_event("assessment_response_saved", {"question_id":q.get("id",""),"lesson_id":selected["id"]})
                    st.success("Response saved to your learning record.")
    else:
        st.info("Professional lessons will appear here when loaded.")

elif page=="Learn by Domain":
    st.title("Learn by Domain")
    d=st.selectbox("Choose domain",list(DOMAINS),format_func=lambda x:f"{x} · {DOMAINS[x]}")
    for x in [x for x in items if x.get("domain")==d]:
        with st.expander(x["title"]+" · "+x.get("difficulty","")):
            if x.get("schema_version") == "2.0":
                st.caption(f"Professional lesson · {x.get('estimated_minutes','—')} minutes · reviewed {x.get('as_of','date not supplied')}")
                st.markdown("### Learning outcomes")
                for outcome in x.get("learning_outcomes", []): st.markdown(f"- {outcome}")
                for heading, field in [
                    ("Executive orientation","executive_orientation"),
                    ("First-principles explanation","first_principles"),
                    ("Technical deep dive","technical_deep_dive"),
                    ("Security and governance","security_governance")
                ]:
                    value=x.get(field)
                    if value:
                        st.markdown(f"### {heading}")
                        if isinstance(value,list):
                            for item in value: st.markdown(f"- {item}")
                        else: st.markdown(value)
                pattern=x.get("architecture_pattern",{})
                if pattern:
                    st.markdown("### Architecture pattern and decision criteria")
                    for label,key in [("When to use","when_to_use"),("When not to use","when_not_to_use"),("Alternatives","alternatives"),("Decision criteria","decision_criteria")]:
                        vals=pattern.get(key,[])
                        if vals:
                            st.markdown(f"**{label}**")
                            for val in vals: st.markdown(f"- {val}")
                if x.get("diagram_mermaid"):
                    st.markdown("### Architecture flow")
                    st.code(x["diagram_mermaid"],language="mermaid")
                for heading, field in [
                    ("Worked example","worked_example"),
                    ("Implementation laboratory","implementation_lab"),
                    ("Trade-off analysis","tradeoffs"),
                    ("Failure modes","failure_modes"),
                    ("Evaluation strategy","evaluation"),
                    ("Production readiness checklist","production_checklist"),
                    ("Case study","case_study"),
                    ("Architect challenge","architect_challenge"),
                    ("Knowledge check","knowledge_check"),
                    ("Further reading","further_reading"),
                    ("Key takeaways","key_takeaways")
                ]:
                    value=x.get(field)
                    if value:
                        with st.expander(heading, expanded=heading in ["Worked example","Implementation laboratory"]):
                            render_structured(value)
                if x.get("implementation_lab",{}).get("code"):
                    st.markdown("**Lab code**")
                    st.code(x["implementation_lab"]["code"],language=x["implementation_lab"].get("code_language","python"))
                read_text=" ".join([x.get("executive_orientation",""),x.get("first_principles",""),x.get("technical_deep_dive","")])
            else:
                st.markdown("**Core idea**"); st.write(x.get("core_idea",""))
                st.markdown("**Architect's perspective**"); st.write(x.get("architect_note",""))
                if x.get("explanation"): st.markdown("**Explanation**"); st.write(x["explanation"])
                read_text=x.get("explanation") or x.get("core_idea","")
            say(read_text,"L"+str(abs(hash(x["id"]))%1000000))
            with st.form("f"+x["id"]):
                status=st.selectbox("Mastery",["Not started","Learning","Practised","Mastered"],key=LEARNER_ID+"_s"+x["id"])
                confidence=st.slider("Confidence",0,5,0,key=LEARNER_ID+"_c"+x["id"])
                notes=st.text_area("Notes",key=LEARNER_ID+"_n"+x["id"])
                if st.form_submit_button("Save progress"):
                    save_progress(x["id"],status,confidence,notes); st.success("Saved")
elif page=="Practice Centre":
    st.title("Practice & Reflection")
    x=st.selectbox("Select item",items,format_func=lambda x:f'{x["id"]} · {x.get("title","")}')
    st.subheader(x.get("title","")); st.write(x.get("question") or x.get("core_idea",""))
    if x.get("options"):
        for i,opt in enumerate(x["options"]): st.write(f"{chr(65+i)}. {opt}")
        answer=st.radio("Your answer",list("ABCD")[:len(x["options"])],horizontal=True)
    else: answer=st.text_area("Your architectural response",height=140)
    confidence=st.slider("Confidence",1,5,3)
    if st.button("Save attempt"):
        c=conn(); created=datetime.datetime.now().isoformat(timespec="minutes"); cloud_id=str(uuid.uuid4())
        reflection=f"Confidence {confidence}/5"
        c.execute("INSERT INTO attempts(item,response,reflection,created,cloud_id,learner_id) VALUES(?,?,?,?,?,?)",(x["title"],str(answer),reflection,created,f"{LEARNER_ID}:{cloud_id}",LEARNER_ID)); c.commit()
        cloud_upsert("attempt:"+cloud_id,{"item":x["title"],"response":str(answer),"reflection":reflection,"created":created})
        audit_event("practice_attempt_saved", {"item":x["title"],"confidence":confidence})
        st.success("Attempt saved")
    if x.get("correct_answer"):
        with st.expander("Reveal answer"):
            st.write("Expected answer:",x["correct_answer"]); st.write(x.get("explanation",""))
elif page=="Guided Tutor":
    st.title("Guided Architecture Tutor")
    st.caption("Curriculum retrieval only; no paid AI call.")
    q=st.text_area("What do you want to understand?",height=110)
    mode=st.selectbox("Teaching style",["First principles","Analogy","Trade-offs","Examiner challenge"])
    if st.button("Build lesson") and q.strip():
        words=[w for w in q.lower().split() if len(w)>3]
        ranked=[]
        for x in items:
            hay=" ".join(str(x.get(k,"")) for k in ["title","core_idea","architect_note","executive_orientation","first_principles","technical_deep_dive"]).lower()
            score=sum(w in hay for w in words)
            if score: ranked.append((score,x))
        ranked.sort(key=lambda z:z[0],reverse=True)
        answer=[]
        for _,x in ranked[:4]:
            answer += [f"### {x['title']}",f"**First principle:** {x.get('core_idea','')}",f"**Architect's lens:** {x.get('architect_note','')}"]
        if not answer: answer=["No close curriculum match. Try MCP, context engineering, tool use, RAG, evaluation, governance or observability."]
        if mode=="Analogy": answer.append("**Analogy exercise:** Explain the concept using a familiar everyday process, then identify where the analogy breaks.")
        if mode=="Trade-offs": answer.append("**Trade-offs:** latency · cost · reliability · security · observability · maintainability.")
        if mode=="Examiner challenge": answer.append("**Examiner challenge:** Defend your recommendation against a simpler alternative. When would you change it?")
        answer.append("**Test yourself:** What requirement drives the design? What can fail? How will you validate it?")
        result="\n\n".join(answer); st.markdown(result); say(result,"TUTOR")
elif page=="Voice Reader":
    st.title("Voice Reader")
    t=st.text_area("Paste a lesson or revision note",height=220)
    if t.strip(): say(t,"READER")
    st.warning("Uses browser/device text-to-speech where available. Speech recognition is not guaranteed free or offline.")
elif page=="Question Bank":
    st.title("Expandable Question Bank")
    st.write("Import JSON or CSV. Suggested JSON format:")
    st.code('[{"id":"Q001","domain":"D1","title":"Title","question":"Question","options":["A","B","C","D"],"correct_answer":"B","explanation":"Why","difficulty":"Intermediate"}]',language="json")
    if IS_ADMIN:
        up=st.file_uploader("Upload question bank",type=["json","csv"])
    else:
        up=None
        st.caption("Question-bank imports are managed by the administrator.")
    if up and st.button("Import"):
        try:
            raw=up.getvalue().decode("utf-8-sig")
            if up.name.lower().endswith(".json"): parsed=json.loads(raw)
            else:
                import csv; parsed=list(csv.DictReader(io.StringIO(raw)))
            parsed=parsed if isinstance(parsed,list) else [parsed]
            c=conn()
            for i,x in enumerate(parsed):
                x.setdefault("id",f"IMP-{datetime.datetime.now():%Y%m%d%H%M%S}-{i}")
                x.setdefault("domain","Unclassified"); x.setdefault("title",str(x.get("question","Imported"))[:100])
                c.execute("INSERT OR REPLACE INTO imported VALUES(?,?,?)",(str(x["id"]),json.dumps(x,ensure_ascii=False),up.name))
                cloud_upsert("import:"+str(x["id"]),{"id":str(x["id"]),"payload":x,"source":up.name})
            c.commit(); st.success(f"Imported {len(parsed)} records"); st.rerun()
        except Exception as ex: st.error(str(ex))
    st.write(f"{len(items)} records available.")
    st.download_button("Export imported questions",json.dumps([x for x in items if str(x["id"]).startswith("IMP-")],ensure_ascii=False,indent=2),"question_bank.json","application/json")
elif page=="Progress & Backup":
    st.title("Progress & Backup")
    c=conn()
    rows=c.execute("SELECT id,status,confidence,notes,updated FROM progress WHERE id LIKE ? ORDER BY updated DESC",(f"{LEARNER_ID}::%",)).fetchall()
    attempts=c.execute("SELECT item,response,reflection,created FROM attempts WHERE learner_id=? ORDER BY id DESC",(LEARNER_ID,)).fetchall()
    a,b,d=st.columns(3); a.metric("Mastered",sum(r[1]=="Mastered" for r in rows)); b.metric("Tracked",len(rows)); d.metric("Attempts",len(attempts))
    if rows: st.dataframe([{"ID":r[0].split("::",1)[-1],"Status":r[1],"Confidence":r[2],"Notes":r[3],"Updated":r[4]} for r in rows],use_container_width=True)
    for item,response,reflection,created in attempts[-30:]:
        with st.expander(f"{item} · {created}"): st.write(response); st.caption(reflection)
    st.markdown("### Restore a previous academy backup")
    backup_file=st.file_uploader("Upload a previously downloaded ccarp_backup.json",type=["json"],key="restore_backup")
    if backup_file and st.button("Restore backup into this academy"):
        try:
            restored=json.loads(backup_file.getvalue().decode("utf-8"))
            for item in restored.get("progress",[]):
                c.execute("""INSERT INTO progress(id,status,confidence,notes,updated) VALUES(?,?,?,?,?)
                    ON CONFLICT(id) DO UPDATE SET status=excluded.status,confidence=excluded.confidence,
                    notes=excluded.notes,updated=excluded.updated""",
                    (f"{LEARNER_ID}::{item['id']}",item.get("status","Learning"),int(item.get("confidence",0)),item.get("notes",""),item.get("updated","")))
                cloud_upsert("progress:"+item["id"],item)
            for item in restored.get("attempts",[]):
                cloud_id=str(uuid.uuid4())
                c.execute("INSERT INTO attempts(item,response,reflection,created,cloud_id,learner_id) VALUES(?,?,?,?,?,?)",
                    (item.get("item",""),item.get("response",""),item.get("reflection",""),item.get("created",""),f"{LEARNER_ID}:{cloud_id}",LEARNER_ID))
                cloud_upsert("attempt:"+cloud_id,item)
            for item in restored.get("imported",[]):
                item_id=str(item.get("id") or ("RESTORED-"+str(uuid.uuid4())))
                c.execute("INSERT OR REPLACE INTO imported(id,payload,source) VALUES(?,?,?)",
                    (item_id,json.dumps(item,ensure_ascii=False),"restored backup"))
                cloud_upsert("import:"+item_id,{"id":item_id,"payload":item,"source":"restored backup"})
            c.commit()
            st.success("Backup restored. Refresh the page to view the restored records.")
            st.rerun()
        except Exception as ex:
            st.error(f"Could not restore backup: {ex}")
    backup={"progress":[dict(zip(["id","status","confidence","notes","updated"],r)) for r in rows],"attempts":[dict(zip(["item","response","reflection","created"],r)) for r in attempts],"imported":[json.loads(r[0]) for r in c.execute("SELECT payload FROM imported")]}
    st.download_button("Download academy backup",json.dumps(backup,ensure_ascii=False,indent=2),"ccarp_backup.json","application/json")
else:
    st.title("About Full Edition 2.1")
    st.success("No OpenAI or Anthropic API key is required.")
    st.markdown("""
- Lessons, local curriculum tutor, question import, practice records and progress tracking work locally.
- Text-to-speech uses browser/device voices where supported.
- Your local database is stored at `data/academy.db`.
- Cloud sync is optional and uses a Supabase Postgres table when configured in Streamlit secrets.
- Without cloud sync, Streamlit Community Cloud's local filesystem must not be treated as durable storage.
- First launch needs internet to install Streamlit.
- This is an independent study aid, not an official Anthropic exam platform. Confirm current objectives and API details with official documentation.
""")
