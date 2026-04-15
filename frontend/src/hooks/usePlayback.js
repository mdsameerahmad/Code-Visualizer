import { useEffect, useRef } from 'react';
import useExecutionStore from '../store/executionStore';

export const usePlayback = () => {
  const { isPlaying, nextStep, currentStepIndex, steps, speed } = useExecutionStore();
  const timerRef = useRef(null);

  useEffect(() => {
    if (isPlaying && currentStepIndex < steps.length - 1) {
      timerRef.current = setInterval(() => {
        nextStep();
      }, speed);
    } else {
      clearInterval(timerRef.current);
    }

    return () => clearInterval(timerRef.current);
  }, [isPlaying, currentStepIndex, steps.length, speed, nextStep]);

  return { isPlaying, currentStepIndex, steps };
};
