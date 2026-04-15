def container_most_water(height):
    l, r = 0, len(height) - 1
    res = 0
    while l < r:
        area = (r - l) * min(height[l], height[r])
        res = max(res, area)
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return res

def three_sum(nums):
    res = []
    nums.sort()
    for i, a in enumerate(nums):
        if i > 0 and a == nums[i - 1]: continue
        l, r = i + 1, len(nums) - 1
        while l < r:
            s = a + nums[l] + nums[r]
            if s > 0: r -= 1
            elif s < 0: l += 1
            else:
                res.append([a, nums[l], nums[r]])
                l += 1
                while nums[l] == nums[l - 1] and l < r:
                    l += 1
    return res
