import { AnimatePresence, motion } from 'framer-motion';
import useExecutionStore from '../../store/executionStore';

const CallStackView = ({ stack }) => {
  const { setCurrentStepIndex, steps, currentStepIndex } = useExecutionStore();
  
  if (!stack || stack.length === 0) return null;

  const handleFrameClick = (frameIndex) => {
    // Reverse the stack index because it's rendered reversed (index 0 is top)
    // Actually the mapping is index 0 is top of stack in the array provided by backend? 
    // Let's check backend: `reversed(self._frames)` in get_frames_info. 
    // So index 0 is indeed the top of the stack (most recent).
    
    // We want to find the most recent step (up to currentStepIndex) 
    // where the stack depth was exactly (stack.length - frameIndex) 
    // and the method name matches.
    const targetDepth = stack.length - frameIndex;
    const targetMethod = stack[frameIndex].method_name;

    for (let i = currentStepIndex; i >= 0; i--) {
      const stepStack = steps[i].call_stack;
      if (stepStack.length === targetDepth && stepStack[0].method_name === targetMethod) {
        setCurrentStepIndex(i);
        break;
      }
    }
  };

  return (
    <div className="p-4 bg-gray-900 rounded-lg border border-gray-800">
      <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">
        Call Stack
      </h3>
      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {stack.map((frame, index) => (
            <motion.div
              key={`${frame.method_name}-${stack.length - index}`}
              layout
              initial={{ y: 10, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 10, opacity: 0 }}
              onClick={() => handleFrameClick(index)}
              className={`flex items-center justify-between p-3 rounded border font-mono text-sm cursor-pointer transition-all ${
                index === 0 
                  ? "bg-indigo-600/20 border-indigo-500 text-indigo-100 ring-1 ring-indigo-500/30" 
                  : "bg-gray-800/50 border-gray-700 text-gray-400 hover:bg-gray-800"
              }`}
            >
              <div className="flex flex-col">
                <span className="font-bold">{frame.method_name}</span>
                <span className="text-[10px] text-gray-500">{frame.class_name}</span>
              </div>
              <div className="flex flex-col items-end gap-1">
                 {frame.parameters && Object.entries(frame.parameters).length > 0 && (
                   <div className="flex gap-2">
                     {Object.entries(frame.parameters).map(([k, v]) => {
                       const displayVal = (v && typeof v === 'object' && 'values' in v) ? '[Array]' : String(v);
                       return (
                         <span key={k} className="px-1.5 py-0.5 bg-gray-950/50 rounded text-[10px] text-indigo-300">
                           {k}={displayVal}
                         </span>
                       );
                     })}
                   </div>
                 )}
                 {index === 0 && <span className="text-[10px] text-indigo-400 uppercase font-bold tracking-tighter">Current</span>}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default CallStackView;
