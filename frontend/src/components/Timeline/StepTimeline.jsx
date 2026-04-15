import useExecutionStore from '../../store/executionStore';

const StepTimeline = ({ step }) => {
  const { currentStepIndex, steps } = useExecutionStore();
  
  if (!step || !step.line_content) return null;

  const prevStep = currentStepIndex > 0 ? steps[currentStepIndex - 1] : null;
  
  let dynamicExplanation = step.explanation || "Executing code...";
  if (prevStep) {
    if (step.call_stack.length > prevStep.call_stack.length) {
      dynamicExplanation = `Calling function: ${step.call_stack[0].method_name}`;
    } else if (step.call_stack.length < prevStep.call_stack.length) {
      dynamicExplanation = `Returning from: ${prevStep.call_stack[0].method_name}`;
    }
  }

  return (
    <div className="p-4 bg-gray-900 rounded-lg border border-gray-800">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
          Current Step
        </h3>
        <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-400 text-xs rounded border border-indigo-500/30 font-mono">
          Line {step.line_number}
        </span>
      </div>
      
      <div className="space-y-4">

        {/* 🔥 REAL OUTPUT */}
        {step.type === "print" && step.output !== null && (
          <div className="p-3 bg-green-900/30 border border-green-500/30 rounded">
            <p className="text-green-400 font-mono text-sm">
              Output: {step.output}
            </p>
          </div>
        )}

        {/* ✅ ONLY SHOW EXPLANATION FOR NON-PRINT */}
        {step.type !== "print" && (
          <div className="p-3 bg-gray-800 rounded border border-gray-700">
            <p className="text-sm text-indigo-300 font-mono font-medium">
              {dynamicExplanation}
            </p>
          </div>
        )}
        
        {/* Executing Code */}
        <div className="p-3 bg-gray-950 rounded border border-gray-800 font-mono text-xs">
          <div className="text-gray-500 mb-1">// Executing:</div>
          <div className="text-green-400">{step.line_content}</div>
        </div>

      </div>
    </div>
  );
};

export default StepTimeline;