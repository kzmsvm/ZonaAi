document.getElementById('send').addEventListener('click', async () => {
    const prompt = document.getElementById('prompt').value;
    const response = await fetch('/prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
    });
    const data = await response.json();
    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
});
