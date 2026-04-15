import React from 'react';
import { Play, Loader2 } from 'lucide-react';

const RunButton = ({ onClick, isLoading }) => {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-800 disabled:opacity-50 text-white rounded-md font-medium transition-all"
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <Play className="w-4 h-4 fill-current" />
      )}
      Run Code
    </button>
  );
};

export default RunButton;
