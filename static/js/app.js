const form = document.getElementById('preferencesForm');
const resultsDiv = document.getElementById('results');
const submitBtn = document.getElementById('submitBtn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Analyzing...';
    
    resultsDiv.innerHTML = '<div class="card loading"><div class="spinner"></div><p>Scoring apartments based on your preferences...</p></div>';

    try {
        const formData = new FormData(form);
        const preferences = {
            work_address: formData.get('work_address'),
            max_rent: parseInt(formData.get('max_rent')),
            min_rent: 0,
            min_bedrooms: parseFloat(formData.get('min_bedrooms')),
            min_bathrooms: parseFloat(formData.get('min_bathrooms')),
            min_sqft: 0
        };

        const response = await fetch('/api/rank', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(preferences)
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to rank apartments');
        }

        displayResults(data);

    } catch (error) {
        resultsDiv.innerHTML = `<div class="card error">ERROR: ${error.message}</div>`;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '🔍 Find My Perfect Apartment';
    }
});

function displayResults(data) {
    if (data.apartments.length === 0) {
        resultsDiv.innerHTML = `
            <div class="card empty-state">
                <div class="empty-state-icon">🏚️</div>
                <h2>No apartments found</h2>
                <p>Try adjusting your requirements to see more options.</p>
            </div>
        `;
        return;
    }

    let html = '<div class="card">';
    html += `<div class="results-header">`;
    html += `<h2>Top Matches</h2>`;
    html += `<div class="results-count">${data.count} apartments found</div>`;
    html += `</div>`;

    data.apartments.slice(0, 20).forEach((item, index) => {
        const apt = item.listing;
        const score = item.score;
        const breakdown = item.breakdown;
        const commute = item.commute_info;

        html += `<div class="apartment-card">`;
        html += `<div class="apartment-header">`;
        html += `<div class="apartment-details">`;
        html += `<div class="apartment-address">${index + 1}. ${apt.address}</div>`;
        html += `<div class="apartment-specs">`;
        html += `$${apt.price}/mo | ${apt.bedrooms || '?'} bed | ${apt.bathrooms || '?'} bath`;
        if (apt.sqft) html += ` | ${apt.sqft} sqft`;
        html += `</div>`;
        
        if (commute && commute.distance_miles) {
            html += `<div class="commute-info">🚗 ${commute.distance_miles} mi (~${commute.estimated_minutes} min commute)</div>`;
        }
        
        html += `</div>`;
        html += `<div class="apartment-score">${score}/100</div>`;
        html += `</div>`;
        
        html += `<div class="score-breakdown">`;
        for (const [key, data] of Object.entries(breakdown)) {
            html += `<div class="score-item">`;
            html += `<div class="score-label">${key.replace('_', ' ')}</div>`;
            html += `<div class="score-value">${data.score.toFixed(1)}</div>`;
            html += `</div>`;
        }
        html += `</div>`;
        
        html += `<a href="${apt.listing_url}" target="_blank" class="apartment-link">View on Zillow →</a>`;
        html += `</div>`;
    });

    html += '</div>';
    resultsDiv.innerHTML = html;
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}
