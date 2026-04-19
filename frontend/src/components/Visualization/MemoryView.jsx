import { AnimatePresence, motion } from 'framer-motion';
import useExecutionStore from '../../store/executionStore';

const isArrayLike = (value) =>
  value &&
  typeof value === 'object' &&
  ('values' in value || value.type === 'array');

const inferKind = (value) => {
  if (value === null || value === undefined) return 'null';
  if (typeof value === 'boolean') return 'boolean';
  if (typeof value === 'number') {
    return Number.isInteger(value) ? 'int' : 'double';
  }
  if (typeof value === 'string') return 'String';
  if (isArrayLike(value)) return 'array';
  if (typeof value === 'object' && value.type === 'HashMap') return 'HashMap';
  if (typeof value === 'object') return 'object';
  return typeof value;
};

const MemoryView = ({ variables, arrays = null }) => {
  const { currentStepIndex, steps } = useExecutionStore();

  if (!variables || Object.entries(variables).length === 0) return null;

  const currentStep = steps[currentStepIndex];
  const heap = currentStep?.heap || {};

  const prevStep = currentStepIndex > 0 ? steps[currentStepIndex - 1] : null;
  const prevVariables = prevStep ? prevStep.variables : {};

  const resolveValue = (value) => {
    if (isArrayLike(value)) {
      return '[Array]';
    }

    if (typeof value === 'number' && heap && heap[String(value)]) {
      const obj = heap[String(value)];
      const className = obj.class || obj.class_name || 'Object';
      const fields = obj.fields || {};
      return `${className} ${JSON.stringify(fields)}`;
    }

    if (typeof value === 'object' && value !== null) {
      if (value.type === 'HashMap') {
        return JSON.stringify(value.map);
      }
      return JSON.stringify(value, null, 2);
    }

    return String(value);
  };

  const entries = Object.entries(variables).filter(([name, value]) => {
    if (!arrays || !arrays[name]) return true;
    if (isArrayLike(value)) return false;
    if (value && typeof value === 'object' && value.type === 'arraylist') return false;
    return true;
  });

  if (entries.length === 0) return null;

  return (
    <div className="p-4 bg-gray-900 rounded-lg border border-gray-800 border-l-4 border-l-emerald-600">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-gray-300 uppercase tracking-widest">
          Variables
        </h3>
        <p className="text-xs text-gray-500 mt-1">
          Scalars and references update on every step (same idea as array length / index hints).
        </p>
      </div>

      <div className="space-y-2">
        {entries.map(([name, value]) => {
          const displayValue = resolveValue(value);
          const kind = inferKind(value);

          const isChanged =
            prevVariables[name] !== undefined &&
            JSON.stringify(prevVariables[name]) !== JSON.stringify(value);

          const isNew = prevVariables[name] === undefined;

          return (
            <motion.div
              key={name}
              layout
              animate={{
                backgroundColor: isChanged
                  ? 'rgba(99, 102, 241, 0.18)'
                  : isNew
                  ? 'rgba(34, 197, 94, 0.12)'
                  : 'rgba(31, 41, 55, 0.45)',
              }}
              className={`rounded-lg border overflow-hidden ${
                isChanged
                  ? 'border-indigo-500/45'
                  : isNew
                  ? 'border-green-500/35'
                  : 'border-gray-700/80'
              }`}
            >
              <div className="flex items-center justify-between gap-3 px-3 py-2 border-b border-gray-800/80 bg-gray-950/40">
                <span
                  className={`font-mono text-sm font-semibold ${
                    isChanged ? 'text-indigo-200' : isNew ? 'text-green-400' : 'text-gray-200'
                  }`}
                >
                  {name}
                </span>
                <span className="text-[10px] uppercase tracking-wider text-gray-500 font-mono">
                  {kind}
                </span>
              </div>
              <div className="px-3 py-3 flex items-center justify-between gap-2">
                <div className="text-[11px] text-gray-500 uppercase tracking-tight shrink-0">
                  value
                </div>
                <AnimatePresence mode="wait">
                  <motion.span
                    key={displayValue}
                    initial={{ scale: 1.08, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="font-mono text-lg sm:text-xl text-emerald-100 text-right font-semibold tabular-nums break-all"
                  >
                    {displayValue}
                  </motion.span>
                </AnimatePresence>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default MemoryView;
