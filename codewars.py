def solution(text, ending):
    print(text[-2])
    print(ending[0])
    if text[-2] == ending[0]:
        return True
    else:
        return False

if __name__ == "__main__":
    print(solution("abc", "bc"))