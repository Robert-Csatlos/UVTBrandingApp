async function loadInventory() {
    try {
        // Change the URL to match your FastAPI endpoint exactly
        const response = await fetch('/inventory/');
        
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        const materials = await response.json();
        const displayElement = document.getElementById('api-data');

        if (materials.length === 0) {
            displayElement.innerText = "Inventory is currently empty.";
            return;
        }

        let html = '<ul style="list-style-type: none; padding: 0;">';
        materials.forEach(item => {
            // Adding all fields from the Inventory model
            html += `
                <li>
                    <strong>${item.name}</strong> (Qty: ${item.quantity})<br>
                    <small>
                        <strong>Code:</strong> ${item.inventory_code} | 
                        <strong>Category:</strong> ${item.category} | 
                        <strong>Status:</strong> ${item.status}<br>
                        <strong>Location:</strong> ${item.location} | 
                        <strong>Responsible:</strong> ${item.responsible_person}
                    </small>
                </li>`;
        });
        html += '</ul>';

displayElement.innerHTML = html;

        displayElement.innerHTML = html;

    } catch (error) {
        console.error("Error loading materials:", error);
        document.getElementById('api-data').innerText = "Error loading database.";
    }
}

window.onload = loadInventory;