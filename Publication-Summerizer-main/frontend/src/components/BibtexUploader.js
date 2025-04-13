import React, { useState } from "react";


const BibtexUploader = ({ authors = [], facultyPublications = {} }) => {
  const [selectedAuthor, setSelectedAuthor] = useState("");
  const [startYear, setStartYear] = useState("");
  const [endYear, setEndYear] = useState("");
  const [searchText, setSearchText] = useState("");
  const [bibtexEntries, setBibtexEntries] = useState([]);

  const handleFileUpload = async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("fileUpload");
    const file = fileInput.files[0];
    if (!file) return alert("Please select a file.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setBibtexEntries(data.entries || []);
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  const handleAuthorSearch = async (e) => {
    e.preventDefault();
    const form = e.target;
    const author = form.author.value;

    try {
      const response = await fetch("http://localhost:5000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ author }),
      });

      const data = await response.json();
      setBibtexEntries(data.entries || []);
    } catch (error) {
      console.error("Search failed:", error);
    }
  };

  const filterByAuthor = (author) => {
    setSelectedAuthor(author.toLowerCase());
  };

  const matchesFilter = (entry) => {
    const yearMatch =
      (!startYear || parseInt(entry.year) >= parseInt(startYear)) &&
      (!endYear || parseInt(entry.year) <= parseInt(endYear));
    const authorMatch =
      !selectedAuthor || (entry.author && entry.author.toLowerCase().includes(selectedAuthor));
    const searchMatch =
      !searchText || (entry.title && entry.title.toLowerCase().includes(searchText.toLowerCase()));
    return yearMatch && authorMatch && searchMatch;
  };

  return (
    <div style={{ display: "flex" }}>
      <div className="sidebar">
        {/* Upload File */}
        <form onSubmit={handleFileUpload}>
          <label htmlFor="fileUpload">Upload BibTeX File:</label>
          <input type="file" id="fileUpload" name="file" accept=".bib" required />
          <button type="submit">Upload BibTeX File</button>
        </form>

        {/* Author Search */}
        <form onSubmit={handleAuthorSearch}>
          <label htmlFor="author">Search Publications by Author Name:</label>
          <input type="text" name="author" placeholder="Enter author name" />
          <button type="submit">Search</button>
        </form>

        {/* Filters */}
        {authors.length > 0 && (
          <>
            <h3>Filter by Author</h3>
            <select onChange={(e) => filterByAuthor(e.target.value)}>
              <option value="">-- Select an Author --</option>
              {authors.map((author, index) => (
                <option key={index} value={author}>{author}</option>
              ))}
            </select>
          </>
        )}

        <label htmlFor="startYear">Filter by Year Range:</label>
        <input
          type="number"
          id="startYear"
          placeholder="Start Year"
          value={startYear}
          onChange={(e) => setStartYear(e.target.value)}
        />
        <input
          type="number"
          id="endYear"
          placeholder="End Year"
          value={endYear}
          onChange={(e) => setEndYear(e.target.value)}
        />
      </div>

      <div className="main-content">
        <h1>Publication Data Search</h1>

        {/* Dynamic Search */}
        <div className="dynamic-search">
          <input
            type="text"
            placeholder="Search within results..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        </div>

        {/* Display Uploaded or Searched Entries */}
        {bibtexEntries.length > 0 && (
          <div className="publication-list">
            <h2>Parsed BibTeX Entries</h2>
            <div className="publication-list-container">
              <ol>
                {bibtexEntries.filter(matchesFilter).map((entry, index) => (
                  <li key={index}>
                    <span id="title">{entry.title}</span>
                    <span id="authors"> by {entry.author}</span> ({entry.year})
                  </li>
                ))}
              </ol>
            </div>
          </div>
        )}

        {/* Faculty Publications */}
        {Object.keys(facultyPublications).length > 0 && (
          <div className="publication-list">
            <h2>Additional Publications Found</h2>
            {Object.entries(facultyPublications).map(([faculty, publications], idx) => (
              <div key={idx}>
                <h3>{faculty}</h3>
                <div className="publication-list-container">
                  <ol>
                    {publications.map((pub, pubIdx) => (
                      <li key={pubIdx}>
                        <div id="name-author">
                          <span id="title">{pub.Title}</span>
                          <span id="authors"> by {pub.Authors}</span>
                        </div>
                        Year: {pub.Year} <br />
                        Type: {pub.Type} <br />
                        {pub.Link === "No Link" ? (
                          <span className="no-link">{pub.Link}</span>
                        ) : (
                          <>
                            Link: <a href={pub.Link} target="_blank" rel="noopener noreferrer">{pub.Link}</a>
                          </>
                        )}
                      </li>
                    ))}
                  </ol>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BibtexUploader;
