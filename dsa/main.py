from dsa.arrays import two_sum, max_subarray, move_zeroes
from dsa.strings import valid_anagram, longest_unique_substring, group_anagrams
from dsa.hashing import contains_duplicate, longest_consecutive
from dsa.sliding_window import longest_substring_k_unique, min_window_substring
from dsa.two_pointers import container_most_water, three_sum
from dsa.binary_search import binary_search, search_rotated, find_peak
from dsa.stack import valid_parentheses, next_greater, MinStack
from dsa.recursion_backtracking import subsets, permutations, n_queens

def run_tests():
    # Arrays
    print("Two Sum:", two_sum([2, 7, 11, 15], 9))
    print("Max Subarray:", max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))
    print("Move Zeroes:", move_zeroes([0, 1, 0, 3, 12]))

    # Strings
    print("Valid Anagram:", valid_anagram("anagram", "nagaram"))
    print("Longest Unique Substring:", longest_unique_substring("abcabcbb"))
    print("Group Anagrams:", group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))

    # Hashing
    print("Contains Duplicate:", contains_duplicate([1, 2, 3, 1]))
    print("Longest Consecutive:", longest_consecutive([100, 4, 200, 1, 3, 2]))

    # Sliding Window
    print("Longest Substring K Unique:", longest_substring_k_unique("eceba", 2))
    print("Min Window Substring:", min_window_substring("ADOBECODEBANC", "ABC"))

    # Two Pointers
    print("Container Most Water:", container_most_water([1, 8, 6, 2, 5, 4, 8, 3, 7]))
    print("Three Sum:", three_sum([-1, 0, 1, 2, -1, -4]))

    # Binary Search
    print("Binary Search:", binary_search([-1, 0, 3, 5, 9, 12], 9))
    print("Search Rotated:", search_rotated([4, 5, 6, 7, 0, 1, 2], 0))
    print("Find Peak:", find_peak([1, 2, 3, 1]))

    # Stack
    print("Valid Parentheses:", valid_parentheses("()[]{}"))
    print("Next Greater:", next_greater([4, 5, 2, 25]))
    ms = MinStack()
    ms.push(-2); ms.push(0); ms.push(-3)
    print("MinStack get_min:", ms.get_min())

    # Recursion
    print("Subsets:", subsets([1, 2, 3]))
    print("Permutations:", permutations([1, 2, 3]))
    print("N-Queens Solution Count:", len(n_queens(4)))

if __name__ == "__main__":
    run_tests()
