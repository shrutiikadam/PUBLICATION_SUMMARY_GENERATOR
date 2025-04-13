import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState();
  const [data, setData] = useState();
  const [selectedAuthor, setSelectedAuthor] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData,
    });
    const result = await response.json();
    setData(result);
    setSelectedAuthor(null); // Reset selected author after new upload
  };

  const handleAuthorClick = (author) => {
    setSelectedAuthor(author);
  };

  const handleShowAll = () => {
    setSelectedAuthor(null);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>📄 Publication Summarizer</h1>

      <input type="file" accept=".xlsx" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload & Fetch</button>

      {data && (
        <div style={{ marginTop: '20px' }}>
          <h2>Authors</h2>
          <button
            onClick={handleShowAll}
            style={{
              margin: '5px',
              padding: '8px 12px',
              borderRadius: '6px',
              border: '1px solid #333',
              background: selectedAuthor === null ? '#333' : '#f0f0f0',
              color: selectedAuthor === null ? '#fff' : '#000',
              cursor: 'pointer',
            }}
          >
            Show All
          </button>

          {Object.keys(data).map((author) => (
            <button
              key={author}
              onClick={() => handleAuthorClick(author)}
              style={{
                margin: '5px',
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #333',
                background: selectedAuthor === author ? '#333' : '#f0f0f0',
                color: selectedAuthor === author ? '#fff' : '#000',
                cursor: 'pointer',
              }}
            >
              {author}
            </button>
          ))}

          <hr />

          <div>
            {selectedAuthor ? (
              <div>
                <h2>Publications by {selectedAuthor}</h2>
                {data[selectedAuthor].length === 0 ? (
                  <p>No publications found.</p>
                ) : (
                  data[selectedAuthor].map((pub, idx) => (
                    <div key={idx} style={{ marginBottom: '20px' }}>
                      <h4>{pub.title}</h4>
                      <p><strong>Authors:</strong> {pub.authors}</p>
                      <p><strong>Year:</strong> {pub.publication_year}</p>
                      <p><strong>Venue:</strong> {pub.venue}</p>
                      <p>{pub.abstract}</p>
                      <hr />
                    </div>
                  ))
                )}
              </div>
            ) : (
              <div>
                <h2>All Publications</h2>
                {Object.keys(data).map((author) =>
                  data[author].map((pub, idx) => (
                    <div key={`${author}-${idx}`} style={{ marginBottom: '20px' }}>
                      <h4>{pub.title}</h4>
                      <p><strong>Authors:</strong> {pub.authors}</p>
                      <p><strong>Year:</strong> {pub.publication_year}</p>
                      <p><strong>Venue:</strong> {pub.venue}</p>
                      <p>{pub.abstract}</p>
                      <p><em>({author})</em></p>
                      <hr />
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;