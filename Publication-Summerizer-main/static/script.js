document.addEventListener('DOMContentLoaded', () => {
    const resultsDiv = document.getElementById('results');
    const filtersDiv = document.createElement('div');
    filtersDiv.id = 'filters';
    filtersDiv.style.marginBottom = '20px';
    resultsDiv.before(filtersDiv); // Insert filters above results

    const authorSections = {};
    const uniqueAuthors = new Set();
    const eventSource = new EventSource(`/stream?filename=${filename}`);

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'author_start') {
            const authorName = data.name;
            uniqueAuthors.add(authorName);

            // If first time this author is seen, create section
            if (!authorSections[authorName]) {
                const authorWrapper = document.createElement('div');
                authorWrapper.className = 'author-section';
                authorWrapper.dataset.author = authorName;

                const authorHeader = document.createElement('h3');
                authorHeader.textContent = `📚 Author: ${authorName}`;
                authorWrapper.appendChild(authorHeader);
                resultsDiv.appendChild(authorWrapper);

                authorSections[authorName] = authorWrapper;
            }

            // Refresh filters at the top
            renderAuthorFilterButtons();
        }

        if (data.type === 'publication') {
            const pubDiv = document.createElement('div');
            pubDiv.className = 'publication';
            pubDiv.dataset.author = data.author;

            pubDiv.style.border = '1px solid #ccc';
            pubDiv.style.padding = '10px';
            pubDiv.style.marginBottom = '10px';
            pubDiv.style.borderRadius = '8px';
            pubDiv.style.backgroundColor = '#f9f9f9';

            pubDiv.innerHTML = `
                <strong>${data.index}. ${data.title}</strong><br>
                <em>${data.authors}</em><br>
                <strong>Citations:</strong> ${data.citations}<br>
                <strong>Publisher:</strong> ${data.publisher}<br>
                <strong>Abstract:</strong> ${data.abstract}<br>
            `;

            if (authorSections[data.author]) {
                authorSections[data.author].appendChild(pubDiv);
            } else {
                resultsDiv.appendChild(pubDiv); // fallback
            }
        }

        if (data.type === 'error') {
            const errorDiv = document.createElement('div');
            errorDiv.innerHTML = `<p style="color:red;">⚠️ ${data.name}: ${data.message}</p>`;
            resultsDiv.appendChild(errorDiv);
        }
    };

    eventSource.onerror = () => {
        resultsDiv.innerHTML += "<p style='color:green;'>Data fetched.</p>";
        eventSource.close();
    };

    function renderAuthorFilterButtons() {
        filtersDiv.innerHTML = '';

        uniqueAuthors.forEach(author => {
            const btn = document.createElement('button');
            btn.textContent = author;
            btn.dataset.author = author;
            btn.className = 'filter-button';
            btn.style.marginRight = '10px';
            filtersDiv.appendChild(btn);
        });

        // Add Show All button
        const showAllBtn = document.createElement('button');
        showAllBtn.textContent = 'Show All';
        showAllBtn.id = 'show-all-btn';
        showAllBtn.style.marginLeft = '20px';
        filtersDiv.appendChild(showAllBtn);
    }

    // Filter logic
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('filter-button')) {
            const selectedAuthor = e.target.dataset.author;

            document.querySelectorAll('.author-section').forEach(section => {
                if (section.dataset.author === selectedAuthor) {
                    section.style.display = 'block';
                } else {
                    section.style.display = 'none';
                }
            });
        }

        if (e.target.id === 'show-all-btn') {
            document.querySelectorAll('.author-section').forEach(section => {
                section.style.display = 'block';
            });
        }
    });
});

