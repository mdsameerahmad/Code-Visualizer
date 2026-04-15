import { AnimatePresence, motion } from 'framer-motion';
import useExecutionStore from '../../store/executionStore';

const MemoryView = ({ variables }) => {
  const { currentStepIndex, steps } = useExecutionStore();

  if (!variables || Object.entries(variables).length === 0) return null;

  const currentStep = steps[currentStepIndex];
  const heap = currentStep?.heap || {}; // ✅ heap snapshot

  const prevStep = currentStepIndex > 0 ? steps[currentStepIndex - 1] : null;
  const prevVariables = prevStep ? prevStep.variables : {};

  // ✅ FINAL RESOLVER (FIXED)
  const resolveValue = (value) => {
    // Array
    if (value && typeof value === 'object' && 'values' in value) {
      return '[Array]';
    }

    // ✅ Object reference (heap)
    if (typeof value === 'number' && heap && heap[String(value)]) {
      const obj = heap[String(value)];

      const className = obj.class || obj.class_name || 'Object';
      const fields = obj.fields || {};

      return `${className} ${JSON.stringify(fields)}`;
    }

    // HashMap
    if (typeof value === 'object' && value !== null) {
      if (value.type === 'HashMap') {
        return JSON.stringify(value.map);
      }
      return JSON.stringify(value, null, 2);
    }

    return String(value);
  };

  return (
    <div className="p-4 bg-gray-900 rounded-lg border border-gray-800">
      <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
        Local Variables
      </h3>

      <div className="space-y-2">
        {Object.entries(variables).map(([name, value]) => {
          const displayValue = resolveValue(value);

          const isChanged =
            prevVariables[name] !== undefined &&
            JSON.stringify(prevVariables[name]) !== JSON.stringify(value);

          const isNew = prevVariables[name] === undefined;

          return (
            <motion.div
              key={name}
              animate={{
                backgroundColor: isChanged
                  ? 'rgba(99, 102, 241, 0.2)'
                  : isNew
                  ? 'rgba(34, 197, 94, 0.1)'
                  : 'rgba(31, 41, 55, 0.5)',
              }}
              className={`flex items-center justify-between py-2 px-3 rounded border ${
                isChanged
                  ? 'border-indigo-500/50'
                  : isNew
                  ? 'border-green-500/30'
                  : 'border-gray-700'
              }`}
            >
              <span
                className={`${
                  isChanged
                    ? 'text-indigo-300'
                    : isNew
                    ? 'text-green-400'
                    : 'text-gray-400'
                } font-mono`}
              >
                {name}
              </span>

              <AnimatePresence mode="wait">
                <motion.span
                  key={displayValue}
                  initial={{ scale: 1.2, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="font-mono text-gray-100 text-right max-w-[250px] truncate"
                >
                  {displayValue}
                </motion.span>
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default MemoryView;