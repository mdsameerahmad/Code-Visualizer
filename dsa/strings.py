from collections import Counter, defaultdict

def valid_anagram(s, t):
    return Counter(s) == Counter(t)

def longest_unique_substring(s):
    seen = {}
    l = res = 0
    for r in range(len(s)):
        if s[r] in seen:
            l = max(l, seen[s[r]] + 1)
        seen[s[r]] = r
        res = max(res, r - l + 1)
    return res

def group_anagrams(strs):
    res = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for c in s:
            count[ord(c) - ord('a')] += 1
        res[tuple(count)].append(s)
    return list(res.values())
