import { AnimatePresence, motion } from 'framer-motion';
import { useMemo } from 'react';

const HashMapView = ({ maps = {}, prevMaps = {} }) => {
  if (!maps || Object.keys(maps).length === 0) {
    return null;
  }

  const detectMapChanges = (name) => {
    const current = maps[name] || {};
    const prev = prevMaps?.[name] || {};

    const currMap = current.map || {};
    const prevMap = prev.map || {};

    const added = Object.keys(currMap).filter(k => !(k in prevMap));
    const updated = Object.keys(currMap).filter(k => k in prevMap && currMap[k] !== prevMap[k]);
    const removed = Object.keys(prevMap).filter(k => !(k in currMap));

    return { added, updated, removed, changed: added.length > 0 || updated.length > 0 || removed.length > 0 };
  };

  return (
    <div className="space-y-6">
      {Object.entries(maps).map(([name, data]) => {
        if (data.type !== 'HashMap') return null;

        const changes = detectMapChanges(name);
        const mapData = data.map || {};
        const entries = Object.entries(mapData);

        return (
          <motion.div
            key={name}
            layout
            className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                HashMap: <span className="text-purple-400">{name}</span>
              </h3>
              <span className="text-xs text-gray-500">
                entries: <span className={changes.changed ? 'text-purple-400 font-bold' : ''}>
                  {entries.length}
                </span>
              </span>
            </div>

            <motion.div layout className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {entries.length === 0 ? (
                <div className="text-gray-600 text-sm italic col-span-full">Empty HashMap</div>
              ) : (
                entries.map(([key, value]) => {
                  const isAdded = changes.added.includes(key);
                  const isUpdated = changes.updated.includes(key);
                  const displayValue = value === null || value === undefined ? '?' : value;

                  return (
                    <motion.div
                      key={`${name}-${key}`}
                      layout
                      initial={isAdded ? { scale: 0.8, opacity: 0, rotate: -10 } : {}}
                      animate={{ scale: 1, opacity: 1, rotate: 0 }}
                      exit={{ scale: 0.8, opacity: 0, rotate: 10 }}
                      transition={{ type: "spring", stiffness: 200, damping: 25 }}
                      className={`p-3 rounded-md border-2 transition-all ${
                        isAdded
                          ? 'bg-purple-600/40 border-purple-500 shadow-[0_0_20px_rgba(168,85,247,0.3)]'
                          : isUpdated
                          ? 'bg-orange-600/30 border-orange-500/60'
                          : 'bg-gray-800 border-gray-700 hover:border-purple-600/40'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="text-xs text-gray-400 font-mono truncate">
                          {key}
                        </div>
                        <div className="text-xs text-gray-500">→</div>
                        <motion.div
                          key={`${key}-${displayValue}`}
                          initial={isUpdated ? { scale: 1.2, opacity: 0.6 } : {}}
                          animate={{ scale: 1, opacity: 1 }}
                          className={`font-mono font-bold text-sm ${
                            isAdded || isUpdated
                              ? 'text-purple-300'
                              : displayValue === '?'
                              ? 'text-gray-500'
                              : 'text-gray-100'
                          }`}
                        >
                          {displayValue}
                        </motion.div>
                      </div>

                      {(isAdded || isUpdated) && (
                        <motion.div
                          initial={{ scale: 1, opacity: 0.8 }}
                          animate={{ scale: 1.2, opacity: 0 }}
                          transition={{ duration: 0.6 }}
                          className="absolute inset-0 border-2 border-purple-400 rounded-md pointer-events-none"
                        />
                      )}
                    </motion.div>
                  );
                })
              )}
            </motion.div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default HashMapView;
