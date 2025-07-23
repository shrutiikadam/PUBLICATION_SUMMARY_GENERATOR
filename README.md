# Publication Summary Generator

This is an AI-powered tool that extracts, filters, and summarizes research publications from `.bib` files or raw text using OpenAI’s GPT models. Built for researchers and students to quickly generate concise summaries and metadata from academic content.

## Features

- Upload and parse `.bib` or raw publication files
- Filter publications by:
  - Author name
  - Year of publication
  - Keywords
- Generate concise summaries using GPT-3.5 / GPT-4
- View parsed publication details in a clean table format
- Download structured output for reports or documentation

## Tech Stack

| Layer       | Technology Used              |
|-------------|-------------------------------|
| Frontend    | React, Tailwind CSS           |
| Backend     | Python Flask                  |
| AI/ML       | OpenAI GPT-3.5 / GPT-4 (API)  |
| Parsing     | `bibtexparser`, Custom Filters|

## How It Works

1. Upload a `.bib` or plain text file containing research publications.
2. Filter by author, year, or keyword.
3. Automatically generate structured summaries using GPT models.
4. View the results in a table and download if needed.

## Example Use Case

Upload this `.bib` entry:
```bibtex
@article{smith2020ai,
  title={AI in Healthcare},
  author={Smith, John and Doe, Jane},
  journal={AI Journal},
  year={2020}
}

Title: AI in Healthcare
Authors: John Smith, Jane Doe
Year: 2020
Summary: This paper explores the integration of artificial intelligence in clinical diagnostics and decision-making.. 
