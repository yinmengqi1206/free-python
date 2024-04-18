import solution

if __name__ == '__main__':
    # twoSum
    print(solution.twoSum([2,7,11,15],9))
    # addTwoNumbers
    # 创建链表l1: 2 -> 4 -> 3，表示数字342
    l1 = solution.ListNode(2)
    l1.next = solution.ListNode(4)
    l1.next.next = solution.ListNode(3)

    # 创建链表l2: 5 -> 6 -> 4，表示数字465
    l2 = solution.ListNode(5)
    l2.next = solution.ListNode(6)
    l2.next.next = solution.ListNode(4)

    # 调用addTwoNumbers函数
    # 打印结果链表
    result = solution.addTwoNumbers(l1, l2)
    while result:
        print(result.val, end=" ")
        result = result.next
    pass
