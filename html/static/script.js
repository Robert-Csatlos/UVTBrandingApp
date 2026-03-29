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

        let html = '<ul>';
        materials.forEach(item => {
            // Ensure these property names match your models.py (name and quantity)
            html += `<li><strong>${item.name}</strong> (Qty: ${item.quantity})</li>`;
        });
        html += '</ul>';

        displayElement.innerHTML = html;

    } catch (error) {
        console.error("Error loading materials:", error);
        document.getElementById('api-data').innerText = "Error loading database.";
    }
}

window.onload = loadInventory;