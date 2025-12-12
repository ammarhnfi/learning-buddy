const API_BASE = import.meta.env.VITE_API_URL || '';

console.log("🔗 API Base URL:", API_BASE); // debug

export const getBotResponse = async (message, userEmail) => {
  try {
    const response = await fetch(`${API_BASE}/chat/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: message,
        user_email: userEmail
      }),
    });
    const data = await response.json();
    return data.answer || "Maaf, terjadi kesalahan di server.";
  } catch (error) {
    console.error("Error fetching bot response:", error);
    return "Maaf, saya sedang mengalami gangguan. Coba lagi nanti.";
  }
};

export const getSmartRecommendation = async (userIdentifier, topN = 5) => {
  try {
    const id = encodeURIComponent(userIdentifier || '');
    const response = await fetch(`${API_BASE}/recommend/smart/${id}?top_n=${topN}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error(`Failed to fetch recommendations: ${response.statusText}`);
    }
    const data = await response.json();
    return data.recommendation || [];
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    return [];
  }
};

export const getSkillAnalysis = async (userEmail) => {
  try {
    const encoded = encodeURIComponent(userEmail);
    console.log("Fetching skill analysis for:", userEmail, "encoded:", encoded);
    const response = await fetch(`${API_BASE}/skill/analyze/${encoded}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    console.log("Skill analysis response status:", response.status, response.statusText);
    if (!response.ok) {
      const text = await response.text();
      console.error("Skill analysis error response text:", text);
      throw new Error(`Failed to fetch skill analysis: ${response.statusText}`);
    }
    const data = await response.json();
    console.log("Skill analysis parsed data:", data);
    return data;
  } catch (error) {
    console.error("Error fetching skill analysis:", error);
    return null;
  }
};
