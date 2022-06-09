# coding=utf-8

from tasks import add, fib

result = add.delay(4, 4)
# result = fib.delay(2000000)
# print('Is task ready: %s' % result.ready())

run_result = result.get()
print('task result: %s' % run_result)
