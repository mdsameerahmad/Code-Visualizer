import { motion } from 'framer-motion';
import { ArrowDownToLine, ArrowRightToLine, ArrowUpToLine, Pause, Play, RotateCcw, SkipBack, SkipForward } from 'lucide-react';
import useExecutionStore from '../../store/executionStore';

const PlayControls = () => {
  const { 
    isPlaying, 
    setIsPlaying, 
    nextStep, 
    prevStep, 
    stepInto,
    stepOver,
    stepOut,
    currentStepIndex, 
    steps,
    reset 
  } = useExecutionStore();

  const isAtStart = currentStepIndex === 0;
  const isAtEnd = steps.length === 0 || currentStepIndex === steps.length - 1;

  return (
    <div className="flex items-center gap-4 p-4 bg-gray-900 border-t border-gray-800">
      <div className="flex items-center gap-2">
        <button
          onClick={reset}
          className="p-2 hover:bg-gray-800 rounded-full text-gray-400 transition-colors"
          title="Reset"
        >
          <RotateCcw className="w-5 h-5" />
        </button>
        <button
          onClick={prevStep}
          disabled={isAtStart}
          className="p-2 hover:bg-gray-800 disabled:opacity-30 rounded-full text-gray-200 transition-colors"
          title="Previous Step"
        >
          <SkipBack className="w-5 h-5 fill-current" />
        </button>
        
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-3 bg-indigo-600 hover:bg-indigo-700 rounded-full text-white transition-all shadow-lg"
          title={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? <Pause className="w-6 h-6 fill-current" /> : <Play className="w-6 h-6 fill-current" />}
        </button>

        <button
          onClick={nextStep}
          disabled={isAtEnd}
          className="p-2 hover:bg-gray-800 disabled:opacity-30 rounded-full text-gray-200 transition-colors"
          title="Next Step"
        >
          <SkipForward className="w-5 h-5 fill-current" />
        </button>

        <div className="h-8 w-px bg-gray-800 mx-2" />

        <button
          onClick={stepInto}
          disabled={isAtEnd}
          className="p-2 hover:bg-gray-800 disabled:opacity-30 rounded text-indigo-400 transition-colors"
          title="Step Into"
        >
          <ArrowDownToLine className="w-5 h-5" />
        </button>

        <button
          onClick={stepOver}
          disabled={isAtEnd}
          className="p-2 hover:bg-gray-800 disabled:opacity-30 rounded text-indigo-400 transition-colors"
          title="Step Over"
        >
          <ArrowRightToLine className="w-5 h-5" />
        </button>

        <button
          onClick={stepOut}
          disabled={isAtEnd}
          className="p-2 hover:bg-gray-800 disabled:opacity-30 rounded text-indigo-400 transition-colors"
          title="Step Out"
        >
          <ArrowUpToLine className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 px-4">
        <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-indigo-500"
            initial={{ width: 0 }}
            animate={{ width: `${steps.length > 1 ? (currentStepIndex / (steps.length - 1)) * 100 : (steps.length === 1 ? 100 : 0)}%` }}
          />
        </div>
      </div>

      <div className="text-sm font-mono text-gray-400 min-w-[80px]">
        Step {steps.length > 0 ? currentStepIndex + 1 : 0} / {steps.length}
      </div>
    </div>
  );
};

export default PlayControls;
