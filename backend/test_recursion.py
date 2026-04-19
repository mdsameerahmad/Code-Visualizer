
from app.engine.executor import Executor

def test_factorial():
    code = """
    public class MathUtils {
        public static int factorial(int n) {
            if (n <= 1) {
                return 1;
            }
            return n * factorial(n - 1);
        }

        public static void main(String[] args) {
            int result = factorial(3);
        }
    }
    """
    executor = Executor()
    steps, _, error = executor.execute(code)

    if error:
        print(f"Error: {error}")
    else:
        print(f"Success! Total steps: {len(steps)}")
        # Check if we have steps for n=3, n=2, n=1
        for step in steps:
            print(f"Step {step.step_number}: Line {step.line_number} - {step.line_content} - {step.explanation}")
        
        # Verify the final result
        last_step = steps[-1]
        print(f"Last step explanation: {last_step.explanation}")
        
        # Check frames in a recursive step
        recursive_step = next((s for s in steps if "factorial(2)" in s.line_content), None)
        if recursive_step:
             print(f"Found recursive call step: {recursive_step.line_content}")

if __name__ == "__main__":
    test_factorial()
