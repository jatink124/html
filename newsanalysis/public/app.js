// Function to add a visual row for stocks
function addItemRow(data = {}) {
    const container = document.getElementById('items-container');
    const div = document.createElement('div');
    div.className = 'item-row';
    div.innerHTML = `
        <div>
            <label>Stock/Entity</label>
            <input type="text" class="entity_name" value="${data.entity_name || ''}" placeholder="e.g. Tata Steel">
        </div>
        <div>
            <label>What's Happening?</label>
            <textarea class="event_details" rows="2">${data.event_details || ''}</textarea>
        </div>
        <div>
            <label>Layman Explanation</label>
            <textarea class="layman_explanation" rows="2">${data.layman_explanation || ''}</textarea>
        </div>
        <button class="btn btn-remove" onclick="this.parentElement.remove()">X</button>
    `;
    container.appendChild(div);
}

// Function to collect data and save
async function saveReport(isEditMode = false, reportId = null) {
    const data = {
        report_date: document.getElementById('reportDate').value,
        title: document.getElementById('reportTitle').value,
        overall_strategy: document.getElementById('overallStrategy').value,
        items: []
    };

    // Scrape data from all item rows
    document.querySelectorAll('.item-row').forEach(row => {
        data.items.push({
            entity_name: row.querySelector('.entity_name').value,
            event_details: row.querySelector('.event_details').value,
            layman_explanation: row.querySelector('.layman_explanation').value
        });
    });

    const url = isEditMode ? `/api/reports/${reportId}` : '/api/reports';
    const method = isEditMode ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Saved Successfully!');
            window.location.href = '/dashboard.html'; // Go back to dashboard
        } else {
            alert('Error saving report');
        }
    } catch (err) {
        console.error(err);
        alert('Server error');
    }
}