import React from 'react';

function BadgeIndicator({ count }) {
  if (count <= 0) return null;

  return (
    <span className="absolute -top-1 -right-1 flex justify-center items-center w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full">
      {count > 9 ? '9+' : count}
    </span>
  );
}

export default BadgeIndicator;