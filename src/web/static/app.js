document.addEventListener('DOMContentLoaded', function() {
    // Quick search functionality
    const quickSearchInput = document.getElementById('quick-search');
    const searchResults = document.getElementById('search-results');
    
    if (quickSearchInput && searchResults) {
        let searchTimeout;
        
        quickSearchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.classList.add('hidden');
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performQuickSearch(query);
            }, 300);
        });
        
        // Hide results when clicking outside
        document.addEventListener('click', function(e) {
            if (!quickSearchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.add('hidden');
            }
        });
    }
    
    async function performQuickSearch(query) {
        try {
            const response = await fetch(`/api/search/employees?q=${encodeURIComponent(query)}`);
            const employees = await response.json();
            
            if (employees.length > 0) {
                const resultsHtml = employees.map(emp => `
                    <div class="search-result-item">
                        <a href="/employee/${encodeURIComponent(emp.name)}" class="search-result-link">
                            <div class="search-result-name">${escapeHtml(emp.name)}</div>
                            <div class="search-result-details">${emp.employee_id || 'N/A'} - ${emp.status}</div>
                        </a>
                    </div>
                `).join('');
                
                searchResults.innerHTML = resultsHtml;
                searchResults.classList.remove('hidden');
            } else {
                searchResults.innerHTML = '<div class="search-no-results">Nessun risultato trovato</div>';
                searchResults.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error performing search:', error);
            searchResults.innerHTML = '<div class="search-error">Errore durante la ricerca</div>';
            searchResults.classList.remove('hidden');
        }
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Add smooth scroll behavior for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states for forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Caricamento...';
            }
        });
    });
    
    // Auto-refresh stats ogni 5 minuti
    if (document.querySelector('.stats-grid')) {
        setInterval(async () => {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                updateStatsDisplay(stats);
            } catch (error) {
                console.error('Error refreshing stats:', error);
            }
        }, 5 * 60 * 1000);
    }
    
    function updateStatsDisplay(stats) {
        const statCards = document.querySelectorAll('.stat-card');
        const statLabels = ['total_persons', 'total_functions', 'total_roles', 'interim_roles'];
        
        statCards.forEach((card, index) => {
            const h3 = card.querySelector('h3');
            if (h3 && stats[statLabels[index]]) {
                h3.textContent = stats[statLabels[index]];
            }
        });
    }
});