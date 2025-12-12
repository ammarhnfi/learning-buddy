import React, { useEffect, useState } from 'react';

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [title, setTitle] = useState('Rekomendasi Kursus');

  useEffect(() => {
    // Try to read recommendations passed via sessionStorage
    try {
      const raw = sessionStorage.getItem('lb_recommendations');
      if (raw) {
        const data = JSON.parse(raw);
        setRecommendations(data);
      }
      const t = sessionStorage.getItem('lb_recommendations_title');
      if (t) setTitle(t);
    } catch (e) {
      console.error('Failed to load recommendations from sessionStorage', e);
    }
  }, []);

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">{title}</h1>
      <p className="mb-6 text-gray-600">direkomendasikan.</p>

      <div className="space-y-4">
        {recommendations && recommendations.length > 0 ? (
          recommendations.map((r, idx) => (
            <div key={idx} className="p-4 border rounded-lg bg-white shadow-sm">
              <div className="font-semibold text-lg">{r.course_name}</div>
              <div className="text-sm text-gray-500">Level: {r.course_level_str} • Durasi: {r.hours_to_study} jam</div>
            </div>
          ))
        ) : (
          <div className="text-gray-500">Belum ada rekomendasi.</div>
        )}
      </div>
    </div>
  );
}
