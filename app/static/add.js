document.getElementById('add-debt-item').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const categoryInput = document.getElementById('category') || document.getElementById('category_text');

    const formData = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        category: categoryInput.value,
        risk: document.getElementById('risk').value,
        effort_estimate: document.getElementById('effort_estimate').value,
        status: document.getElementById('status').value,
        assigned_to: document.getElementById('assigned_to').value,
        created_at: new Date().toISOString()
    };

    fetch('/api/debts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })

    .then(response => response.json())
        .then(data => {
            alert('Technical debt item added successfully!');
            window.location.href = '/'; // Redirect to the main page
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while adding the item');
        });
});