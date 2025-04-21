import os
from flask import Flask, render_template, request, jsonify ,redirect, url_for,Response, stream_with_context
import openpyxl
from habanero import Crossref
import bibtexparser
import requests
from bs4 import BeautifulSoup
import time
import json
from pybtex.database import parse_string
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from scholarly import scholarly
import pandas as pd
app = Flask(__name__)

api_key = '54d27e4262c11dcd791af7df6a496401e6528d4513419932764a1b84cf0680f6'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Persistent storage for results
original_publications = {}
filtered_publications = {}
filters = {"year_from": None, "year_to": None, "type": None}


def find_exact_author(name, email_domain=None):
    search_query = scholarly.search_author(name)
    name_lower = name.strip().lower()
    email_domain = email_domain.strip().lower() if email_domain else None

    for author in search_query:
        author_name = author.get('name', '').strip().lower()
        author_email = author.get('email_domain', '').strip().lower()
        if author_name == name_lower and (not email_domain or email_domain in author_email):
            return scholarly.fill(author)
    return None

# Stream publication data for multiple authors
def stream_publications_from_excel(filepath):
    df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
    for index, row in df.iterrows():
        name = str(row.get('name')).strip()
        email_domain = str(row.get('email_domain')).strip()
        yield f"data: {json.dumps({'type': 'author_start', 'name': name})}\n\n"

        try:
            author = find_exact_author(name, email_domain)
            if not author:
                yield f"data: {json.dumps({'type': 'error', 'name': name, 'message': 'Author not found'})}\n\n"
                continue
                # working -------------------------->
            for idx, pub in enumerate(author['publications'], 1):
                try:
                    pub_filled = scholarly.fill(pub)
                    bib = pub_filled.get('bib', {})

                    abstract = bib.get("abstract", "")
                    summary = summarize_text(abstract) if abstract else "No abstract available"

                    publication_data = {
                        "type": "publication",
                        "index": idx,
                        "author": name,
                        "title": bib.get("title", "No Title"),
                        "authors": bib.get("author", "Unknown"),
                        "citations": pub_filled.get("num_citations", 0),
                        "abstract": summary,  # ✅ Summarized abstract!
                        "venue": bib.get("venue", "Unknown Venue"),
                        "year": bib.get("year", "Unknown Year"),
                        "publisher": bib.get("publisher", "Unknown Publisher")
                    }

                    yield f"data: {json.dumps(publication_data)}\n\n"
                    time.sleep(0.5)
                except Exception as pub_err:
                    print(f"⚠️ Error processing publication {idx} for {name}: {pub_err}")
                    continue

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'name': name, 'message': str(e)})}\n\n"

@app.route('/excel', methods=['GET', 'POST'])
def excel():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file and uploaded_file.filename.endswith(('.xlsx', '.csv')):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(filepath)
            return render_template('loading.html', filename=uploaded_file.filename)
        else:
            return render_template('excel.html', error="Please upload a valid .xlsx or .csv file with 'name' and 'email_domain'.")
    return render_template('excel.html')

@app.route('/stream')
def stream():
    filename = request.args.get('filename')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return Response(stream_with_context(stream_publications_from_excel(filepath)), mimetype='text/event-stream')


# Load once (outside the route)
model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

def summarize_text(text):
    inputs = tokenizer(text, max_length=512, return_tensors="pt", truncation=True)
    summary_ids = model.generate(
        inputs["input_ids"], 
        num_beams=5,
        max_length=100,
        min_length=50,
        length_penalty=2.0,
        early_stopping=True,
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

@app.route('/summarize', methods=['POST'])
def summarize_route():
    data = request.get_json()
    text = data.get("text", "")
    summary = summarize_text(text)
    return jsonify({"summary": summary})

# Function to fetch publications from CrossRef
def fetch_crossref_papers(author):
    cr = Crossref()
    try:
        works = cr.works(query=author, limit=5)
        paper_details = []

        for item in works.get("message", {}).get("items", []):
            title = item.get("title", ["N/A"])[0]
            paper_type = item.get("type", "N/A")
            year = (
                item.get("published-print", {}).get("date-parts", [[None]])[0][0]
                or item.get("published-online", {}).get("date-parts", [[None]])[0][0]
            )
            authors = ", ".join(
                f"{auth.get('given', '')} {auth.get('family', '')}".strip()
                for auth in item.get("author", [])
            )
            abstract = item.get("abstract", "N/A")

            # Clean abstract (sometimes includes tags like <jats:p>…</jats:p>)
            if abstract != "N/A":
                abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", "").strip()

            # Generate summary if abstract is present
            summary = "N/A"
            if abstract != "N/A" and len(abstract.split()) > 5:
                try:
                    summary = summarize_text(abstract)
                except Exception as e:
                    summary = f"Error summarizing: {e}"

            paper_details.append({
                "title": title,
                "type": paper_type,
                "year": year,
                "authors": authors,
                "abstract": abstract,
                "summary": summary
            })

        return sorted(paper_details, key=lambda x: x.get("year", float("-inf")) or float("-inf"), reverse=True)

    except Exception as e:
        return [{"error": str(e)}]

def get_publications_from_crossref(author_name):
    url = f"https://api.crossref.org/works?query.author={author_name}&rows=5"
    response = requests.get(url)
    data = response.json()

    publications = []
    for item in data['message']['items']:
        authors_list = item.get('author', [])
        authors_str = ', '.join([
            (a.get('given', '') + " " + a.get('family', '')) if 'given' in a and 'family' in a 
            else a.get('name', 'Unknown Author')
            for a in authors_list
        ])

        publications.append({
            'title': item.get('title', ['No Title'])[0],
            'authors': authors_str,
            'publication_year': item.get('issued', {}).get('date-parts', [[None]])[0][0],
            'venue': item.get('container-title', [''])[0],
            'abstract': item.get('abstract', 'Abstract not available.')
        })
    
    return publications

#working good 
def apply_filters(publications, filters):
    year_from = filters["year_from"]
    year_to = filters["year_to"]
    paper_type = filters["type"]

    filtered = {}
    for author, papers in publications.items():
        filtered_papers = [
            paper
            for paper in papers
            if (year_from is None or (paper["year"] and paper["year"] >= year_from))
            and (year_to is None or (paper["year"] and paper["year"] <= year_to))
            and (not paper_type or paper["type"].lower() == paper_type.lower())
        ]
        if filtered_papers:
            filtered[author] = filtered_papers

    return filtered
from urllib.parse import unquote

@app.route('/author/<author>')
def get_author_papers(author):
    author = unquote(author)
    author_papers = filtered_publications.get(author, [])
    return jsonify(author_papers)


def fetch_author_url(name):
    # Replace spaces with '+' for URL encoding
    url = f'https://dblp.org/search/author/api?q={name.replace(" ", "+")}&format=json'
    response = requests.get(url)
    
    if response.status_code != 200:
        return None  # Handle API failure
    try:
        data = response.json()
        # Check if there are hits
        if data['result']['hits']['hit']:
            # Return the URL of the first author found
            return data['result']['hits']['hit'][0]['info']['url']
    except (KeyError, IndexError):
        return None  # Handle cases where the expected data structure doesn't exist
    return None



@app.route('/organization')
def organization():
    
    return render_template('organizations.html')

@app.route('/citations')
def author_citations():
    author_id = request.args.get('author_id', default='', type=str)
    #api_key = "9f8b218df1de1fe8a49c47baab5d710c45cb5dc3c5351226d36ca7c82744bdb5"
    url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id={author_id}&api_key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()  # Parse JSON response
        print(data)
        return jsonify(data)  # Return JSON response to the client
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500



@app.route('/fetch_authors')
def fetch_authors():
    #api_key = "9f8b218df1de1fe8a49c47baab5d710c45cb5dc3c5351226d36ca7c82744bdb5"  # Replace with your actual API key
    query = "Claudine_Badue"
    author = request.args.get('author', default='', type=str)
    url = f"https://serpapi.com/search.json?engine=google_scholar_profiles&hl=en&mauthors={author.replace('', '%20')}&api_key={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()  # Parse JSON response
        profiles = data.get("profiles", {})
        print(profiles)
        if not profiles:
            return jsonify({"error": "No authors found for the given name"}), 404

        # Extract the first author's ID
        author_id = profiles[0].get("author_id")
        if not author_id:
            return jsonify({"error": "Author ID not found in response"}), 500

        # Fetch citation data
        #citation_data = author_citations(author_id)
        return jsonify(profiles)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

def fetch_papers(author_url):
    response = requests.get(author_url)
    if response.status_code != 200:
        return []  # If the request fails, return an empty list
    
    soup = BeautifulSoup(response.text, 'html.parser')
    papers = []
    seen = set()  # Set to track unique papers by title or other criteria

    results = soup.find_all('li', class_='entry')

    for result in results:
        title_tag = result.find('span', class_='title')
        title = title_tag.text.strip() if title_tag else "No Title"
        
        # Check if the title is already seen
        if title in seen:
            continue  # Skip duplicate entries
        seen.add(title)

        author_tags = result.find_all('span', itemprop='author')
        authors = [author.text.strip() for author in author_tags]
        formatted_authors = ', '.join(authors) if authors else "No Author Info"
        
        snippet_tag = result.find('span', class_='abstract')
        snippet = snippet_tag.text.strip() if snippet_tag else "No Abstract"
        snippet = snippet.replace("△ Less", "").strip()
        
        year_tag = result.find('span', itemprop='datePublished')
        year = year_tag.text.strip() if year_tag else "No Year"
        
        link_tag = result.find('div', class_='head').find('a')
        link = link_tag['href'] if link_tag else "No Link"
        
        type_ = result.find('img').get('title', 'No Type')

        papers.append({
            "Title": title,
            "Authors": formatted_authors,
            "Year": year,
            "Link": link,
            "Type": type_,
            "Description": snippet,
        })
    
    # Save papers to text.json
    with open('text.json', 'w', encoding='utf-8') as w:
        json.dump(papers, w, ensure_ascii=False, indent=4)
    
    return papers

@app.route('/bibtex')
def bibtex():
    return render_template('bibtex.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('bibtex'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('bibtex'))

    faculty_publications = {}
    authors_set = set()  # Use a set to ensure uniqueness of authors

    if file and file.filename.endswith('.bib'):
        bib_data = file.read().decode('utf-8')
        bib_database = bibtexparser.loads(bib_data)
        entries = bib_database.entries

        # Extract authors from BibTeX entries and store them in authors_set
        for entry in entries:
            faculty_name = entry.get('author')
            if faculty_name:
                # Split authors if multiple authors are present
                author_list = faculty_name.split(' and ')
                for author in author_list:
                    # Clean up and add to set
                    cleaned_author = author.strip()
                    if cleaned_author:
                        authors_set.add(cleaned_author)

        # Convert set to a list to pass to the template
        authors_list = list(authors_set)

        return render_template('bibtex.html', entries=entries, faculty_publications=faculty_publications, authors=authors_list)

    return redirect(url_for('bibtex'))

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    df = pd.read_excel(file)
    authors = df['Author Name'].tolist()

    all_publications = {}
    for author in authors:
        publications = get_publications_from_crossref(author)
        all_publications[author] = publications

    return jsonify(all_publications)

@app.route('/search', methods=['POST'])
def search():
    author_name = request.form.get('author')
    if not author_name:
        return redirect(url_for('bibtex'))
    
    start = time.time()
    
    # Fetch author URL and papers based on the author name
    author_url = fetch_author_url(author_name)
    
    if author_url:
        publications = fetch_papers(author_url)
    else:
        publications = []  # If no author URL is found, return an empty list

    end = time.time()
    print(f'Time taken: {end - start} seconds')
    
    return render_template('bibtex.html', faculty_publications={author_name: publications})


@app.route("/")
def landing():
    return render_template("landing.html") 

@app.route("/pricing")
def pricing():
    return render_template("pricing.html") 


if __name__ == '__main__':
    app.run(debug=True)
