import { create } from 'zustand';

const useExecutionStore = create((set, get) => ({
  steps: [],
  currentStepIndex: 0,
  isPlaying: false,
  speed: 1000,
  error: null,
  breakpoints: new Set(),

  setSteps: (steps) => set({ steps, currentStepIndex: 0, error: null }),
  setCurrentStepIndex: (index) => set({ currentStepIndex: index }),
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  setSpeed: (speed) => set({ speed }),
  setError: (error) => set({ error, steps: [], currentStepIndex: 0, isPlaying: false }),
  
  toggleBreakpoint: (line) => set((state) => {
    const newBreakpoints = new Set(state.breakpoints);
    if (newBreakpoints.has(line)) newBreakpoints.delete(line);
    else newBreakpoints.add(line);
    return { breakpoints: newBreakpoints };
  }),

  nextStep: () => {
    const { currentStepIndex, steps, isPlaying, breakpoints } = get();
    if (currentStepIndex >= steps.length - 1) {
      set({ isPlaying: false });
      return;
    }
    const nextIndex = currentStepIndex + 1;
    if (isPlaying && breakpoints.has(steps[nextIndex].line_number)) {
      set({ isPlaying: false });
    }
    set({ currentStepIndex: nextIndex });
  },
  
  prevStep: () => set((state) => ({ 
    currentStepIndex: Math.max(state.currentStepIndex - 1, 0) 
  })),

  stepInto: () => get().nextStep(),

  stepOver: () => {
    const { steps, currentStepIndex } = get();
    if (currentStepIndex >= steps.length - 1) return;
    const currentDepth = steps[currentStepIndex].call_stack.length;
    let nextIdx = currentStepIndex + 1;
    while (nextIdx < steps.length - 1 && steps[nextIdx].call_stack.length > currentDepth) {
      nextIdx++;
    }
    set({ currentStepIndex: nextIdx });
  },

  stepOut: () => {
    const { steps, currentStepIndex } = get();
    if (currentStepIndex >= steps.length - 1) return;
    const currentDepth = steps[currentStepIndex].call_stack.length;
    let nextIdx = currentStepIndex + 1;
    while (nextIdx < steps.length - 1 && steps[nextIdx].call_stack.length >= currentDepth) {
      nextIdx++;
    }
    set({ currentStepIndex: nextIdx });
  },

  reset: () => set({ steps: [], currentStepIndex: 0, isPlaying: false, breakpoints: new Set() }),
}));

export default useExecutionStore;
