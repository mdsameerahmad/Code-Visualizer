import { AnimatePresence, motion } from 'framer-motion';

const ArrayView = ({ arrays }) => {
  if (!arrays || Object.keys(arrays).length === 0) {
    return null;
  }

  return (
    <div className="space-y-6">
      {Object.entries(arrays).map(([name, data]) => (
        <div
          key={name}
          className="p-4 bg-gray-900 rounded-lg border border-gray-800"
        >
          <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
            Array: <span className="text-indigo-400">{name}</span>
          </h3>

          <div className="flex flex-wrap gap-2">
            {data.values.map((val, idx) => {
              // ✅ Correct display logic
              const displayValue =
                val === null || val === undefined ? '?' : val;

              return (
                <motion.div
                  key={`${name}-${idx}`}
                  layout
                  className={`w-12 h-12 flex flex-col items-center justify-center rounded border transition-colors ${
                    data.lastUpdatedIndex === idx
                      ? 'bg-indigo-600/30 border-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.3)]'
                      : 'bg-gray-800 border-gray-700'
                  }`}
                >
                  <span className="text-xs text-gray-500 mb-0.5">
                    {idx}
                  </span>

                  <AnimatePresence mode="wait">
                    <motion.span
                      key={displayValue}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      exit={{ scale: 0.8, opacity: 0 }}
                      className={`font-mono font-bold ${
                        displayValue === '?'
                          ? 'text-gray-500'
                          : 'text-white'
                      }`}
                    >
                      {displayValue}
                    </motion.span>
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ArrayView;