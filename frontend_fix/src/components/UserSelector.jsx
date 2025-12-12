import React, { useState, useEffect } from 'react';

function UserSelector({ currentUserEmail, onUserChange }) {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await fetch('/dashboard/users');
                if (response.ok) {
                    const data = await response.json();
                    setUsers(data);
                }
            } catch (error) {
                console.error("Failed to fetch users", error);
            } finally {
                setLoading(false);
            }
        };
        fetchUsers();
    }, []);

    if (loading) {
        return <div className="text-sm text-gray-500">Loading users...</div>;
    }

    return (
        <div className="flex items-center space-x-2">
            <label htmlFor="user-select" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                User:
            </label>
            <select
                id="user-select"
                value={currentUserEmail}
                onChange={(e) => onUserChange(e.target.value)}
                className="block w-64 px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-gray-900 dark:text-white"
            >
                {users.map((user) => (
                    <option key={user.email} value={user.email}>
                        {user.name} ({user.email})
                    </option>
                ))}
            </select>
        </div>
    );
}

export default UserSelector;
