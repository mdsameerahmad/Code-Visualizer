from app.engine.executor import Executor

def run_test(name, code, expected_array_name, expected_values):
    print(f"\n--- Running Test: {name} ---")
    executor = Executor()
    steps, error = executor.execute(code)
    
    if error:
        print(f"Error: {error.message}")
        return False
        
    final_step = steps[-1]
    actual_values = final_step.arrays[expected_array_name].values
    print(f"Result for {expected_array_name}: {actual_values}")
    
    if actual_values == expected_values:
        print(f"PASSED: {name}")
        return True
    else:
        print(f"FAILED: {name}. Expected {expected_values}, got {actual_values}")
        return False

def test_dynamic_parsing():
    all_passed = True
    
    # Test 1: Dynamic array and variable names (nums, j)
    code1 = """
int[] nums = new int[3];
for(int j = 0; j < 3; j++) {
  nums[j] = j * 2;
}
"""
    all_passed &= run_test("Dynamic names (nums, j)", code1, "nums", [0, 2, 4])
    
    # Test 2: Different names and expression (data, k)
    code2 = """
int[] data = new int[2];
for(int k = 0; k < 2; k++) {
  data[k] = data[k] + 5;
}
"""
    all_passed &= run_test("Dynamic names (data, k)", code2, "data", [5, 5])
    
    # Test 3: If-else with dynamic names (x, a)
    code3 = """
int[] x = new int[3];
for(int a = 0; a < 3; a++) {
  if(a == 1) {
    x[a] = 10;
  } else {
    x[a] = a;
  }
}
"""
    all_passed &= run_test("If-else dynamic names (x, a)", code3, "x", [0, 10, 2])
    
    if all_passed:
        print("\nSUMMARY: ALL DYNAMIC PARSING TESTS PASSED!")
    else:
        print("\nSUMMARY: SOME TESTS FAILED.")

if __name__ == "__main__":
    test_dynamic_parsing()
