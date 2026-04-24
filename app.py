import streamlit as st
import openai
import csv
import json
import io
import os
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StayVista · Villa Acquisition Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@300;400;500;700&family=Jost:wght@300;400;500&display=swap');

:root {
    --ink:     #0B0B0B;
    --surface: #111111;
    --card:    #181818;
    --border:  #262626;
    --gold:    #C8A45A;
    --gold2:   #E6C97A;
    --text:    #EBEBEB;
    --muted:   #777;
    --green:   #52C97B;
    --red:     #E05A5A;
}

html, body, [class*="css"] {
    font-family: 'Jost', sans-serif;
    background: var(--ink);
    color: var(--text);
}
.stApp { background: var(--ink); }

.app-header {
    padding: 2.8rem 0 1.6rem;
    text-align: center;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.4rem;
    position: relative;
}
.app-header::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 60px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.app-header .eyebrow {
    font-size: 0.68rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.6rem;
}
.app-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 300;
    color: var(--text);
    margin: 0;
    line-height: 1.1;
}
.app-header h1 span { color: var(--gold); }
.app-header .sub {
    color: var(--muted);
    font-size: 0.82rem;
    letter-spacing: 0.1em;
    margin-top: 0.6rem;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
.sidebar-brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: var(--gold) !important;
    text-align: center;
    padding: 1.4rem 0 1rem;
    border-bottom: 1px solid var(--border);
    letter-spacing: 0.06em;
    margin-bottom: 1.4rem;
}
.sidebar-section {
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold);
    margin: 1.2rem 0 0.5rem;
}
.sidebar-item {
    font-size: 0.82rem;
    color: var(--muted) !important;
    padding: 0.18rem 0;
}

.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: var(--gold);
    font-weight: 400;
    margin-bottom: 0.8rem;
}

.metric-strip {
    display: flex;
    gap: 0.8rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.metric-tile {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 1rem 1.4rem;
    flex: 1;
    min-width: 90px;
    text-align: center;
}
.metric-val {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 300;
    line-height: 1;
}
.metric-lbl {
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.3rem;
}
.gold  { color: var(--gold); }
.green { color: var(--green); }
.red   { color: var(--red); }

.pills { display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0.6rem 0; }
.pill {
    background: rgba(200,164,90,0.12);
    border: 1px solid rgba(200,164,90,0.35);
    color: var(--gold2);
    border-radius: 2px;
    padding: 0.18rem 0.55rem;
    font-size: 0.73rem;
    letter-spacing: 0.04em;
}
.pill-miss {
    background: rgba(224,90,90,0.08);
    border-color: rgba(224,90,90,0.25);
    color: #E07070;
}

.score-wrap {
    text-align: center;
    padding: 1rem 0;
}
.score-num {
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 300;
    line-height: 1;
}
.score-denom { font-size: 1rem; color: var(--muted); }
.score-label {
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.3rem;
}
.score-rationale {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 0.7rem;
    line-height: 1.6;
    font-style: italic;
}

.spec-row {
    display: flex;
    justify-content: space-between;
    padding: 0.35rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.83rem;
}
.spec-row:last-child { border-bottom: none; }
.spec-key { color: var(--muted); }
.spec-val { color: var(--text); font-weight: 500; }

.transcript-box {
    background: #0D0D0D;
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 1rem 1.2rem;
    font-size: 0.8rem;
    color: #999;
    max-height: 220px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    line-height: 1.65;
}

.stButton > button {
    background: var(--gold) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Jost', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 2rem !important;
    font-weight: 500 !important;
}
.stButton > button:hover { background: var(--gold2) !important; }

[data-testid="stFileUploader"] {
    border: 1px dashed var(--border) !important;
    background: var(--card) !important;
    border-radius: 3px !important;
}

.stProgress > div > div { background: var(--gold) !important; }

[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 2px !important;
    font-family: 'Jost', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(200,164,90,0.1) !important;
}

[data-testid="stExpander"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
}

.status { font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; }
.status-active { color: var(--gold); }
.status-done   { color: var(--green); }

hr { border-color: var(--border) !important; }

.empty-state {
    text-align: center;
    padding: 5rem 2rem;
    color: var(--muted);
}
.empty-state .icon { font-size: 3.5rem; margin-bottom: 1rem; opacity: 0.4; }
.empty-state p { font-family: 'Playfair Display', serif; font-size: 1.3rem; color: #444; }
.empty-state small { font-size: 0.82rem; color: #3A3A3A; line-height: 1.8; display: block; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="eyebrow">StayVista · Acquisition Intelligence</div>
    <h1>Villa <span>Analysis</span> Suite</h1>
    <div class="sub">Whisper Transcription · GPT-4 Extraction · CSV Export</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⬡ StayVista</div>', unsafe_allow_html=True)

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Your key is used only for this session and never stored.",
    )

    st.markdown('<div class="sidebar-section">Workflow</div>', unsafe_allow_html=True)
    for step in [
        "① Upload audio files (MP3/WAV/M4A/OGG)",
        "② Whisper transcribes the speech",
        "③ GPT-4o extracts all villa data",
        "④ Download structured CSV report",
    ]:
        st.markdown(f'<div class="sidebar-item">{step}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Amenities Tracked</div>', unsafe_allow_html=True)
    for a in [
        "Swimming Pool", "Jacuzzi / Hot Tub", "Lawn & Garden",
        "Servant Quarters", "Parking", "Generator Backup",
        "CCTV / Security", "Home Theatre", "Gym / Fitness",
        "Terrace / Rooftop", "Bar & Lounge", "Bonfire Area",
        "Pet Friendly", "Chef / Cook", "AC Rooms",
        "Modular Kitchen", "Outdoor Seating",
        "Mountain / Sea / Forest View",
    ]:
        st.markdown(f'<div class="sidebar-item">· {a}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("OpenAI Whisper · GPT-4o · StayVista")

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior real-estate acquisition analyst for StayVista, India's leading premium villa rental platform.
Your task: analyze a villa walkthrough audio transcript and extract every relevant data point for acquisition evaluation.

Return ONLY a valid JSON object — no markdown fences, no explanation. Use this exact structure:
{
  "villa_name": "string or Unknown",
  "location": {
    "city": "",
    "state": "",
    "locality": "",
    "full_address": "",
    "nearby_landmarks": "",
    "distance_from_city": ""
  },
  "property_details": {
    "bedrooms": null,
    "bathrooms": null,
    "total_area_sqft": null,
    "plot_area_sqft": null,
    "floors": null,
    "year_built": null,
    "property_type": "Villa/Farmhouse/Bungalow/Cottage/Other"
  },
  "amenities": {
    "swimming_pool": false,
    "pool_type": "",
    "pool_heated": false,
    "jacuzzi": false,
    "lawn_garden": false,
    "lawn_size_sqft": null,
    "servant_quarters": false,
    "servant_quarters_count": null,
    "parking": false,
    "parking_capacity": null,
    "generator_backup": false,
    "cctv_security": false,
    "home_theatre": false,
    "gym_fitness": false,
    "terrace_rooftop": false,
    "bar_lounge": false,
    "bonfire_area": false,
    "pet_friendly": false,
    "chef_cook_available": false,
    "ac_rooms": false,
    "ac_rooms_count": null,
    "modular_kitchen": false,
    "outdoor_seating": false,
    "mountain_view": false,
    "sea_view": false,
    "forest_view": false,
    "other_amenities": []
  },
  "acquisition": {
    "asking_price_inr": null,
    "price_per_sqft_inr": null,
    "price_negotiable": null,
    "ownership_type": "Freehold/Leasehold/Unknown",
    "caretaker_present": false,
    "currently_operational": false,
    "existing_bookings": false,
    "annual_revenue_inr": null,
    "legal_issues_mentioned": false,
    "renovation_needed": false,
    "renovation_estimate_inr": null,
    "contact_person": "",
    "contact_number": ""
  },
  "stayvista_fit_score": 0,
  "stayvista_fit_rationale": "",
  "key_highlights": [],
  "concerns": [],
  "acquisition_recommendation": "Strong Buy / Buy / Hold / Pass",
  "summary": ""
}

Scoring (stayvista_fit_score 0-100):
80-100: Premium location + 5+ luxury amenities + strong revenue potential
60-79: Good property, solid amenities, minor gaps
40-59: Acceptable but needs investment or has location concerns
0-39:  Poor fit for StayVista brand

Fill every field you can infer. Use null for unknown numbers, false for unknown booleans."""


# ── Transcribe with Whisper ───────────────────────────────────────────────────
def transcribe_audio(client: openai.OpenAI, file_bytes: bytes, filename: str) -> str:
    buf = io.BytesIO(file_bytes)
    buf.name = filename
    resp = client.audio.transcriptions.create(
        model="whisper-1",
        file=buf,
        response_format="text",
        language="en",
    )
    return resp


# ── Extract with GPT-4o ───────────────────────────────────────────────────────
def extract_villa_data(client: openai.OpenAI, transcript: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"TRANSCRIPT:\n\n{transcript}"},
        ],
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Flatten to CSV row ────────────────────────────────────────────────────────
def flatten_to_csv_row(data: dict, filename: str) -> dict:
    row = {
        "source_file": filename,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "villa_name": data.get("villa_name", ""),
    }
    loc = data.get("location", {})
    row.update({k: loc.get(k, "") for k in ["city","state","locality","full_address","nearby_landmarks","distance_from_city"]})

    prop = data.get("property_details", {})
    row.update({k: prop.get(k, "") for k in ["bedrooms","bathrooms","total_area_sqft","plot_area_sqft","floors","year_built","property_type"]})

    am = data.get("amenities", {})
    for key in [
        "swimming_pool","pool_type","pool_heated","jacuzzi",
        "lawn_garden","lawn_size_sqft","servant_quarters","servant_quarters_count",
        "parking","parking_capacity","generator_backup","cctv_security",
        "home_theatre","gym_fitness","terrace_rooftop","bar_lounge",
        "bonfire_area","pet_friendly","chef_cook_available","ac_rooms","ac_rooms_count",
        "modular_kitchen","outdoor_seating","mountain_view","sea_view","forest_view",
    ]:
        row[key] = am.get(key, "")
    row["other_amenities"] = " | ".join(am.get("other_amenities", []))

    acq = data.get("acquisition", {})
    row.update({k: acq.get(k, "") for k in [
        "asking_price_inr","price_per_sqft_inr","price_negotiable","ownership_type",
        "caretaker_present","currently_operational","existing_bookings","annual_revenue_inr",
        "legal_issues_mentioned","renovation_needed","renovation_estimate_inr",
        "contact_person","contact_number",
    ]})

    row.update({
        "stayvista_fit_score": data.get("stayvista_fit_score", ""),
        "acquisition_recommendation": data.get("acquisition_recommendation", ""),
        "stayvista_fit_rationale": data.get("stayvista_fit_rationale", ""),
        "key_highlights": " | ".join(data.get("key_highlights", [])),
        "concerns": " | ".join(data.get("concerns", [])),
        "summary": data.get("summary", ""),
    })
    return row


def build_csv(rows: list) -> bytes:
    if not rows:
        return b""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def score_color(s):
    if s >= 70: return "green"
    if s >= 40: return "gold"
    return "red"


def rec_emoji(rec: str) -> str:
    for k, v in {"strong buy": "🟢", "buy": "🟡", "hold": "🟠", "pass": "🔴"}.items():
        if k in rec.lower():
            return v
    return "⬜"


# ── Upload section ────────────────────────────────────────────────────────────
col_up, col_tip = st.columns([3, 2])

with col_up:
    uploaded_files = st.file_uploader(
        "Upload villa audio recordings",
        type=["mp3", "wav", "m4a", "ogg", "flac", "webm", "mp4"],
        accept_multiple_files=True,
        help="Upload walkthrough audio. MP3, WAV, M4A, OGG, FLAC supported.",
    )

with col_tip:
    st.markdown("""
    <div class="card">
        <div class="card-title">Recording Tips</div>
        <p style="color:#777; font-size:0.83rem; line-height:1.75; margin:0">
            Record villa walkthroughs on your phone and export as <strong style="color:#ccc">MP3 or M4A</strong>.
            The owner / agent narration is captured by Whisper, then GPT-4o extracts
            every data point StayVista needs — no manual entry required.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Process ───────────────────────────────────────────────────────────────────
if uploaded_files:
    n = len(uploaded_files)
    st.markdown(f"<p style='color:var(--muted); font-size:0.82rem'>📎 {n} file(s) queued — {', '.join(f.name for f in uploaded_files)}</p>", unsafe_allow_html=True)

    if not api_key:
        st.warning("⚠️  Enter your OpenAI API key in the sidebar to proceed.")
    else:
        if st.button(f"🔍  Analyse {n} Villa Recording{'s' if n > 1 else ''}"):
            oai = openai.OpenAI(api_key=api_key)
            all_results, all_rows = [], []
            progress = st.progress(0)
            status = st.empty()

            for idx, uf in enumerate(uploaded_files):
                fname = uf.name
                fbytes = uf.read()

                status.markdown(f'<p class="status status-active">⟳ [{idx+1}/{n}] Transcribing {fname} via Whisper…</p>', unsafe_allow_html=True)
                try:
                    transcript = transcribe_audio(oai, fbytes, fname)
                except Exception as e:
                    st.error(f"Transcription failed — {fname}: {e}")
                    progress.progress((idx + 1) / n)
                    continue

                status.markdown(f'<p class="status status-active">⟳ [{idx+1}/{n}] Extracting villa data via GPT-4o…</p>', unsafe_allow_html=True)
                try:
                    villa = extract_villa_data(oai, transcript)
                except Exception as e:
                    st.error(f"Extraction failed — {fname}: {e}")
                    progress.progress((idx + 1) / n)
                    continue

                villa["_transcript"] = transcript
                villa["_filename"] = fname
                all_results.append(villa)
                all_rows.append(flatten_to_csv_row(villa, fname))
                progress.progress((idx + 1) / n)

            status.markdown('<p class="status status-done">✓ All villas analysed successfully</p>', unsafe_allow_html=True)
            st.session_state["results"] = all_results
            st.session_state["csv_bytes"] = build_csv(all_rows)
            st.session_state["csv_rows"] = all_rows
            st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.get("results"):
    results = st.session_state["results"]
    csv_bytes = st.session_state["csv_bytes"]

    st.markdown("---")
    st.markdown("## Acquisition Results")

    scores = [r.get("stayvista_fit_score", 0) for r in results]
    avg = sum(scores) / len(scores) if scores else 0
    high = sum(1 for s in scores if s >= 70)
    buys = sum(1 for r in results if "buy" in r.get("acquisition_recommendation","").lower())

    st.markdown(f"""
    <div class="metric-strip">
        <div class="metric-tile"><div class="metric-val gold">{len(results)}</div><div class="metric-lbl">Villas Analysed</div></div>
        <div class="metric-tile"><div class="metric-val {score_color(avg)}">{avg:.0f}</div><div class="metric-lbl">Avg Fit Score</div></div>
        <div class="metric-tile"><div class="metric-val green">{high}</div><div class="metric-lbl">High Fit ≥70</div></div>
        <div class="metric-tile"><div class="metric-val gold">{buys}</div><div class="metric-lbl">Buy / Strong Buy</div></div>
    </div>
    """, unsafe_allow_html=True)

    col_dl, _ = st.columns([1, 3])
    with col_dl:
        st.download_button(
            "⬇  Download CSV Report",
            data=csv_bytes,
            file_name=f"stayvista_acquisition_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

    st.markdown("---")

    PILL_MAP = {
        "swimming_pool": "🏊 Pool", "pool_heated": "🔥 Heated Pool",
        "jacuzzi": "♨️ Jacuzzi", "lawn_garden": "🌿 Lawn/Garden",
        "servant_quarters": "🏠 Servant Qtrs", "parking": "🚗 Parking",
        "generator_backup": "⚡ Generator", "cctv_security": "📹 CCTV",
        "home_theatre": "🎬 Home Theatre", "gym_fitness": "💪 Gym",
        "terrace_rooftop": "🌇 Terrace", "bar_lounge": "🍹 Bar/Lounge",
        "bonfire_area": "🔥 Bonfire", "pet_friendly": "🐾 Pet Friendly",
        "chef_cook_available": "👨‍🍳 Chef", "ac_rooms": "❄️ AC Rooms",
        "modular_kitchen": "🍳 Mod Kitchen", "outdoor_seating": "🪑 Outdoor Seating",
        "mountain_view": "⛰️ Mountain View", "sea_view": "🌊 Sea View",
        "forest_view": "🌲 Forest View",
    }

    for villa in results:
        score = villa.get("stayvista_fit_score", 0)
        name = villa.get("villa_name", "Unknown Villa")
        loc = villa.get("location", {})
        loc_str = ", ".join(filter(None, [loc.get("city"), loc.get("state")]))
        am = villa.get("amenities", {})
        prop = villa.get("property_details", {})
        acq = villa.get("acquisition", {})
        rec = villa.get("acquisition_recommendation", "")

        with st.expander(
            f"{rec_emoji(rec)}  {name}   ·   {loc_str or 'Location TBD'}   ·   Score {score}/100   ·   {rec}",
            expanded=True,
        ):
            left, right = st.columns([3, 2])

            with left:
                address = loc.get("full_address") or loc_str or "Address not captured"
                landmarks = ("🗺️ " + loc.get("nearby_landmarks")) if loc.get("nearby_landmarks") else ""
                dist = ("&nbsp;&nbsp;·&nbsp;&nbsp;" + loc.get("distance_from_city")) if loc.get("distance_from_city") else ""
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{name}</div>
                    <p style="color:var(--muted); font-size:0.82rem; margin-bottom:0.8rem">
                        📍 {address}<br>{landmarks}{dist}
                    </p>
                    <p style="color:#ccc; font-size:0.85rem; line-height:1.75">{villa.get('summary','—')}</p>
                </div>
                """, unsafe_allow_html=True)

                # Amenity pills
                st.markdown("**Amenities Detected**")
                pill_html = '<div class="pills">'
                found = False
                for key, label in PILL_MAP.items():
                    if am.get(key):
                        pill_html += f'<span class="pill">{label}</span>'
                        found = True
                for oa in am.get("other_amenities", []):
                    pill_html += f'<span class="pill">{oa}</span>'
                    found = True
                if not found:
                    pill_html += '<span class="pill pill-miss">No amenities captured</span>'
                pill_html += "</div>"
                st.markdown(pill_html, unsafe_allow_html=True)

                if villa.get("key_highlights"):
                    st.markdown("**Key Highlights**")
                    for h in villa["key_highlights"]:
                        st.markdown(f"<span style='color:var(--green)'>✦</span> <span style='font-size:0.83rem'>{h}</span>", unsafe_allow_html=True)

                if villa.get("concerns"):
                    st.markdown("**Concerns**")
                    for c in villa["concerns"]:
                        st.markdown(f"<span style='color:var(--red)'>⚠</span> <span style='font-size:0.83rem; color:#bbb'>{c}</span>", unsafe_allow_html=True)

            with right:
                sc = score_color(score)
                st.markdown(f"""
                <div class="card score-wrap">
                    <div class="score-label">StayVista Fit Score</div>
                    <div class="score-num {sc}">{score}<span class="score-denom">/100</span></div>
                    <div style="font-size:0.75rem; color:var(--muted); letter-spacing:0.1em; margin-top:0.3rem">{rec}</div>
                    <div class="score-rationale">{villa.get('stayvista_fit_rationale','')}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**Property Details**")
                spec_html = ""
                for k, v in [
                    ("Type", prop.get("property_type")),
                    ("Bedrooms", prop.get("bedrooms")),
                    ("Bathrooms", prop.get("bathrooms")),
                    ("Total Area", f"{prop.get('total_area_sqft'):,} sqft" if prop.get("total_area_sqft") else None),
                    ("Plot Area", f"{prop.get('plot_area_sqft'):,} sqft" if prop.get("plot_area_sqft") else None),
                    ("Floors", prop.get("floors")),
                    ("Year Built", prop.get("year_built")),
                ]:
                    if v:
                        spec_html += f'<div class="spec-row"><span class="spec-key">{k}</span><span class="spec-val">{v}</span></div>'
                st.markdown(spec_html or "<p style='color:var(--muted); font-size:0.82rem'>Not captured</p>", unsafe_allow_html=True)

                st.markdown("**Acquisition Details**")
                price = acq.get("asking_price_inr")
                acq_html = ""
                for k, v in [
                    ("Asking Price", f"₹{price:,.0f}" if price else None),
                    ("₹/sqft", f"₹{acq.get('price_per_sqft_inr'):,.0f}" if acq.get("price_per_sqft_inr") else None),
                    ("Negotiable", "Yes" if acq.get("price_negotiable") is True else ("No" if acq.get("price_negotiable") is False else None)),
                    ("Ownership", acq.get("ownership_type")),
                    ("Annual Revenue", f"₹{acq.get('annual_revenue_inr'):,.0f}" if acq.get("annual_revenue_inr") else None),
                    ("Caretaker", "Yes" if acq.get("caretaker_present") else None),
                    ("Operational", "Yes" if acq.get("currently_operational") else None),
                    ("Legal Issues", "⚠ Mentioned" if acq.get("legal_issues_mentioned") else None),
                    ("Renovation", "Needed" if acq.get("renovation_needed") else None),
                    ("Reno Estimate", f"₹{acq.get('renovation_estimate_inr'):,.0f}" if acq.get("renovation_estimate_inr") else None),
                    ("Contact", acq.get("contact_person")),
                    ("Phone", acq.get("contact_number")),
                ]:
                    if v:
                        acq_html += f'<div class="spec-row"><span class="spec-key">{k}</span><span class="spec-val">{v}</span></div>'
                st.markdown(acq_html or "<p style='color:var(--muted); font-size:0.82rem'>Not captured</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#333; font-size:0.72rem; margin-top:0.5rem'>Source: {villa.get('_filename','')}</p>", unsafe_allow_html=True)

            with st.expander("📝 Raw Whisper Transcript"):
                st.markdown(f'<div class="transcript-box">{villa.get("_transcript","No transcript available.")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.download_button(
            "⬇  Download Full Acquisition Report (CSV)",
            data=csv_bytes,
            file_name=f"stayvista_acquisition_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
        fc = len(st.session_state["csv_rows"][0]) if st.session_state.get("csv_rows") else 0
        st.caption(f"{len(results)} villa(s) · {fc} data fields per entry")

else:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">🏛️</div>
        <p>Upload villa audio recordings to begin</p>
        <small>
            Supports MP3 · WAV · M4A · OGG · FLAC<br>
            Multiple files processed in one batch
        </small>
    </div>
    """, unsafe_allow_html=True)
