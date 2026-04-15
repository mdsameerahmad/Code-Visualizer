import sys
import os

# Add app path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from engine.executor import Executor


def run_test(name, func, expected_error=None):
    print(f"\n--- Running Test: {name} ---")
    try:
        steps, error = func()

        if expected_error:
            if error and expected_error in error.get("message", ""):
                print("✅ PASSED (Expected Error)")
            else:
                print(f"❌ FAILED: Expected '{expected_error}', got {error}")
        else:
            if error:
                print(f"❌ FAILED: {error}")
            else:
                print(f"✅ PASSED | Final: {steps[-1].variables}")

    except Exception as e:
        print(f"❌ CRASH: {e}")


# ================= TESTS ================= #

def test_factorial():
    executor = Executor()
    code = """
public class Test {
    public static int fact(int n) {
        if (n == 0) return 1;
        return n * fact(n - 1);
    }

    public static void main(String[] args) {
        int res = fact(4);
    }
}
"""
    return executor.execute(code)


def test_nested():
    executor = Executor()
    code = """
public class Test {
    public static int add(int a, int b) {
        return a + b;
    }

    public static int multiply(int x, int y) {
        return x * y;
    }

    public static void main(String[] args) {
        int res = add(2, multiply(3, 4));
    }
}
"""
    return executor.execute(code)


def test_array():
    executor = Executor()
    code = """
public class Test {
    public static int sumArr(int[] arr, int i) {
        if (i == 0) return arr[0];
        return arr[i] + sumArr(arr, i - 1);
    }

    public static void main(String[] args) {
        int[] arr = new int[3];
        arr[0] = 1;
        arr[1] = 2;
        arr[2] = 3;

        int res = sumArr(arr, 2);
    }
}
"""
    return executor.execute(code)


def test_error_args():
    executor = Executor()
    code = """
public class Test {
    public static int add(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        int res = add(5);
    }
}
"""
    return executor.execute(code)


# ================= RUN ================= #

if __name__ == "__main__":
    run_test("Factorial", test_factorial)
    run_test("Nested Calls", test_nested)
    run_test("Array Recursion", test_array)
    run_test("Wrong Args", test_error_args, "expected")