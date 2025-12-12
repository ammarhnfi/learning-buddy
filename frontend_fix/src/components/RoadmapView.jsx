import React, { useState, useEffect } from 'react';
import ReactFlow, {
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

// Custom node styles
const nodeStyles = {
    background: '#fff',
    border: '1px solid #e2e8f0',
    borderRadius: '16px',
    padding: '20px',
    width: 260,
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    textAlign: 'left',
    cursor: 'pointer',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
};

function RoadmapView({ userEmail, onSelectCourse }) {
    const [roadmapData, setRoadmapData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [selectedPathId, setSelectedPathId] = useState(null);

    useEffect(() => {
        const fetchRoadmap = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/roadmap/${userEmail}`);
                if (response.ok) {
                    const data = await response.json();
                    setRoadmapData(data);

                    if (data.learning_paths && data.learning_paths.length > 0) {
                        setSelectedPathId(data.learning_paths[0].path_id);
                    }
                }
            } catch (error) {
                console.error("Failed to fetch roadmap", error);
            } finally {
                setLoading(false);
            }
        };

        if (userEmail) {
            fetchRoadmap();
        }
    }, [userEmail]);

    useEffect(() => {
        if (!roadmapData || !selectedPathId) return;

        const path = roadmapData.learning_paths.find(p => p.path_id === selectedPathId);
        if (!path) return;

        const newNodes = [];
        const newEdges = [];
        let yPos = 50;

        path.courses.forEach((course, index) => {
            // Status Logic
            let statusColor = '#94a3b8'; // gray-400
            let statusBg = '#f8fafc'; // slate-50
            let statusBorder = '#cbd5e1'; // slate-300
            let glow = 'none';

            if (course.status === 'Lulus') {
                statusColor = '#16a34a'; // green-600
                statusBg = '#f0fdf4'; // green-50
                statusBorder = '#bbf7d0'; // green-200
            } else if (course.status === 'Sedang Mempelajari') {
                statusColor = '#2563eb'; // blue-600
                statusBg = '#eff6ff'; // blue-50
                statusBorder = '#bfdbfe'; // blue-200
            }

            newNodes.push({
                id: course.course_id.toString(),
                position: { x: 250, y: yPos },
                data: {
                    label: (
                        <div onClick={() => onSelectCourse(course.course_id)}>
                            <div className="flex justify-between items-start mb-2">
                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide`}
                                    style={{ color: statusColor, backgroundColor: statusBg, borderColor: statusBorder, borderWidth: '1px' }}>
                                    {course.status === 'Lulus' ? 'Selesai' : course.status === 'Sedang Mempelajari' ? 'Aktif' : 'Belum'}
                                </span>
                                <span className="text-[10px] text-gray-400 font-medium">{course.level}</span>
                            </div>
                            <div className="font-bold text-sm text-gray-800 dark:text-gray-900 leading-tight mb-2">
                                {course.course_name}
                            </div>
                            <div className="flex items-center text-[11px] text-gray-500">
                                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                {course.hours} Jam
                            </div>
                        </div>
                    )
                },
                style: {
                    ...nodeStyles,
                    borderColor: statusBorder,
                    backgroundColor: '#fff' // Always white bg for card look
                },
            });

            if (index > 0) {
                newEdges.push({
                    id: `e${index - 1}-${index}`,
                    source: path.courses[index - 1].course_id.toString(),
                    target: course.course_id.toString(),
                    markerEnd: { type: MarkerType.ArrowClosed },
                    type: 'smoothstep',
                    animated: course.status === 'Sedang Mempelajari',
                    style: { stroke: '#cbd5e1', strokeWidth: 2 },
                });
            }

            yPos += 180; // Increased spacing
        });

        setNodes(newNodes);
        setEdges(newEdges);

    }, [selectedPathId, roadmapData, setNodes, setEdges, onSelectCourse]);

    if (loading) return (
        <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
    );

    if (!roadmapData) return <div className="text-center py-10 text-red-500">Failed to load roadmap.</div>;

    return (
        <div className="h-[calc(100vh-100px)] flex flex-col">
            <div className="mb-6 flex flex-col sm:flex-row justify-between items-center px-4 gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Learning Roadmap</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Ikuti alur belajar yang telah disusun untukmu.</p>
                </div>

                <select
                    value={selectedPathId || ''}
                    onChange={(e) => setSelectedPathId(parseInt(e.target.value))}
                    className="px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[250px]"
                >
                    {roadmapData.learning_paths.map(path => (
                        <option key={path.path_id} value={path.path_id}>
                            {path.path_name}
                        </option>
                    ))}
                </select>
            </div>

            <div className="flex-grow bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 shadow-inner overflow-hidden relative">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    fitView
                    attributionPosition="bottom-right"
                >
                    <Background color="#94a3b8" gap={20} size={1} />
                    <Controls />
                </ReactFlow>
            </div>
        </div>
    );
}

export default RoadmapView;
