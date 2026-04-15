def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i
    return []

def max_subarray(nums):
    if not nums: return 0
    cur_max = res = nums[0]
    for i in range(1, len(nums)):
        cur_max = max(nums[i], cur_max + nums[i])
        res = max(res, cur_max)
    return res

def move_zeroes(nums):
    l = 0
    for r in range(len(nums)):
        if nums[r]:
            nums[l], nums[r] = nums[r], nums[l]
            l += 1
    return nums
