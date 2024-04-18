from typing import List, Optional

class ListNode:
    def __init__(self, val=0, next=None):
         self.val = val
         self.next = next

class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode()
        curr = dummy
        carry = 0
        
        while l1 or l2 or carry:
            sum_val = carry
            if l1:
                sum_val += l1.val
                l1 = l1.next
            if l2:
                sum_val += l2.val
                l2 = l2.next
            
            carry, val = divmod(sum_val, 10)
            curr.next = ListNode(val)
            curr = curr.next
        return dummy.next

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
# 两数相加 https://leetcode.cn/problems/add-two-numbers/
addTwoNumbers = _inst.addTwoNumbers