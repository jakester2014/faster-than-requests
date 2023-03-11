import time
import faster_than_requests


lista = ["https://httpbin.org/get" for _ in range(25)]


time2 = time.time()
faster_than_requests.get2str_list(lista, threads = True)
print(time.time() - time2)
