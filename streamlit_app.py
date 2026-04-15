import streamlit as st
import requests
import openai
from pathlib import Path

# --- PAGE SETUP ---
st.set_page_config(page_title="AeroSpeak Decoder", page_icon="✈️")
st.title("✈️ AeroSpeak: METAR Voice Decoder")
st.markdown("Enter an ICAO code (e.g., **CYOO**, **CYYZ**) to hear the latest weather.")

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    voice_choice = st.selectbox("Select Voice", ["onyx", "alloy", "echo", "nova"])
    st.info("The 'Onyx' voice sounds most like a professional ATIS.")

# --- FUNCTIONS ---
def get_live_metar(station):
    url = f"https://aviationweather.gov/api/data/metar?ids={station}"
    try:
        response = requests.get(url)
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
        return None
    except:
        return None

def process_weather(station_id, client):
    raw_metar = get_live_metar(station_id)
    
    if not raw_metar:
        st.error(f"Could not find data for {station_id}. Check the code and try again.")
        return

    st.subheader("Raw Data")
    st.code(raw_metar)

    # 1. AI Decoding
    with st.spinner("Decoding weather..."):
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional aviation weather briefer. Decode the METAR into a natural-sounding script. Read altimeters as individual digits (e.g., 'two nine decimal eight two'). Replace codes with full words (e.g., 'OVC' as 'Overcast')."},
                {"role": "user", "content": f"Decode for voice readback: {raw_metar}"}
            ]
        )
        script = completion.choices[0].message.content
        st.subheader("Briefer Script")
        st.write(script)

    # 2. AI Voice Synthesis
    with st.spinner("Synthesizing voice..."):
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice=voice_choice,
            input=script
        )
        # Streamlit can play audio directly from bytes
        audio_bytes = audio_response.content
        st.audio(audio_bytes, format="audio/mp3")

# --- MAIN UI ---
icao_input = st.text_input("Airport ICAO Code", value="CYOO").upper()

if st.button("Get Voice Report"):
    if not api_key:
        st.warning("Please enter your OpenAI API key in the sidebar.")
    else:
        client = openai.OpenAI(api_key=api_key)
        process_weather(icao_input, client)