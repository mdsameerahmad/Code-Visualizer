from collections import Counter

def longest_substring_k_unique(s, k):
    if not s or k == 0: return 0
    l = res = 0
    count = Counter()
    for r in range(len(s)):
        count[s[r]] += 1
        while len(count) > k:
            count[s[l]] -= 1
            if count[s[l]] == 0:
                del count[s[l]]
            l += 1
        if len(count) == k:
            res = max(res, r - l + 1)
    return res

def min_window_substring(s, t):
    if not t or not s: return ""
    t_count = Counter(t)
    window = {}
    have, need = 0, len(t_count)
    res, res_len = [-1, -1], float("inf")
    l = 0
    for r in range(len(s)):
        c = s[r]
        window[c] = 1 + window.get(c, 0)
        if c in t_count and window[c] == t_count[c]:
            have += 1
        while have == need:
            if (r - l + 1) < res_len:
                res = [l, r]
                res_len = (r - l + 1)
            window[s[l]] -= 1
            if s[l] in t_count and window[s[l]] < t_count[s[l]]:
                have -= 1
            l += 1
    l, r = res
    return s[l:r+1] if res_len != float("inf") else ""
