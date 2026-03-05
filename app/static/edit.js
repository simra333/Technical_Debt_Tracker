const debtId = document.getElementById('debt-id').value;

// Load existing data
fetch(`/api/debts/${debtId}`)
    .then(response => response.json())
    .then(debt => {
        document.getElementById('title').value = debt.title;
        document.getElementById('description').value = debt.description;
        document.getElementById('risk').value = debt.risk;
        document.getElementById('effort_estimate').value = debt.effort_estimate;
        document.getElementById('status').value = debt.status;
        document.getElementById('assigned_to').value = debt.assigned_to;
    })
    .catch(error => {
        console.error('Error fetching debt item:', error);
        alert('An error occurred while fetching the debt item');
    });

//Handle form submission
document.getElementById('edit-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        risk: document.getElementById('risk').value,
        effort_estimate: document.getElementById('effort_estimate').value,
        status: document.getElementById('status').value,
        assigned_to: document.getElementById('assigned_to').value
    };

    fetch(`/api/debts/${debtId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
        .then(() => {
            alert('Technical debt item updated successfully!');
            window.location.href = '/'; // Redirect to the main page
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the item');
        });
    });