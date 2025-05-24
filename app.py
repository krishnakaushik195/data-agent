import time
import requests
import json
import csv
import io
from bs4 import BeautifulSoup
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Gemini Trainer", layout="centered")
st.title("📘 Gemini Training Data Generator")

topic = st.text_input("Enter topic:", "agenthacks")
submit = st.button("Generate")

if submit:
    client = genai.Client(api_key="AIzaSyDchUVEvIC5QQT8KWbA6CFjBAmbrbUcvqg")
    model_id = "gemini-2.0-flash"
    google_search_tool = types.Tool(google_search=types.GoogleSearch())

    prompt = f"""
    Return 3 direct scrape-friendly URLs related to: "{topic}"
    - Output ONLY 3 full links, no text or explanation.
    - Each link on a new line.
    """

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

    def scrape_and_merge(urls):
        merged_content = ""
        for url in urls:
            try:
                res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                text = soup.get_text(separator="\n")
                cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
                merged_content += f"\n--- From: {url} ---\n{cleaned}\n"
            except:
                continue
        return merged_content.strip()

    def chunk_text(text, max_chars=3000):
        chunks = []
        start = 0
        while start < len(text):
            end = text.rfind("\n", start, start + max_chars)
            if end <= start: end = start + max_chars
            chunks.append(text[start:end].strip())
            start = end
        return chunks

    def make_prompt(chunk):
        return f"""
You are an annotator. Convert the following scraped text into a JSON array of examples.
Each example must be: {{"input": "...", "output": "..."}}.
Output JSON only.

\"\"\"{chunk}\"\"\"
"""

    def generate_examples(raw_text):
        data = []
        for chunk in chunk_text(raw_text):
            prompt = make_prompt(chunk)
            try:
                result = client.models.generate_content(model=model_id, contents=prompt)
                out = "".join(p.text for p in result.candidates[0].content.parts)
                out = out.replace("```json", "").replace("```", "").strip()
                examples = json.loads(out)
                data.extend(examples)
            except:
                continue
        return data

    merged = scrape_and_merge(url_list)
    examples = generate_examples(merged)

    if examples:
        # Show minimal preview
        st.subheader("🧪 Sample Training Example")
        st.table([examples[0]])

        # Downloads
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["input", "output"])
        for row in examples:
            writer.writerow([row.get("input", ""), row.get("output", "")])

        st.download_button("⬇ Download CSV", data=csv_buf.getvalue(),
                           file_name=f"{topic}_training_data.csv", mime="text/csv")

        st.download_button("⬇ Download Merged Text", data=merged,
                           file_name=f"{topic}_merged_text.txt", mime="text/plain")
