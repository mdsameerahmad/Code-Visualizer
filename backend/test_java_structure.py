import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from engine.executor import Executor
from engine.exceptions import ExecutionError

def run_test(name, test_func, expected_error_message_part=None):
    print(f"--- Running Test: {name} ---")
    try:
        # Test functions now return steps, error_dict
        steps, error = test_func()
        
        if expected_error_message_part:
            if error and expected_error_message_part in error.get("message", ""):
                print(f"--- Test '{name}' PASSED (Expected Error: {error.get('message')}) ---")
            else:
                print(f"--- Test '{name}' FAILED: Expected error containing '{expected_error_message_part}', but got {'no error' if not error else error.get('message')} ---")
        else:
            if error:
                print(f"--- Test '{name}' FAILED with unexpected error: {error.get('type')}: {error.get('message')} ---")
            elif not steps:
                print(f"--- Test '{name}' FAILED: No steps generated ---")
            else:
                print(f"--- Test '{name}' PASSED ---")
    except AssertionError as e:
        print(f"--- Test '{name}' FAILED: {e} ---")
    except Exception as e:
        print(f"--- Test '{name}' FAILED with unexpected internal test error: {type(e).__name__}: {e} ---")
    print("-" * 30)

# Test Case 1: Valid Program - Simple Function
def test_valid_program_simple_function():
    executor = Executor()
    code = """
public class Test {
    public static void main(String[] args) {
        int result = add(2, 3);
    }

    public static int add(int a, int b) {
        return a + b;
    }
}
"""
    steps, error = executor.execute(code)
    if not error:
        final_variables = steps[-1].variables
        assert final_variables.get("result") == 5, f"Expected result to be 5, got {final_variables.get('result')}"
    return steps, error

# Test Case 2: Recursion - Factorial inside class
def test_recursion_factorial():
    executor = Executor()
    code = """
public class Factorial {
    public static void main(String[] args) {
        int res = fact(3); // Expected: 3 * 2 * 1 = 6
    }

    public static int fact(int n) {
        if (n == 0) return 1;
        return n * fact(n - 1);
    }
}
"""
    steps, error = executor.execute(code)
    if not error:
        final_variables = steps[-1].variables
        assert final_variables.get("res") == 6, f"Expected res to be 6, got {final_variables.get('res')}"
    return steps, error

# Test Case 3: Invalid Case - No class
def test_no_class():
    executor = Executor()
    code = """
int x = 10;
"""
    steps, error = executor.execute(code)
    return steps, error

# Test Case 4: Invalid Case - No main method
def test_no_main_method():
    executor = Executor()
    code = """
public class MyClass {
    public static int someMethod() {
        return 1;
    }
}
"""
    steps, error = executor.execute(code)
    return steps, error

# Test Case 5: Invalid Case - Private method called outside (from main)
def test_private_method_called_outside():
    executor = Executor()
    code = """
public class MyClass {
    public static void main(String[] args) {
        int x = privateMethod();
    }

    private static int privateMethod() {
        return 10;
    }
}
"""
    steps, error = executor.execute(code)
    return steps, error

# Test Case 6: Invalid Case - Non-static method called from static context (main)
def test_non_static_call_in_static():
    executor = Executor()
    code = """
public class MyClass {
    public static void main(String[] args) {
        int x = nonStaticMethod();
    }

    public int nonStaticMethod() {
        return 20;
    }
}
"""
    steps, error = executor.execute(code)
    return steps, error

if __name__ == "__main__":
    run_test("Valid Program - Simple Function", test_valid_program_simple_function)
    run_test("Recursion - Factorial", test_recursion_factorial)
    run_test("Invalid Case - No Class", test_no_class, expected_error_message_part="No public class found")
    run_test("Invalid Case - No Main Method", test_no_main_method, expected_error_message_part="Missing public static void main(String[] args) method")
    run_test("Invalid Case - Private Method Called Outside", test_private_method_called_outside, expected_error_message_part="Private method 'privateMethod' cannot be accessed from main method")
    run_test("Invalid Case - Non-static Call in Static", test_non_static_call_in_static, expected_error_message_part="Non-static method 'nonStaticMethod' cannot be called from a static context")