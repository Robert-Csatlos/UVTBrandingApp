fetch('/api/message')
    .then(response => response.json())
    .then(data => {
        document.getElementById('api-data').innerText = data.message;
    })
    .catch(error => {
        document.getElementById('api-data').innerText = "Failed to load data.";
    });