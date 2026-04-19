import { motion } from 'framer-motion';

const ExecutionFlow = ({ step, prevStep }) => {
  if (!step) return null;

  const lineChanged = prevStep?.line_number !== step.line_number;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 transition-colors"
    >
      <div className="flex items-center gap-3">
        <motion.div
          key={step.line_number}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.4 }}
          className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-600/30 border border-indigo-500"
        >
          <span className="text-xs font-bold text-indigo-300">→</span>
        </motion.div>

        <div className="flex-1">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Current Execution</div>
          <motion.div
            initial={lineChanged ? { opacity: 0.5, y: 5 } : {}}
            animate={{ opacity: 1, y: 0 }}
            key={`${step.line_number}-${step.line_content}`}
            className="font-mono text-sm text-indigo-300 mt-1 break-words"
          >
            Line {step.line_number}: <span className="text-gray-200">{step.line_content}</span>
          </motion.div>
        </div>
      </div>

      {step.explanation && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="mt-2 pt-2 border-t border-gray-700/50"
        >
          <p className="text-xs text-gray-400 italic">{step.explanation}</p>
        </motion.div>
      )}

      {step.output && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="mt-2 pt-2 border-t border-gray-700/50"
        >
          <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Output</div>
          <div className="px-2 py-1.5 bg-gray-950 rounded border border-gray-700/50 font-mono text-sm text-green-400">
            {step.output}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default ExecutionFlow;
