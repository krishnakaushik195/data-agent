# 📡 dataagent

**Automated High-Quality Training Data Extraction**

---

## 🚀 Tagline  
Automated High-Quality Training Data Extraction

---

## 🧠 About the project

### Inspiration  
As I work on my startup **Quark** — focused on small, domain-specific models — I realized that **high-quality supervised training data** is the most critical yet tedious part of the process. Collecting, curating, and annotating technical datasets across various niches takes **significant time and effort**.

### What it does  
`dataagent` is a prototype tool that:
- Uses an LLM (Gemini) to intelligently find scrape-ready links  
- Scrapes technical content from the web  
- Cleans and merges content  
- Generates annotated training data (input-output pairs)  
- Outputs the data in CSV/JSON formats for easy fine-tuning

### How we built it  
- Frontend with **Streamlit** for fast prototyping and UI  
- **Google Gemini API** used to:
  - Suggest scrape-worthy URLs for a topic  
  - Convert unstructured text into labeled data  
- **Requests** and **BeautifulSoup** for scraping and parsing HTML  
- Raw text is chunked, processed, and saved in clean formats for future fine-tuning pipelines

### Challenges we ran into  
- Gemini occasionally returns unexpected or malformed JSON, requiring fallback/debug handling  
- Some web pages are heavily JS-based or blocked scraping  
- Maintaining prompt consistency across chunks for high-quality annotation

### Accomplishments that we're proud of  
- Built an **end-to-end data pipeline** in a short time  
- Made data collection manageable and reproducible for niche AI use cases  
- Created a solid prototype that can scale with more features

### What we learned  
- Prompt engineering plays a **huge role** in annotation quality  
- Even lightweight scraping pipelines need good error handling  
- Iterative evaluation is key when working with LLMs for structured output

### What's next for dataagent  
- Add support for PDF and code repo parsing  
- Improve Gemini prompts for broader annotation styles (e.g., classification, summarization)  
- Auto-tag domains or topics in outputs  
- Connect to vector DBs for downstream RAG/LLM pipelines

---

## ❗Note  
I couldn't integrate some sponsor tools due to time constraints, but I hope that’s understandable. The project still uses **LLMs effectively** and serves the core goal well.

---

## 🛠️ Built With

- Python  
- Streamlit  
- BeautifulSoup  
- Requests  
- Google Gemini API  
- CSV  
- JSON
