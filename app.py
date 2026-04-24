import streamlit as st
import whisper
import json
import csv
import io
import os
import tempfile
from groq import Groq

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StayVista Acquisition Tool",
    page_icon="🏡",
    layout="wide"
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🏡 StayVista Property Acquisition Tool")
st.caption("Upload a property walkthrough video → get a structured summary + CSV instantly")
st.divider()

# ── Sidebar: API key ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Free at console.groq.com"
    )
    st.markdown("[Get free Groq API key →](https://console.groq.com)")
    st.divider()
    st.markdown("**Supported formats**")
    st.markdown("MP4, MOV, MKV, AVI, M4A, MP3, WAV")
    st.markdown("**Supported languages**")
    st.markdown("Hindi, English, Hinglish — auto-detected")

# ── Whisper loader (cached so it loads only once) ──────────────────────────────
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a real estate data extraction assistant for StayVista,
a luxury villa rental platform. Given a transcription of a property walkthrough video,
return a JSON object with EXACTLY these two keys:

1. "summary": Write a clean, structured property summary using ONLY the sections below.
   Include a section ONLY if it was mentioned in the transcription — skip it entirely if not.
   Do not add assumptions or generic filler. Every line must come from the transcription.

   Format the summary exactly like this (use only relevant sections):

   PROPERTY OVERVIEW
   [Property name, type, location, gated community or not, age/condition if mentioned]

   ROOMS & LAYOUT
   [Total rooms, bedrooms, bathrooms, floors, special rooms like pooja/study/theatre]

   AMENITIES & FEATURES
   [Pools (count + type), jacuzzi, gym, spa, garden, terrace, BBQ, bonfire area, etc.]

   KITCHEN & INTERIORS
   [Kitchen type, furnishing status, AC, interiors highlights]

   OUTDOOR & VIEWS
   [View type, plot area, garden size, outdoor features]

   SERVICES & SECURITY
   [Parking, caretaker, security staff, CCTV, WiFi, generator, EV charging]

   APPROVALS & LEGAL
   [RERA approval, RERA number, any other approvals]

   PRICING
   [Monthly rent, nightly rate, security deposit, minimum stay]

   POC NOTES
   [Any additional observations from the field agent]

2. "csv_data": A flat dict with ALL these keys (use null only if genuinely not mentioned):
   property_name, location, city, state, is_gated_community, community_name,
   nearby_landmarks, property_type, total_rooms, bedrooms, bathrooms, total_floors,
   area_sqft, plot_area_sqft, furnishing_status, age_of_property_years,
   is_rera_approved, rera_number, other_approvals,
   has_swimming_pool, number_of_swimming_pools, pool_type, has_jacuzzi,
   number_of_jacuzzis, has_private_pool, has_gym, has_spa, has_sauna,
   has_game_room, has_home_theatre, has_kids_play_area, has_garden,
   garden_area_sqft, has_terrace, has_balcony, has_barbeque_area,
   has_bonfire_area, view_type, kitchen_type, has_dining_area, has_living_room,
   has_study_room, has_pooja_room, has_parking, parking_capacity, has_caretaker,
   has_security_staff, has_cctv, has_wifi, has_ac, has_generator_backup,
   has_ev_charging, monthly_rent_inr, nightly_rate_inr, security_deposit_inr,
   minimum_stay_nights, special_features, condition_of_property, acquisition_poc_notes

Return ONLY valid JSON. No markdown. Never invent details."""

# ── Main app ───────────────────────────────────────────────────────────────────
if not groq_api_key:
    st.info("👈 Enter your Groq API key in the sidebar to get started.")
    st.stop()

uploaded_file = st.file_uploader(
    "Upload property walkthrough video or audio",
    type=["mp4", "mov", "mkv", "avi", "m4a", "mp3", "wav"]
)

if uploaded_file:
    st.video(uploaded_file) if uploaded_file.name.endswith(
        ("mp4", "mov", "mkv", "avi")) else st.audio(uploaded_file)

    if st.button("🚀 Process Property", type="primary", use_container_width=True):

        # Save uploaded file to temp path
        suffix = os.path.splitext(uploaded_file.name)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            # ── Step 1: Transcribe ─────────────────────────────────────────────
            with st.status("🎙️ Transcribing audio...", expanded=True) as status:
                st.write("Loading Whisper model...")
                model = load_whisper()
                st.write("Transcribing and translating to English...")
                result = model.transcribe(tmp_path, task="translate", language=None)
                transcription = result["text"]
                detected_lang = result.get("language", "unknown")
                status.update(label=f"✅ Transcription done  (detected: {detected_lang})",
                              state="complete")

            with st.expander("📄 View raw transcription"):
                st.write(transcription)

            # ── Step 2: AI Analysis ────────────────────────────────────────────
            with st.status("🤖 Analysing with Llama 3...", expanded=True) as status:
                st.write("Extracting property details...")
                client = Groq(api_key=groq_api_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Transcription:\n\n{transcription}"}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                raw = response.choices[0].message.content
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                    data = json.loads(clean)
                status.update(label="✅ Analysis complete", state="complete")

            summary  = data["summary"]
            csv_data = data["csv_data"]

            # ── Step 3: Display results ────────────────────────────────────────
            st.divider()
            col1, col2 = st.columns(2, gap="large")

            with col1:
                st.subheader("📋 Property Summary")
                # Render each section as a neat block
                for line in summary.strip().split("\n"):
                    if line.strip().isupper() and len(line.strip()) > 2:
                        st.markdown(f"**{line.strip()}**")
                    elif line.strip():
                        st.markdown(line)

            with col2:
                st.subheader("📊 Extracted Data")
                found = {k: v for k, v in csv_data.items() if v is not None}
                st.caption(f"{len(found)} of {len(csv_data)} fields captured")

                # Group display
                groups = {
                    "📍 Location": ["property_name","location","city","state",
                                    "is_gated_community","community_name","nearby_landmarks"],
                    "🏠 Property": ["property_type","total_rooms","bedrooms","bathrooms",
                                    "total_floors","area_sqft","plot_area_sqft",
                                    "furnishing_status","age_of_property_years","condition_of_property"],
                    "✅ Approvals": ["is_rera_approved","rera_number","other_approvals"],
                    "🏊 Amenities": ["has_swimming_pool","number_of_swimming_pools","pool_type",
                                     "has_jacuzzi","number_of_jacuzzis","has_private_pool",
                                     "has_gym","has_spa","has_sauna","has_game_room",
                                     "has_home_theatre","has_kids_play_area","has_garden",
                                     "garden_area_sqft","has_terrace","has_balcony",
                                     "has_barbeque_area","has_bonfire_area","view_type"],
                    "🛋️ Interiors": ["kitchen_type","has_dining_area","has_living_room",
                                     "has_study_room","has_pooja_room"],
                    "🔒 Services":  ["has_parking","parking_capacity","has_caretaker",
                                     "has_security_staff","has_cctv","has_wifi","has_ac",
                                     "has_generator_backup","has_ev_charging"],
                    "💰 Pricing":  ["monthly_rent_inr","nightly_rate_inr",
                                    "security_deposit_inr","minimum_stay_nights"],
                    "📝 Notes":    ["special_features","acquisition_poc_notes"],
                }
                for group_name, keys in groups.items():
                    group_data = {k: csv_data[k] for k in keys
                                  if k in csv_data and csv_data[k] is not None}
                    if group_data:
                        with st.expander(group_name, expanded=True):
                            for k, v in group_data.items():
                                label = k.replace("_", " ").title()
                                st.markdown(f"**{label}:** {v}")

            # ── Step 4: Downloads ──────────────────────────────────────────────
            st.divider()
            st.subheader("⬇️ Download Outputs")
            dl1, dl2 = st.columns(2)

            with dl1:
                st.download_button(
                    label="📄 Download Summary (.txt)",
                    data=summary,
                    file_name=f"{csv_data.get('property_name','property').replace(' ','_')}_summary.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with dl2:
                csv_buffer = io.StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=csv_data.keys())
                writer.writeheader()
                writer.writerow(csv_data)
                st.download_button(
                    label="📊 Download Data (.csv)",
                    data=csv_buffer.getvalue(),
                    file_name=f"{csv_data.get('property_name','property').replace(' ','_')}_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        finally:
            os.unlink(tmp_path)  # clean up temp file
