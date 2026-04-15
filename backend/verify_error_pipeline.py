from app.engine.executor import Executor
import json

def test_error_pipeline():
    executor = Executor()
    
    # 1. Out of bounds
    print("\n--- Test 1: Out of Bounds ---")
    code1 = "int[] arr = new int[3];\narr[5] = 10;"
    steps1, error1 = executor.execute(code1)
    print(f"Error: {error1}")
    assert error1['type'] == 'RuntimeError'
    assert "bounds" in error1['message'].lower()
    assert error1['line'] == 2

    # 2. Undefined variable
    print("\n--- Test 2: Undefined Variable ---")
    code2 = "int[] arr = new int[3];\narr[0] = j;"
    steps2, error2 = executor.execute(code2)
    print(f"Error: {error2}")
    assert error2['type'] == 'RuntimeError'
    assert "j" in error2['message']
    assert "defined" in error2['message']

    # 3. Infinite loop
    print("\n--- Test 3: Infinite Loop ---")
    code3 = "for(int i = 0; i < 10; ) {\n}"
    steps3, error3 = executor.execute(code3)
    print(f"Error: {error3}")
    assert error3['type'] == 'RuntimeError'
    assert "loop" in error3['message'].lower()

    # 4. Syntax Error
    print("\n--- Test 4: Syntax Error ---")
    code4 = "int x = ;"
    steps4, error4 = executor.execute(code4)
    print(f"Error: {error4}")
    assert error4['type'] == 'SyntaxError'

    # 5. Unsupported Syntax
    print("\n--- Test 5: Unsupported Syntax ---")
    code5 = "System.out.println(1);"
    steps5, error5 = executor.execute(code5)
    print(f"Error: {error5}")
    assert error5['type'] == 'UnsupportedError'

    print("\nALL ERROR PIPELINE TESTS PASSED!")

if __name__ == "__main__":
    test_error_pipeline()
