document.addEventListener("DOMContentLoaded", () => {
    const newsContainer = document.getElementById('news-container');
    const regionFilter = document.getElementById('region-filter');
    const themeFilter = document.getElementById('theme-filter');
    const originFilter = document.getElementById('origin-filter');
    const lastUpdatedEl = document.getElementById('last-updated');
    
    // Carousel Elements
    const track = document.getElementById('carousel-track');
    const btnPrev = document.getElementById('carousel-prev');
    const btnNext = document.getElementById('carousel-next');
    const indicators = document.getElementById('carousel-indicators');

    let articles = [];
    let currentSlide = 0;
    let carouselItemsCount = 0;

    // Fetch News Data
    fetch('news.json')
        .then(response => response.json())
        .then(data => {
            articles = data.articles;
            updateLastUpdated(data.last_updated);
            applyFilters(); // Renders first 50
        })
        .catch(err => console.error("Error loading news data:", err));

    // Fetch Bulletin/Highlights Data
    fetch('bulletin.json')
        .then(response => response.json())
        .then(data => {
            renderCarousel(data.highlights);
        })
        .catch(err => console.error("Error loading bulletin data:", err));

    // Event Listeners for Filters
    regionFilter.addEventListener('change', applyFilters);
    themeFilter.addEventListener('change', applyFilters);
    originFilter.addEventListener('change', applyFilters);

    function applyFilters() {
        const region = regionFilter.value;
        const theme = themeFilter.value;
        const origin = originFilter.value;

        const filtered = articles.filter(article => {
            const matchRegion = region === 'all' || article.region === region;
            const matchTheme = theme === 'all' || article.theme === theme;
            const matchOrigin = origin === 'all' || article.origin === origin;
            return matchRegion && matchTheme && matchOrigin;
        });

        // Take up to 50 items
        renderNews(filtered.slice(0, 50));
    }

    function renderNews(newsArray) {
        newsContainer.innerHTML = '';
        if (newsArray.length === 0) {
            newsContainer.innerHTML = '<p>Nenhuma notícia encontrada para estes filtros.</p>';
            return;
        }

        newsArray.forEach(article => {
            const dateStr = new Date(article.published_at).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
            
            const card = document.createElement('article');
            card.className = 'card';
            
            const imageHtml = article.image 
                ? `<img src="${article.image}" alt="Capa" class="card-img" loading="lazy">` 
                : `<div class="card-img-placeholder">${article.source}</div>`;

            card.innerHTML = `
                <div class="card-img-container">
                    ${imageHtml}
                </div>
                <div class="card-content">
                    <div class="card-meta">
                        <strong>${article.source}</strong>
                        <span>${dateStr}</span>
                    </div>
                    <h3 class="card-title">${article.title}</h3>
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
            // Slide
            const slide = document.createElement('div');
            slide.className = 'carousel-item';
            
            const imageHtml = item.image 
                ? `<img src="${item.image}" alt="Destaque" class="carousel-img">`
                : `<div class="carousel-img-placeholder">${item.source}</div>`;
            
            slide.innerHTML = `
                ${imageHtml}
                <div class="carousel-caption" onclick="window.open('${item.url}', '_blank')">
                    <p>${item.source}</p>
                    <h3>${item.title}</h3>
                </div>
            `;
            track.appendChild(slide);

            // Indicator
            const dot = document.createElement('div');
            dot.className = 'dot' + (index === 0 ? ' active' : '');
            dot.addEventListener('click', () => goToSlide(index));
            indicators.appendChild(dot);
        });

        // Initialize Carousel
        updateCarouselPosition();
    }

    function goToSlide(index) {
        currentSlide = index;
        updateCarouselPosition();
    }

    function updateCarouselPosition() {
        if(carouselItemsCount === 0) return;
        track.style.transform = `translateX(-${currentSlide * 100}%)`;
        
        // Update dots
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

    // Auto-advance carousel
    setInterval(() => {
        if(carouselItemsCount > 1) {
            currentSlide = (currentSlide + 1) % carouselItemsCount;
            updateCarouselPosition();
        }
    }, 5000);

    function updateLastUpdated(isoString) {
        if(!isoString) return;
        const date = new Date(isoString);
        lastUpdatedEl.textContent = `Última coleta automatizada: ${date.toLocaleString('pt-BR')}`;
    }
});
