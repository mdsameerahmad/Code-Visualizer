import React from 'react';
import { AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const ErrorBox = ({ error }) => {
  if (!error) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 bg-red-950/40 border border-red-500/50 rounded-lg flex flex-col gap-2 shadow-lg"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span className="font-bold uppercase text-xs tracking-widest">{error.type}</span>
        </div>
        {error.line > 0 && (
          <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-[10px] rounded border border-red-500/30 font-mono">
            Line {error.line}
          </span>
        )}
      </div>
      <p className="text-red-200 text-sm font-medium leading-relaxed">
        {error.message}
      </p>
    </motion.div>
  );
};

export default ErrorBox;
