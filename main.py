"""leetcode 283"""

def move_zeros(nums: list[int]):
    """Make a left and right points and move throguh arrary"""
    left = 0
    for right in range(len(nums)):
        if nums[right]:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1 
            
    return nums
            


if __name__ == "__main__":
    nums = [7,0,3,0,5,6]
    print(move_zeros(nums))
