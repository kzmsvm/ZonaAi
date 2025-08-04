import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [systems, setSystems] = useState([]);
  const [selectedSystem, setSelectedSystem] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");

  useEffect(() => {
    axios.get("/integrations/scan").then((res) => setSystems(res.data.detected_systems));
  }, []);

  const addIntegration = async () => {
    try {
      await axios.post("/integrations/add", { system: selectedSystem, api_key: apiKey, base_url: `https://${selectedSystem}.com` });
      alert("Entegrasyon eklendi!");
    } catch (e) {
      alert("Hata: " + e.message);
    }
  };

  const sendPrompt = async () => {
    const res = await axios.post("/prompt", { prompt, provider: "codex" });
    setResponse(res.data.response);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl">ZonaAi</h1>
      <div className="my-4">
        <h2>Entegrasyon Ekle</h2>
        <select onChange={(e) => setSelectedSystem(e.target.value)} className="border p-2">
          <option value="">Sistem Seç</option>
          {systems.map((sys) => (
            <option key={sys} value={sys}>
              {sys}
            </option>
          ))}
        </select>
        <input
          type="text"
          placeholder="API Anahtarı"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          className="border p-2 ml-2"
        />
        <button onClick={addIntegration} className="bg-blue-500 text-white p-2 ml-2">
          Ekle
        </button>
      </div>
      <div>
        <h2>Sohbet</h2>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="border p-2 w-full"
        />
        <button onClick={sendPrompt} className="bg-green-500 text-white p-2 mt-2">
          Gönder
        </button>
        <p className="mt-2">{response}</p>
      </div>
    </div>
  );
};

export default App;

