import solution

if __name__ == '__main__':
    # twoSum
    print(solution.twoSum([2,7,11,15],9))
    # 调用solution.addTwoNumbers 并打印返回结果，参数是listNode，循环打印result的数据
    # l1 = 2 -> 4 -> 3
    # l2 = 5 -> 6 -> 4
    result = solution.addTwoNumbers(
        l1=solution.ListNode(2, solution.ListNode(4, solution.ListNode(3, None))),
        l2=solution.ListNode(5, solution.ListNode(6, solution.ListNode(4, None)))
    )
    # 循环打印结果
    while result:
        # 打印每个node的值
        print(result.val)
        # 移动到下一个node
        result = result.next
