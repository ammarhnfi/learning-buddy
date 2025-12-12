import React from 'react';
import { createPortal } from 'react-dom';

export default function RecommendationModal({ open, onClose, recommendations = [], user = '' }) {
  if (!open) return null;

  const modal = (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black opacity-50" onClick={onClose} />
      <div className="relative bg-white dark:bg-gray-800 w-11/12 max-w-2xl rounded-lg shadow-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Rekomendasi Kursus untuk {user || 'Anda'}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Berdasarkan progres terakhir, ini kursus yang direkomendasikan.</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {recommendations.length === 0 ? (
            <div className="text-center py-10 text-gray-500">Tidak ada rekomendasi saat ini.</div>
          ) : (
            recommendations.map((r, idx) => (
              <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-100 dark:border-gray-600">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{r.course_name}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-300">Level: {r.course_level_str} • Durasi: {r.hours_to_study} jam</div>
                    {r.reason && <div className="text-sm text-gray-400 mt-1">Alasan: {r.reason}</div>}
                    {typeof r.score === 'number' && <div className="text-xs text-gray-400 mt-1">Relevansi: {(r.score*100).toFixed(0)}%</div>}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="mt-4 flex justify-end">
          <button onClick={onClose} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md">Tutup</button>
        </div>
      </div>
    </div>
  );

  if (typeof document === 'undefined') return null;
  return createPortal(modal, document.body);
}
