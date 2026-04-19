import { useState } from 'react';
import { executeCode as apiExecuteCode } from '../services/api';
import useExecutionStore from '../store/executionStore';

export const useExecution = (setCode) => {
  const [isLoading, setIsLoading] = useState(false);
  const { setSteps, setError } = useExecutionStore();

  const runCode = async (code) => {
    setIsLoading(true);
    setError(null);
    setSteps([]);
    
    try {
      const data = await apiExecuteCode(code);
      
      if (data.normalized_code && setCode) {
        setCode(data.normalized_code);
      }

      if (data.error) {
        setError(data.error);
        if (data.steps && data.steps.length > 0) {
          setSteps(data.steps);
        }
        return;
      }
      
      setError(null);
      setSteps(data.steps);
    } catch (err) {
      setError({
        type: 'NetworkError',
        message: 'Failed to connect to server',
        line: 0
      });
    } finally {
      setIsLoading(false);
    }
  };

  return { runCode, isLoading };
};
