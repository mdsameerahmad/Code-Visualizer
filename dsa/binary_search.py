def binary_search(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if nums[m] > target: r = m - 1
        elif nums[m] < target: l = m + 1
        else: return m
    return -1

def search_rotated(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if target == nums[m]: return m
        if nums[l] <= nums[m]:
            if target > nums[m] or target < nums[l]: l = m + 1
            else: r = m - 1
        else:
            if target < nums[m] or target > nums[r]: r = m - 1
            else: l = m + 1
    return -1

def find_peak(nums):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if m > 0 and nums[m] < nums[m - 1]: r = m - 1
        elif m < len(nums) - 1 and nums[m] < nums[m + 1]: l = m + 1
        else: return m
