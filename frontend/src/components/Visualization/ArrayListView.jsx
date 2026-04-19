import { motion } from 'framer-motion';

const ArrayListView = ({ lists = {}, prevLists = {} }) => {
  if (!lists || Object.keys(lists).length === 0) {
    return null;
  }

  const detectChanges = (name) => {
    const current = lists[name];
    const prev = prevLists?.[name];

    if (!current || !prev) return { added: [], removed: [], changed: true };

    const currValues = current.values || [];
    const prevValues = prev.values || [];

    const added = currValues.slice(prevValues.length);
    const removed = prevValues.length > currValues.length;

    return {
      added,
      removed,
      sizeChanged: currValues.length !== prevValues.length,
      changed: currValues.length !== prevValues.length || 
               currValues.some((v, i) => v !== prevValues[i])
    };
  };

  return (
    <div className="space-y-6">
      {Object.entries(lists).map(([name, data]) => {
        const changes = detectChanges(name);
        const values = data.values || [];

        return (
          <motion.div
            key={name}
            layout
            className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                ArrayList: <span className="text-cyan-400">{name}</span>
              </h3>
              <span className="text-xs text-gray-500">
                size: <span className={changes.sizeChanged ? 'text-cyan-400 font-bold' : ''}>
                  {values.length}
                </span>
              </span>
            </div>

            <motion.div layout className="flex flex-wrap gap-2">
              {values.length === 0 ? (
                <div className="text-gray-600 text-sm italic">Empty ArrayList</div>
              ) : (
                values.map((val, idx) => {
                  const isAdded = changes.added.includes(val);
                  const displayValue = val === null || val === undefined ? '?' : val;

                  return (
                    <motion.div
                      key={`${name}-${idx}`}
                      layout
                      initial={isAdded ? { scale: 0, x: 50, opacity: 0 } : {}}
                      animate={{ scale: 1, x: 0, opacity: 1 }}
                      exit={{ scale: 0, x: -50, opacity: 0 }}
                      transition={{ type: "spring", stiffness: 200, damping: 25 }}
                      className={`relative px-3 py-2 rounded-md border-2 flex items-center justify-center min-w-[45px] font-mono font-bold text-sm transition-all ${
                        isAdded
                          ? 'bg-cyan-600/40 border-cyan-500 text-cyan-200 shadow-[0_0_20px_rgba(34,211,238,0.3)]'
                          : displayValue === '?'
                          ? 'bg-gray-800/50 border-gray-700 text-gray-500'
                          : 'bg-gray-800 border-gray-700 text-gray-100 hover:border-cyan-600/50'
                      }`}
                    >
                      {displayValue}
                      
                      {isAdded && (
                        <motion.div
                          initial={{ scale: 0.8, opacity: 1 }}
                          animate={{ scale: 1.3, opacity: 0 }}
                          transition={{ duration: 0.6 }}
                          className="absolute inset-0 border-2 border-cyan-400 rounded-md pointer-events-none"
                        />
                      )}
                    </motion.div>
                  );
                })
              )}
            </motion.div>

            {data.type === 'ArrayList' && (
              <div className="mt-2 text-xs text-gray-600">
                Capacity optimized for dynamic growth
              </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
};

export default ArrayListView;
