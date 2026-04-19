import { useState } from 'react';
import PlayControls from '../components/Controls/PlayControls';
import CodeEditor from '../components/Editor/CodeEditor';
import RunButton from '../components/Editor/RunButton';
import StepTimeline from '../components/Timeline/StepTimeline';
import ArrayView from '../components/Visualization/ArrayView';
import ErrorBox from '../components/Visualization/ErrorBox';
import MemoryView from '../components/Visualization/MemoryView';
import { useExecution } from '../hooks/useExecution';
import { usePlayback } from '../hooks/usePlayback';
import useExecutionStore from '../store/executionStore';

const Home = () => {
  const [code, setCode] = useState(`public class MathUtils {
    public static int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }

    public static void main(String[] args) {
        int result = factorial(3);
    }
}`);
  const { runCode, isLoading } = useExecution(setCode);
  const { currentStepIndex, steps, error, outputHistory } = useExecutionStore();
  usePlayback();

  const currentStep = steps[currentStepIndex];

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-gray-900 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-indigo-600 rounded flex items-center justify-center font-bold text-lg">C</div>
          <h1 className="text-xl font-bold tracking-tight">CodeVista</h1>
        </div>
        <RunButton onClick={() => runCode(code)} isLoading={isLoading} />
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left: Editor */}
        <div className="w-1/2 p-4 flex flex-col gap-4 border-r border-gray-800">
          <div className="flex-1 relative">
            <CodeEditor 
              code={code} 
              onChange={setCode} 
              errorLine={error?.line} 
              currentLine={currentStep?.line_number}
            />
          </div>
        </div>

        {/* Right: Visualization */}
        <div className="w-1/2 flex flex-col bg-gray-950 overflow-y-auto">
          <div className="p-6 space-y-8 pb-20">
            {error ? (
              <ErrorBox error={error} />
            ) : (
              <>
                {currentStep && <StepTimeline step={currentStep} />}

                {currentStep && (
                  <MemoryView variables={currentStep.variables} arrays={currentStep.arrays} />
                )}
                {currentStep && (
                  <ArrayView
                    arrays={currentStep.arrays}
                    prevArrays={steps[currentStepIndex - 1]?.arrays}
                    error={error}
                  />
                )}
                
                {outputHistory.length > 0 && (
                  <div className="p-4 bg-gray-900 rounded-lg border border-gray-800">
                    <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
                      Output
                    </h3>
                    <div className="bg-gray-800 p-3 rounded font-mono text-sm text-gray-100 max-h-40 overflow-y-auto">
                      {outputHistory.map((output, index) => (
                        <p key={index}>{output}</p>
                      ))}
                    </div>
                  </div>
                )}

                {!currentStep && !isLoading && (
                  <div className="flex flex-col items-center justify-center py-20 text-gray-500">
                    <p>No execution data yet.</p>
                    <p className="text-sm">Click "Run Code" to see visualization.</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>

      {/* Bottom: Controls */}
      <PlayControls />
    </div>
  );
};

export default Home;
