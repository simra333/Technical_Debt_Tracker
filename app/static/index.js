// Fetch and display technical debt items
fetch('/api/debts')
    .then(response => response.json())
    .then(data => {
        const debtList = document.getElementById('debt-list');

        if (data.length === 0) {
            debtList.innerHTML = '<li>No technical debt items found.</li>';
            return;
        }
        data.forEach(debt => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <strong>${debt.title}</strong> - ${debt.description} 
                <br>
                <em>Created on: ${new Date(debt.created_at).toLocaleDateString()}</em>
                <br>
                Status: ${debt.status}
                <br>
                <button onclick="window.location.href='/edit/${debt.id}'">Edit</button>
                <button onclick="deleteDebt(${debt.id})">Delete</button>
            `;
            debtList.appendChild(listItem);
        })
    });

// Function to delete a debt item
function deleteDebt(id) {
    if (!confirm('Are you sure you want to delete this debt item?')) {
        return;
    }

    fetch(`/api/debts/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.status === 204) {
            alert('Item deleted successfully');
            location.reload();
        } else {
            alert('Failed to delete item');
        }
    })
    .catch(error => {
        console.error('Error deleting item:', error);
        alert('An error occurred while deleting the item');
    });
}
