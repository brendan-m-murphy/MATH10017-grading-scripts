import re
import subprocess
#from chatgpt_wrapper import ChatGPT

def lab3_check(output):
    """
    Correct output should be:

    divided by 3!
    divided by 4!
    oops!
    divided by 3!
    oops!
    divided by 4!
    divided by 9!

    Param: output, string
    Returns: 0 if no error, 1 if error
    """
    correct_matches = ["by 3", "by 4", "oops", "by 3", "oops", "by 4", "by 9"]
    matches = re.findall(r'by [349]|oops', output.lower())
    if matches == correct_matches:
        return 0
    else:
        return 1


    
def lab3_feedback(output):
    correct = "divided by 3!\ndivided by 4!\noops!\ndivided by 3!\noops!\ndivided by 4!\ndivided by 9!\n"
    FLAG = lab3_check(output)
    if FLAG:
        msg = "The output of your program is incorrect. The correct output is:\n\n"
        return msg + correct
    else:
        return "The output of your program looks correct, good job!\n"

########################
# LAB 4  
########################
def lab4_check(out):
    if "the maximum among" in out:
        nums = [int(num) for num in re.findall(r'[0-9]+', out)]
        if max(nums[:3]) == nums[3]:
            return 1
        else:
            return 2
    else:
        nums = [int(num) for num in re.findall(r'[0-9]+', out)]
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        if nums[:11] == primes:
            return 3
        else:
            return 4

def lab4_feedback(out):
    code = lab4_check(out)
    if code in [1, 3]:
        return "The output of your program looks correct, good job!"
    else:
        return "The output of your program seems incorrect."

########################
# LAB 5
########################
def lab5_check(out):
    nums = [int(num) for num in re.findall(r'[0-9]{2,}', out)]
    primes = [11, 13, 17, 19, 23, 29, 31]
    if nums[:7] == primes:
        return 0
    else:
        return 1

def lab5_feedback(out):
    code = lab5_check(out)
    if code == 0:
        return "The output of your program looks correct, good job!"
    else:
        return "The output of your program seems incorrect."


# def gpt_feedback(c_file, bot):
#     with open(c_file, 'rt') as f:
#         code = f.read()
#     response = bot.ask("Check this C code for errors and formatting:\n" + code)
#     return response
