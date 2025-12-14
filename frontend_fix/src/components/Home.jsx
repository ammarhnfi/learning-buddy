import React from 'react';

function Home() {
    return (
        <div className="space-y-12">
            {/* Hero Section */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 md:p-12 text-center border border-gray-200 dark:border-gray-700">
                <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-4">
                    Learning Buddy adalah...
                </h1>
                <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                    Teman belajar pribadimu yang siap membantu kapan saja. Dapatkan rekomendasi materi,
                    pantau progress belajarmu, dan diskusikan kesulitanmu bersama AI yang cerdas.
                </p>
            </div>

            {/* Features Section */}
            <div className="space-y-8">
                <div className="text-center">
                    <h2 className="text-3xl font-bold text-gray-900 dark:text-white inline-block px-6 py-2 border-2 border-gray-900 dark:border-white rounded-full">
                        Kenapa Learning Buddy...
                    </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Manfaat 1 */}
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                            Personalized Roadmap
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                            Dapatkan jalur belajar yang disesuaikan khusus dengan tujuan dan kemampuanmu saat ini.
                        </p>
                    </div>

                    {/* Manfaat 2 */}
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                            AI Assistant 24/7
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                            Tanya jawab seputar materi, coding error, atau tips belajar kapan saja tanpa batas waktu.
                        </p>
                    </div>

                    {/* Manfaat 3 */}
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                            Progress Tracking
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                            Visualisasikan perkembangan skillmu dengan data real-time yang akurat.
                        </p>
                    </div>
                </div>
            </div>

            {/* Footer Section */}
            <div className="border-t-2 border-gray-200 dark:border-gray-700 pt-8 mt-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center md:text-left">
                    <div>
                        <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Learning Buddy</h4>
                        <p className="text-gray-500 dark:text-gray-400">
                            Jl. Batik Kumeli No.50, Bandung
                        </p>
                    </div>
                    <div>
                        <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Tentang Kami</h4>
                        <ul className="space-y-1 text-gray-500 dark:text-gray-400">
                            <li><a href="#" className="hover:text-blue-600">Visi & Misi</a></li>
                            <li><a href="#" className="hover:text-blue-600">Tim Kami</a></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Hubungi Kami</h4>
                        <ul className="space-y-1 text-gray-500 dark:text-gray-400">
                            <li>support@learningbuddy.com</li>
                            <li>+62 812 3456 7890</li>
                        </ul>
                    </div>
                </div>
                <div className="text-center mt-8 text-gray-400 text-sm">
                    &copy; 2025 Team Learning Buddy. All rights reserved.
                </div>
            </div>
        </div>
    );
}

export default Home;
