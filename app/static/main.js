async function sendPrompt() {
  const prompt = document.getElementById('prompt').value;
  const session_id = document.getElementById('session_id').value;
  const provider = document.getElementById('provider').value;
  const res = await fetch('/prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, session_id, provider })
  });
  const data = await res.json();
  document.getElementById('response').innerText = data.response;
}
