import React, { useState, useEffect } from 'react';

function CourseDetail({ courseId, onBack }) {
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCourse = async () => {
            setLoading(true);
            setError(null);
            try {
                console.log("Fetching course details for ID:", courseId);
                const response = await fetch(`/courses/${courseId}`);
                if (response.ok) {
                    const data = await response.json();
                    setCourse(data);
                } else {
                    setError("Gagal memuat detail kursus. (Course Not Found)");
                }
            } catch (error) {
                console.error("Failed to fetch course details", error);
                setError("Gagal menghubungi server. Pastikan backend berjalan dan koneksi internet stabil.");
            } finally {
                setLoading(false);
            }
        };

        if (courseId) {
            fetchCourse();
        } else {
            console.warn("No courseId provided to CourseDetail");
            setError("Kursus tidak ditemukan atau ID tidak valid.");
            setLoading(false);
        }
    }, [courseId]);

    if (loading) return (
        <div className="flex justify-center items-center h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
    );

    if (error) return (
        <div className="p-8 text-center">
            <div className="text-red-500 mb-4">{error}</div>
            <button onClick={onBack} className="text-blue-600 hover:underline">Kembali</button>
        </div>
    );

    if (!course) return null;

    return (
        <div className="max-w-6xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg my-8">
            <button
                onClick={onBack}
                className="mb-6 flex items-center text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 transition-colors font-medium"
            >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Kembali ke Dashboard
            </button>

            {/* Header Section */}
            <div className="mb-8 border-b border-gray-200 dark:border-gray-700 pb-8">
                <div className="flex flex-wrap gap-2 mb-4">
                    <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm font-semibold">
                        {course.level}
                    </span>
                    <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-sm font-semibold">
                        {course.hours} Jam Belajar
                    </span>
                    {course.rating && (
                        <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-full text-sm font-semibold flex items-center">
                            <svg className="w-4 h-4 mr-1 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                            {course.rating}
                        </span>
                    )}
                    {course.type && (
                        <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full text-sm font-semibold">
                            {course.type}
                        </span>
                    )}
                </div>

                <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">{course.course_name}</h1>

                {course.summary && (
                    <p className="text-xl text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
                        {course.summary}
                    </p>
                )}

                <div className="flex flex-wrap gap-4 text-sm text-gray-500 dark:text-gray-400">
                    {course.total_students && (
                        <div className="flex items-center">
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                            {course.total_students}
                        </div>
                    )}
                    {course.total_modules && (
                        <div className="flex items-center">
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                            </svg>
                            {course.total_modules}
                        </div>
                    )}
                    {course.price && (
                        <div className="flex items-center font-medium text-green-600 dark:text-green-400">
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {course.price === 'FREE' ? 'Gratis' : 'Berbayar'}
                        </div>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content: Description & Tutorials */}
                <div className="lg:col-span-2 space-y-8">

                    {/* Description */}
                    <section>
                        <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Tentang Kelas</h3>
                        <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300 leading-relaxed"
                            dangerouslySetInnerHTML={{ __html: course.description }} />
                    </section>

                    {/* Tutorials */}
                    <section>
                        <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white flex items-center">
                            Materi Tutorial
                            <span className="ml-3 text-sm font-normal text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full">
                                {course.tutorials.length} Modul
                            </span>
                        </h3>

                        {course.tutorials.length === 0 ? (
                            <div className="text-gray-500 italic">Belum ada daftar tutorial.</div>
                        ) : (
                            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
                                {course.tutorials.map((tutorial, index) => (
                                    <div key={index} className="flex items-center p-4 border-b border-gray-200 dark:border-gray-700 last:border-0 hover:bg-white dark:hover:bg-gray-800 transition-colors">
                                        <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-full font-bold text-sm mr-4">
                                            {index + 1}
                                        </span>
                                        <span className="text-gray-800 dark:text-gray-200 font-medium">{tutorial}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>
                </div>

                {/* Sidebar: Technologies & Info */}
                <div className="space-y-6">
                    {course.technologies && course.technologies.length > 0 && (
                        <div className="bg-gray-50 dark:bg-gray-700/30 p-6 rounded-xl border border-gray-100 dark:border-gray-700">
                            <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Teknologi yang Dipelajari</h4>
                            <div className="flex flex-wrap gap-2">
                                {course.technologies.map((tech, idx) => (
                                    <span key={idx} className="px-3 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium shadow-sm">
                                        {tech.trim()}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="bg-indigo-50 dark:bg-indigo-900/20 p-6 rounded-xl border border-indigo-100 dark:border-indigo-800">
                        <h4 className="text-lg font-bold text-indigo-900 dark:text-indigo-200 mb-2">Mulai Belajar Sekarang</h4>
                        <p className="text-sm text-indigo-700 dark:text-indigo-300 mb-4">
                            Akses materi lengkap dan mulai perjalanan belajarmu.
                        </p>
                        <button className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-md transition-all transform hover:scale-[1.02]">
                            Lanjut Belajar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default CourseDetail;
