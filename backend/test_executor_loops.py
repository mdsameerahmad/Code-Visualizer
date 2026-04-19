import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from engine.executor import Executor
from engine.exceptions import ExecutionError

def run_test(name, test_func):
    print(f"--- Running Test: {name} ---")
    try:
        test_func()
        print(f"--- Test '{name}' PASSED ---")
    except AssertionError as e:
        print(f"--- Test '{name}' FAILED: {e} ---")
    except ExecutionError as e:
        print(f"--- Test '{name}' FAILED with ExecutionError: {e.message} ---")
    except Exception as e:
        print(f"--- Test '{name}' FAILED with unexpected error: {type(e).__name__}: {e} ---")
    print("-" * 30)

def test_decrementing_for_loop():
    executor = Executor()
    code = """
int[] arr = new int[3];
for(int i = 2; i >= 0; i--) {
  arr[i] = arr[i] + 1;
}
"""
    steps = []
    try:
        steps, _, _ = executor.execute(code)
        final_arrays = steps[-1].arrays
        expected_array = [1, 1, 1]
        actual_array = final_arrays["arr"].values
        assert actual_array == expected_array, f"Expected {expected_array}, got {actual_array}"
    except ExecutionError as e:
        raise AssertionError(f"ExecutionError occurred: {e.message} at line {e.line}")
    except Exception as e:
        raise AssertionError(f"Unexpected error during execution: {e}")

def test_complex_for_loop_with_conditions():
    executor = Executor()
    code = """
int[] arr = new int[5];
for(int i = 4; i >= 0; i--) {
  if(i % 2 == 0) {
    arr[i] = i;
  } else {
    arr[i] = i * 2;
  }
}
"""
    steps = []
    try:
        steps, _, _ = executor.execute(code)
        final_arrays = steps[-1].arrays
        expected_array = [0, 2, 2, 6, 4]
        actual_array = final_arrays["arr"].values
        assert actual_array == expected_array, f"Expected {expected_array}, got {actual_array}"
    except ExecutionError as e:
        raise AssertionError(f"ExecutionError occurred: {e.message} at line {e.line}")
    except Exception as e:
        raise AssertionError(f"Unexpected error during execution: {e}")

if __name__ == "__main__":
    run_test("Decrementing For Loop with >= Condition", test_decrementing_for_loop)
    run_test("Complex For Loop with Conditions", test_complex_for_loop_with_conditions)
