# 📚 Publication Summary Generator

**Publication Summary** is an AI-powered tool designed to extract, filter, and summarize research publications for individual authors or entire organizations. It supports `.bib` and `.xlsx` file uploads to parse publication metadata and utilizes advanced NLP models to generate clean and concise research summaries. 

This system is ideal for academic institutions, research organizations, or scholarly communities to manage and review author contributions efficiently.

---

## ✨ Key Features

- **Upload Support**: 
  - `.bib` files for individual authors.
  - `.xlsx` files containing publication metadata.
  
- **Author Filtering**: 
  - Search and filter by author name(s).
  - Filter publications by **year** or **author** in multi-author scenarios.

- **AI-Based Summarization**:
  - Uses a **T5-based model** for generating concise summaries of research papers.

- **Organization Management**:
  - Add authors to your organization.
  - Manage org-wise publication records with real-time filtering.

- **SerpAPI Integration**:
  - Fetches author profile data dynamically from Google Scholar.

- **Interactive UI**:
  - Built with **React**, provides a clean and intuitive interface.
  - Responsive across devices for easy access.

---

## Tech Stack

| Layer       | Technology                         |
|-------------|-------------------------------------|
| Frontend    | React, React Router, Tailwind CSS   |
| Backend     | Python ,Flask           |
| AI Model    | T5 Transformer (Hugging Face)       |
| Data Fetch  | SerpAPI (Google Scholar Profiles)   |
| File Parsing| BibTeX Parser, Pandas (for Excel)   |

---

## 🛠️ Set Up Instructions

### 2. Set Up Backend (Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Set Up Frontend (React)
```bash
cd frontend
npm install
npm start
```
## Now open your browser at:
http://localhost:3000
