"""
1번 부터 6번 까지 모두 순서에 맞게 실행됨
"""

a = 10
b = 20
print('1: {}'.format(a))
print('2: {}'.format(b))

def hello(): print('Hello World')

if __name__ == "__main__":
    print('3: {}'.format(a))
    print('4: {}'.format(b))
    a = 100
    b = 200
    print('5: {}'.format(a))
    print('6: {}'.format(b))

    hello()

# def hello(): print('Hello World') # 여기 있으면 오류남