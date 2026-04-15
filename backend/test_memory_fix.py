import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.engine.memory import Memory
from app.engine.exceptions import ExecutionError

print(f"ID of ExecutionError in test_memory_fix.py: {id(ExecutionError)}")

def run_test(name, test_func, expected_exception=None):
    print(f"--- Running Test: {name} ---")
    try:
        test_func()
        if expected_exception:
            print(f"--- Test '{name}' FAILED: Expected {expected_exception.__name__} but no exception was raised ---")
        else:
            print(f"--- Test '{name}' PASSED ---")
    except ExecutionError as e:
        if expected_exception == ExecutionError:
            print(f"--- Test '{name}' PASSED (Expected ExecutionError: {e.message}) ---")
        else:
            print(f"--- Test '{name}' FAILED with ExecutionError: {e.message} (Caught ID: {id(type(e))}) ---")
    except AssertionError as e:
        print(f"--- Test '{name}' FAILED: {e} ---")
    except Exception as e:
        print(f"--- Test '{name}' FAILED with unexpected error: {type(e).__name__}: {e} (Caught ID: {id(type(e))}) ---")
    print("-" * 30)

# Test 1: Array initialization with 0
def test_initialization():
    memory = Memory()
    memory.create_array("arr", 2)
    snapshot = memory.get_snapshot()
    assert snapshot["arrays"]["arr"]["values"] == [0, 0], f"Expected [0, 0], got {snapshot['arrays']['arr']['values']}"

# Test 2: Array assignment and sum
def test_assignment_and_sum():
    memory = Memory()
    memory.create_array("arr", 2)
    
    # Simulate loop: for(int i = 0; i < 2; i++) { arr[1] = arr[1] + 5; }
    memory.set_array_value("arr", 1, memory.arrays["arr"]["values"][1] + 5) # First iteration
    memory.set_array_value("arr", 1, memory.arrays["arr"]["values"][1] + 5) # Second iteration
    
    snapshot = memory.get_snapshot()
    assert snapshot["arrays"]["arr"]["values"] == [0, 10], f"Expected [0, 10], got {snapshot['arrays']['arr']['values']}"

# Test 3: Array assignment with loop
def test_loop_assignment():
    memory = Memory()
    memory.create_array("arr", 3)
    
    # Simulate loop: for(int i = 0; i < 3; i++) { arr[i] = arr[i] + 1; }
    for i in range(3):
        memory.set_array_value("arr", i, memory.arrays["arr"]["values"][i] + 1)
    
    snapshot = memory.get_snapshot()
    assert snapshot["arrays"]["arr"]["values"] == [1, 1, 1], f"Expected [1, 1, 1], got {snapshot['arrays']['arr']['values']}"

# Test 4: Index out of bounds
def test_index_out_of_bounds():
    memory = Memory()
    memory.create_array("arr", 2)
    memory.set_array_value("arr", 2, 10) # This should raise ExecutionError

# Test 5: Non-integer index
def test_non_integer_index():
    memory = Memory()
    memory.create_array("arr", 2)
    memory.set_array_value("arr", "1", 10) # This should raise ExecutionError

# Test 6: Non-integer value
def test_non_integer_value():
    memory = Memory()
    memory.create_array("arr", 2)
    memory.set_array_value("arr", 0, "hello") # This should raise ExecutionError

# Test 7: None value assignment (should convert to 0)
def test_none_value_assignment():
    memory = Memory()
    memory.create_array("arr", 2)
    memory.set_array_value("arr", 0, None)
    snapshot = memory.get_snapshot()
    assert snapshot["arrays"]["arr"]["values"] == [0, 0], f"Expected [0, 0], got {snapshot['arrays']['arr']['values']}"


if __name__ == "__main__":
    run_test("Initialization with 0", test_initialization)
    run_test("Assignment and Sum", test_assignment_and_sum)
    run_test("Loop Assignment", test_loop_assignment)
    run_test("Index Out of Bounds", test_index_out_of_bounds, expected_exception=ExecutionError)
    run_test("Non-Integer Index", test_non_integer_index, expected_exception=ExecutionError)
    run_test("Non-Integer Value", test_non_integer_value, expected_exception=ExecutionError)
    run_test("None Value Assignment (should convert to 0)", test_none_value_assignment)
