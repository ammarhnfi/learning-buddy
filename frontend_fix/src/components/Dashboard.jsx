import React, { useState, useEffect } from 'react';
import {
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend
} from 'recharts';

function Dashboard({ userEmail, onSummarize, onSelectCourse }) {
    const [userData, setUserData] = useState(null);
    const [skillData, setSkillData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchUserData = async () => {
            setLoading(true);
            try {
                // Fetch Dashboard Data
                const dashboardRes = await fetch(`/dashboard/${userEmail}`);
                if (dashboardRes.ok) {
                    const data = await dashboardRes.json();
                    setUserData(data);
                }

                // Fetch Skill Analysis Data
                const skillRes = await fetch(`/skill/analyze/${userEmail}`);
                if (skillRes.ok) {
                    const sData = await skillRes.json();
                    setSkillData(sData);
                }

            } catch (error) {
                console.error("Failed to fetch data", error);
            } finally {
                setLoading(false);
            }
        };

        if (userEmail) {
            fetchUserData();
        }
    }, [userEmail]);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!userData) {
        return <div className="text-center py-10 text-red-500">Failed to load data.</div>;
    }

    // Prepare Data for Charts
    const radarData = skillData?.skill_development?.top_skills?.map(s => ({
        subject: s.skill,
        A: s.proficiency,
        fullMark: 100
    })) || [];

    const pieData = [
        { name: 'Selesai', value: userData.stats.completed, color: '#16a34a' },
        { name: 'Proses', value: userData.stats.in_progress, color: '#2563eb' },
    ];
    // Filter out zero values for cleaner pie chart
    const activePieData = pieData.filter(d => d.value > 0);

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header & Welcome */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                        Halo, {userData.user.name} 👋
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-1">
                        Berikut adalah progres belajar Anda sejauh ini.
                    </p>
                </div>
                <button
                    onClick={onSummarize}
                    className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg shadow-sm transition-colors flex items-center"
                >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Rangkum Progres
                </button>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Total Jam Belajar</div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">{userData.stats.total_hours} Jam</div>
                </div>
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Kursus Selesai</div>
                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">{userData.stats.completed}</div>
                </div>
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Sedang Dipelajari</div>
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{userData.stats.in_progress}</div>
                </div>
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Rata-rata Nilai</div>
                    <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{userData.stats.average_score}</div>
                </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Skill Radar Chart */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Peta Keahlian (Skill Radar)</h3>
                    <div className="h-[300px] w-full">
                        {radarData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                                    <PolarGrid stroke="#e5e7eb" />
                                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 12 }} />
                                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                    <Radar
                                        name="Skill Level"
                                        dataKey="A"
                                        stroke="#4f46e5"
                                        fill="#6366f1"
                                        fillOpacity={0.6}
                                    />
                                    <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} />
                                </RadarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-400">
                                Belum ada data skill yang cukup.
                            </div>
                        )}
                    </div>
                </div>

                {/* Course Progress Pie Chart */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Status Pembelajaran</h3>
                    <div className="h-[300px] w-full flex items-center justify-center">
                        {activePieData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={activePieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={100}
                                        fill="#8884d8"
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {activePieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                    <Legend verticalAlign="bottom" height={36} />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="text-gray-400">Belum ada kursus yang diambil.</div>
                        )}
                    </div>
                </div>
            </div>

            {/* Course List */}
            <div className="space-y-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Kursus Saya</h2>

                {userData.courses.length === 0 ? (
                    <div className="text-center py-10 bg-white dark:bg-gray-800 rounded-xl border border-dashed border-gray-300 dark:border-gray-700">
                        <p className="text-gray-500 dark:text-gray-400">Belum ada kursus yang diambil.</p>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {userData.courses.map((course) => (
                            <div
                                key={course.id}
                                onClick={() => onSelectCourse(course.id)}
                                className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-all cursor-pointer group"
                            >
                                <div className="flex flex-col md:flex-row justify-between gap-4">

                                    {/* Left: Info */}
                                    <div className="flex-grow">
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border
                        ${course.level === 'Dasar' ? 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800' :
                                                    course.level === 'Menengah' ? 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300 dark:border-yellow-800' :
                                                        'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800'}`}>
                                                {course.level}
                                            </span>
                                            <span className={`text-xs font-medium ${course.status === 'Lulus' ? 'text-green-600' : 'text-blue-600'}`}>
                                                {course.status}
                                            </span>
                                        </div>

                                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors mb-3">
                                            {course.title}
                                        </h3>

                                        {/* Progress Bar */}
                                        <div className="w-full max-w-md bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-2">
                                            <div
                                                className={`h-2.5 rounded-full ${course.status === 'Lulus' ? 'bg-green-500' : 'bg-blue-600'}`}
                                                style={{ width: `${course.progress_pct}%` }}
                                            ></div>
                                        </div>
                                        <div className="text-sm text-gray-500 dark:text-gray-400 flex gap-4">
                                            <span>{course.progress_pct}% Selesai</span>
                                            <span>•</span>
                                            <span>{course.hours_spent} / {course.total_hours} Jam</span>
                                        </div>
                                    </div>

                                    {/* Right: Score & Action */}
                                    <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-center gap-4 min-w-[120px]">
                                        {course.score !== null ? (
                                            <div className="text-right">
                                                <div className="text-xs text-gray-500 dark:text-gray-400">Nilai Akhir</div>
                                                <div className="text-2xl font-bold text-gray-900 dark:text-white">{course.score}</div>
                                            </div>
                                        ) : (
                                            <div className="text-sm text-gray-400 italic">Belum ada nilai</div>
                                        )}

                                        <button
                                            onClick={() => course.id && onSelectCourse(course.id)}
                                            disabled={!course.id}
                                            className={`text-sm font-medium flex items-center ${course.id ? 'text-indigo-600 dark:text-indigo-400 hover:underline cursor-pointer' : 'text-gray-400 cursor-not-allowed'}`}
                                            title={!course.id ? "Detail kursus tidak tersedia saat ini" : "Lihat Detail Kursus"}
                                        >
                                            Lihat Detail
                                            <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                            </svg>
                                        </button>
                                    </div>

                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Dashboard;
