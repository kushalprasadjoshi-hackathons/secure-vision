document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');

    startBtn.addEventListener('click', function() {
        fetch('/start_surveillance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            alert(data.status);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    stopBtn.addEventListener('click', function() {
        fetch('/stop_surveillance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            alert(data.status);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});