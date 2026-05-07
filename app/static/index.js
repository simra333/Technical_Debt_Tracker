fetch('/api/debts')
    .then(response => {
        // If not logged in, send them to the login page
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }

        // If something else went wrong, stop and show an error
        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        return response.json();
    })
    .then(data => {
        if (!data) return; // this happens when we redirected to /login

        const debtList = document.getElementById('debt-list');

        if (!Array.isArray(data)) {
            debtList.innerHTML = '<li>Error: API did not return a list of technical debt items.</li>';
            return;
        }

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
        });
    })
    .catch(error => {
        console.error('Error loading debts:', error);
        const debtList = document.getElementById('debt-list');
        debtList.innerHTML = '<li>Error loading technical debt items. Please log in and try again.</li>';
    });