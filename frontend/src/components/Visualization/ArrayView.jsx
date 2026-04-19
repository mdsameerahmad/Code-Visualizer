import { AnimatePresence, motion } from 'framer-motion';
import useExecutionStore from '../../store/executionStore';

const ArrayView = ({ arrays, prevArrays = {}, error = null }) => {
  const { steps, currentStepIndex } = useExecutionStore();
  const currentStep = steps[currentStepIndex];
  
  if (!arrays || Object.keys(arrays).length === 0) {
    return null;
  }

  const detectArrayError = () => {
    // Check global error
    if (error && (error.type?.includes('OutOfBounds') || error.message?.includes('bounds'))) {
      const index = parseInt(error.message) || null;
      return { type: error.type, message: `Index ${index} out of bounds`, index };
    }
    
    // Check current step explanation (backend explicitly sets this for OOB)
    if (currentStep?.explanation?.includes('OUT OF BOUNDS')) {
      const indexMatch = currentStep.explanation.match(/index (-?\d+)/i);
      const index = indexMatch ? parseInt(indexMatch[1]) : null;
      return { type: 'ArrayIndexOutOfBoundsException', message: currentStep.explanation, index };
    }

    return null;
  };

  const arrayError = detectArrayError();

  return (
    <div className="space-y-12">
      {Object.entries(arrays).map(([name, data]) => {
        const values = data.values || [];
        const lastUpdatedIdx = data.lastUpdatedIndex;
        const isAccessedArray = currentStep?.accessed_array_name === name;
        const accessedIdx = isAccessedArray ? currentStep?.accessed_array_index : null;

        const hasError = !!arrayError;
        const errorIdx = hasError ? arrayError.index : null;

        return (      
          <div key={name} className="flex flex-col">
            <h3 className="text-sm font-bold text-gray-400 mb-6 uppercase tracking-widest border-l-4 border-indigo-500 pl-3">
              Array: <span className="text-white">{name}</span>
            </h3>

            <div className="relative flex items-center">
              {/* Main Array Container */}
              <div className="flex flex-col">
                {/* Value Boxes */}
                <div className="flex items-end">
                  {values.map((val, idx) => {
                    const isBeingAccessed = accessedIdx === idx;
                    const isBeingUpdated = lastUpdatedIdx === idx;
                    const isError = hasError && errorIdx === idx;

                    return (
                      <motion.div
                        key={`${name}-val-${idx}`}
                        layout
                        className={`w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center border-2 text-xl font-bold font-mono transition-colors relative
                          ${isError ? 'bg-red-950 border-red-500 text-red-200' : 
                            isBeingUpdated ? 'bg-green-900/40 border-green-500 text-green-100 shadow-[0_0_15px_rgba(34,197,94,0.3)]' :
                            isBeingAccessed ? 'bg-indigo-900/40 border-indigo-500 text-indigo-100' :
                            'bg-gray-900 border-gray-700 text-gray-300'}
                        `}
                      >
                        <AnimatePresence mode="wait">
                          <motion.span
                            key={val}
                            initial={{ scale: 0.5, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.5, opacity: 0 }}
                          >
                            {val === null || val === undefined ? '0' : val}
                          </motion.span>
                        </AnimatePresence>

                        {/* Traversal Arrow */}
                        {isBeingAccessed && (
                          <motion.div
                            initial={{ y: -20, opacity: 0 }}
                            animate={{ y: -45, opacity: 1 }}
                            className="absolute text-indigo-400 text-2xl font-bold"
                          >
                            ↓
                          </motion.div>
                        )}
                      </motion.div>
                    );
                  })}
                  
                  {/* OOB Error Box (Extended) */}
                  {hasError && errorIdx !== null && (errorIdx >= values.length || errorIdx < 0) && (
                    <motion.div
                      initial={{ scale: 0, x: -20 }}
                      animate={{ scale: 1, x: 0 }}
                      className="flex flex-col items-center ml-2"
                    >
                      <motion.div
                        animate={{ borderColor: ['#ef4444', '#dc2626', '#ef4444'], boxShadow: ['0 0 0px rgba(239,68,68,0)', '0 0 30px rgba(239,68,68,0.6)', '0 0 0px rgba(239,68,68,0)'] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                        className="w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center border-4 border-dashed border-red-600 bg-red-950/60 text-red-400 text-2xl font-black font-mono relative"
                      >
                        !
                        {/* Traversal Arrow for OOB */}
                        <motion.div
                          animate={{ y: [-45, -55, -45] }}
                          transition={{ duration: 0.5, repeat: Infinity }}
                          className="absolute text-red-500 text-3xl font-bold"
                        >
                          ↓
                        </motion.div>
                      </motion.div>
                      <div className="w-14 h-8 sm:w-16 sm:h-8 flex items-center justify-center font-mono font-bold text-sm bg-red-600 text-white mt-1 shadow-lg shadow-red-900/50">
                        {errorIdx}
                      </div>
                    </motion.div>
                  )}
                </div>

                {/* Indices Row */}
                <div className="flex mt-1 items-start">
                  {values.map((_, idx) => (
                    <div
                      key={`${name}-idx-${idx}`}
                      className={`w-14 h-8 sm:w-16 sm:h-8 flex items-center justify-center font-mono font-bold text-sm
                        ${accessedIdx === idx ? 'bg-indigo-600 text-white' : 'bg-green-700 text-green-50'}
                      `}
                    >
                      {idx}
                    </div>
                  ))}
                  <div className="ml-4 flex items-center text-[10px] font-black text-gray-500 uppercase tracking-tighter pt-2">
                    ← Array Indices
                  </div>
                </div>

                {/* Metadata Labels */}
                <div className="mt-6 grid grid-cols-1 gap-1 text-sm font-mono">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500 font-bold">Array Length =</span>
                    <span className="text-white font-bold">{values.length}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500 font-bold">First Index =</span>
                    <span className="text-white font-bold">0</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500 font-bold">Last Index =</span>
                    <span className="text-white font-bold">{values.length - 1}</span>
                  </div>
                </div>
              </div>
            </div>

            {hasError && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-4 p-3 bg-red-950/40 border border-red-900 rounded text-red-200 text-xs font-mono"
              >
                <strong>{arrayError.type}:</strong> {arrayError.message}
              </motion.div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default ArrayView;
