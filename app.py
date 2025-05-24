import time
import requests
import json
import csv
import io
from bs4 import BeautifulSoup
import streamlit as st
from google import genai
from google.genai import types

# Streamlit UI
st.title("🔎 Gemini-based Training Data Collector")

# User input
topic = st.text_input("Enter topic of interest:", "google i/o 2025")
submit = st.button("Start Scraping and Generate Data")

if submit:
    # Gemini client init
    client = genai.Client(api_key="AIzaSyDchUVEvIC5QQT8KWbA6CFjBAmbrbUcvqg")
    model_id = "gemini-2.0-flash"

    # Google Search Tool
    google_search_tool = types.Tool(google_search=types.GoogleSearch())

    prompt = f"""
    I want to collect data for training a language model about the topic: "{topic}".

    Return ONLY high-quality, direct links that are suitable for scraping. 
    Each link should:
    - Be directly accessible (no redirects or shortened URLs).
    - Contain rich technical data: documentation, code, or detailed tutorials.
    - Be scrape-friendly (avoid heavily JavaScript-based or anti-scraping protected sites).

    ⚠️ IMPORTANT:
    - Do NOT include any descriptions, titles, or explanations.
    - Output should ONLY be clean, full URLs.
    - Each URL should be on a separate line.
    - Return exactly 3 links.
    """

    # Call Gemini to get links
    with st.spinner("📡 Getting scraping-ready URLs from Gemini..."):
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )

        pure_links = "".join(part.text for part in response.candidates[0].content.parts)
        url_list = [url.strip() for url in pure_links.strip().splitlines() if url.strip()]

    st.subheader("🔗 Scraping-Ready Links:")
    for link in url_list:
        st.write(link)

    # Scraping function
    def scrape_and_merge(urls):
        merged_content = ""
        for idx, url in enumerate(urls):
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url, headers=headers, timeout=10)
                res.raise_for_status()
                soup = BeautifulSoup(res.text, "html.parser")
                text = soup.get_text(separator="\n")
                cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
                merged_content += f"\n--- Content from: {url} ---\n{cleaned_text}\n"
            except Exception as e:
                st.warning(f"⚠️ Failed to scrape {url}: {e}")
        return merged_content.strip()

    with st.spinner("🌐 Scraping URLs and merging content..."):
        merged_text = scrape_and_merge(url_list)
    st.success(f"✅ Merged content ready in memory.")

    # Text chunking function
    def chunk_text(text, max_chars=3000):
        chunks = []
        start = 0
        while start < len(text):
            end = start + max_chars
            if end < len(text):
                split_pos = text.rfind('\n', start, end)
                if split_pos == -1:
                    split_pos = text.rfind('. ', start, end)
                if split_pos == -1 or split_pos <= start:
                    split_pos = end
                end = split_pos
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end
        return chunks

    def make_gemini_prompt(chunk_text):
        return f"""
You are an expert data annotator preparing training data for a language model.
Convert the following raw scraped text into a JSON array of high-quality supervised examples.
Each example should be a JSON object with two keys: "input" and "output".
- "input": a question or prompt about the data,
- "output": the correct answer or explanation.

⚠️ Return ONLY a valid JSON array. No extra text or explanation.

Raw scraped text:
\"\"\"{chunk_text}\"\"\"
"""

    def convert_raw_to_json(client, model_id, raw_text):
        chunks = chunk_text(raw_text, max_chars=3000)
        all_json = []
        for i, chunk in enumerate(chunks):
            with st.spinner(f"🧠 Processing chunk {i+1}/{len(chunks)}..."):
                prompt = make_gemini_prompt(chunk)
                K_response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                raw_output = "".join(part.text for part in K_response.candidates[0].content.parts).strip()
                cleaned_data = raw_output.replace("```json", "").replace("```", "").strip()

                try:
                    json_data = json.loads(cleaned_data)
                    all_json.extend(json_data)
                except json.JSONDecodeError as e:
                    st.warning(f"⚠️ JSON decode error on chunk {i+1}: {e}")
                    st.code(cleaned_data[:1000], language='json')
        return all_json

    st.info("🚀 Generating training data with Gemini...")
    training_data = convert_raw_to_json(client, model_id, merged_text)

    if not training_data:
        st.warning("⚠️ No training data generated.")
    else:
        st.success(f"✅ Total training examples generated: {len(training_data)}")

        # Show preview (first 3 examples)
        st.subheader("📋 Sample Training Data (first 3 examples):")
        for example in training_data[:3]:
            st.markdown(f"**Input:** {example.get('input', '')}")
            st.markdown(f"**Output:** {example.get('output', '')}")
            st.markdown("---")

        # Convert to CSV (in-memory)
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["input", "output"])
        for entry in training_data:
            input_text = entry.get("input", "").replace('\n', ' ').strip()
            output_text = entry.get("output", "").replace('\n', ' ').strip()
            writer.writerow([input_text, output_text])
        csv_data = csv_buffer.getvalue()
        st.success("📦 Training data is ready in memory.")

        # Download buttons
        st.download_button(
            label="📥 Download Merged Text Data",
            data=merged_text,
            file_name=f"{topic.replace(' ', '_')}_merged_data.txt",
            mime="text/plain"
        )

        st.download_button(
            label="📥 Download Training Data CSV",
            data=csv_data,
            file_name=f"{topic.replace(' ', '_')}_training_data.csv",
            mime="text/csv"
        )
