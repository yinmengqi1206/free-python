from typing import List

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        hashtable = dict()
        for i, num in enumerate(nums):
            if target-num in hashtable:
                return [hashtable[target-num],i]
            hashtable[nums[i]] = i
        return []

_inst = Solution()
# 两数之和 https://leetcode.cn/problems/two-sum/description/
twoSum = _inst.twoSum