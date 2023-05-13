import time

start_time  = time.time()

try:
    curr_time = start_time
    while True:
        print("In Loop")
        time.sleep(2)
        if (time.time()-curr_time) >= 30:
            print("yo")
            curr_time = time.time()

except KeyboardInterrupt:
    print("Exiting")