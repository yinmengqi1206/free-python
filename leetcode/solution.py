from typing import List


class Solution:
    # 两数之和 https://leetcode.cn/problems/two-sum/description/
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        hashtable = dict()
        for i, num in enumerate(nums):
            if target-num in hashtable:
                return [hashtable[target-num],i]
            hashtable[nums[i]] = i
        return []