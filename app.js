document.addEventListener("DOMContentLoaded", () => {
    const newsContainer = document.getElementById('news-container');
    const regionFilter = document.getElementById('region-filter');
    const themeFilter = document.getElementById('theme-filter');
    const originFilter = document.getElementById('origin-filter');
    const searchInput = document.getElementById('search-input');
    const lastUpdatedEl = document.getElementById('last-updated');
    const noResultsMsg = document.getElementById('no-results-msg');
    
    // Carousel Elements
    const track = document.getElementById('carousel-track');
    const btnPrev = document.getElementById('carousel-prev');
    const btnNext = document.getElementById('carousel-next');
    const indicators = document.getElementById('carousel-indicators');

    let articles = [];
    let currentSlide = 0;
    let carouselItemsCount = 0;

    // Fetch News Data (added cache-busting just in case for live envs)
    fetch('news.json?t=' + new Date().getTime())
        .then(response => response.json())
        .then(data => {
            articles = data.articles;
            updateLastUpdated(data.last_updated);
            applyFilters();
        })
        .catch(err => console.error("Error loading news data:", err));

    // Fetch Bulletin/Highlights Data
    fetch('bulletin.json?t=' + new Date().getTime())
        .then(response => response.json())
        .then(data => {
            renderCarousel(data.highlights);
        })
        .catch(err => console.error("Error loading bulletin data:", err));

    // Event Listeners for Filters & Search
    regionFilter.addEventListener('change', applyFilters);
    themeFilter.addEventListener('change', applyFilters);
    originFilter.addEventListener('change', applyFilters);
    searchInput.addEventListener('input', applyFilters); // Real-time search

    function applyFilters() {
        const region = regionFilter.value;
        const theme = themeFilter.value;
        const origin = originFilter.value;
        const query = searchInput.value.toLowerCase().trim();

        const filtered = articles.filter(article => {
            const matchRegion = region === 'all' || article.region === region;
            const matchTheme = theme === 'all' || article.theme === theme;
            const matchOrigin = origin === 'all' || article.origin === origin;
            
            let matchSearch = true;
            if (query) {
                const titleStr = (article.title || "").toLowerCase();
                const sumStr = (article.summary || "").toLowerCase();
                matchSearch = titleStr.includes(query) || sumStr.includes(query);
            }
            
            return matchRegion && matchTheme && matchOrigin && matchSearch;
        });

        renderNews(filtered, query);
    }

    function renderNews(newsArray, query) {
        newsContainer.innerHTML = '';
        noResultsMsg.style.display = 'none';

        if (newsArray.length === 0) {
            noResultsMsg.style.display = 'block';
            if (query) {
                noResultsMsg.innerHTML = `<p>Nenhuma notícia encontrada para "<strong>${query}</strong>" com os filtros selecionados.</p>`;
            } else {
                noResultsMsg.innerHTML = `<p>Nenhuma notícia encontrada com os filtros selecionados.</p>`;
            }
            return;
        }

        // Render up to 50 items
        newsArray.slice(0, 50).forEach(article => {
            const dateStr = new Date(article.published_at).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
            
            const card = document.createElement('article');
            card.className = 'card';
            
            // Image tag with loading="lazy", referrerpolicy, and onerror fallback
            const fallbackHTML = `<div class="card-img-placeholder">${article.source}</div>`;
            const imageHtml = article.image 
                ? `<img src="${article.image}" alt="Capa da notícia" class="card-img" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null; this.outerHTML='<div class=\\'card-img-placeholder\\'>${article.source}</div>';">` 
                : fallbackHTML;

            card.innerHTML = `
                <div class="card-img-container">
                    ${imageHtml}
                </div>
                <div class="card-content">
                    <div class="card-meta">
                        <span class="source">${article.source}</span>
                        <span class="date">${dateStr}</span>
                    </div>
                    <h3 class="card-title">${article.title}</h3>
                    <p class="card-desc">${article.summary}</p>
                    <div class="card-tags">
                        <span class="tag">🌍 ${article.region}</span>
                        <span class="tag">📌 ${article.theme}</span>
                    </div>
                    <a href="${article.url}" class="card-link" target="_blank" rel="noopener noreferrer">Ler Notícia Original</a>
                </div>
            `;
            newsContainer.appendChild(card);
        });
    }

    function renderCarousel(highlights) {
        track.innerHTML = '';
        indicators.innerHTML = '';
        carouselItemsCount = highlights.length;

        if (carouselItemsCount === 0) return;

        highlights.forEach((item, index) => {
            const slide = document.createElement('div');
            slide.className = 'carousel-item';
            
            const fallbackHTML = `<div class='carousel-img-placeholder'>${item.source}</div>`;
            const imageHtml = item.image 
                ? `<img src="${item.image}" alt="Destaque" class="carousel-img" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null; this.outerHTML=\`${fallbackHTML}\`;">`
                : fallbackHTML;
            
            slide.innerHTML = `
                ${imageHtml}
                <div class="carousel-caption" onclick="window.open('${item.url}', '_blank')">
                    <span class="carousel-source">${item.source}</span>
                    <h3>${item.title}</h3>
                </div>
            `;
            track.appendChild(slide);

            const dot = document.createElement('div');
            dot.className = 'dot' + (index === 0 ? ' active' : '');
            dot.addEventListener('click', () => goToSlide(index));
            indicators.appendChild(dot);
        });

        updateCarouselPosition();
    }

    function goToSlide(index) {
        currentSlide = index;
        updateCarouselPosition();
    }

    function updateCarouselPosition() {
        if(carouselItemsCount === 0) return;
        track.style.transform = `translateX(-${currentSlide * 100}%)`;
        
        Array.from(indicators.children).forEach((dot, idx) => {
            dot.classList.toggle('active', idx === currentSlide);
        });
    }

    btnNext.addEventListener('click', () => {
        if(carouselItemsCount === 0) return;
        currentSlide = (currentSlide + 1) % carouselItemsCount;
        updateCarouselPosition();
    });

    btnPrev.addEventListener('click', () => {
        if(carouselItemsCount === 0) return;
        currentSlide = (currentSlide - 1 + carouselItemsCount) % carouselItemsCount;
        updateCarouselPosition();
    });

    setInterval(() => {
        if(carouselItemsCount > 1) {
            currentSlide = (currentSlide + 1) % carouselItemsCount;
            updateCarouselPosition();
        }
    }, 5000);

    function updateLastUpdated(isoString) {
        if(!isoString) return;
        const date = new Date(isoString);
        lastUpdatedEl.textContent = `Última coleta automatizada: ${date.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}`;
    }
});
