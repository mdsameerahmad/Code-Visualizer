def subsets(nums):
    res = []
    subset = []
    def dfs(i):
        if i >= len(nums):
            res.append(subset.copy())
            return
        subset.append(nums[i])
        dfs(i + 1)
        subset.pop()
        dfs(i + 1)
    dfs(0)
    return res

def permutations(nums):
    res = []
    if len(nums) == 1: return [nums.copy()]
    for _ in range(len(nums)):
        n = nums.pop(0)
        perms = permutations(nums)
        for p in perms:
            p.append(n)
        res.extend(perms)
        nums.append(n)
    return res

def n_queens(n):
    col, pos_diag, neg_diag = set(), set(), set()
    res = []
    board = [["."] * n for _ in range(n)]
    def backtrack(r):
        if r == n:
            res.append(["".join(row) for row in board])
            return
        for c in range(n):
            if c in col or (r + c) in pos_diag or (r - c) in neg_diag:
                continue
            col.add(c); pos_diag.add(r + c); neg_diag.add(r - c)
            board[r][c] = "Q"
            backtrack(r + 1)
            col.remove(c); pos_diag.remove(r + c); neg_diag.remove(r - c)
            board[r][c] = "."
    backtrack(0)
    return res
