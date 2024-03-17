# from fastapi import FastAPI
# from fastapi_utils.tasks import repeat_every
import time

# app = FastAPI()

# @app.on_event("startup")
# @repeat_every(seconds=5)
# async def check_anomalies() -> None:
#     print(1)
#     time.sleep(1)
#     print(2)
#     time.sleep(1)
#     print(3)


# import datetime
# import bot
# from asgiref.sync import async_to_sync
# from fastapi import FastAPI
# from fastapi_utils.tasks import repeat_every

# app = FastAPI()

# @app.on_event("startup")
# # @repeat_every(seconds = 100)
# async def parse_links() -> None:
#     msg = '12345'
#     await bot.bot.send_message(761706095, msg)
# # async_to_sync(bot.bot.send_message)(-1002023766309, '123')

import bot
import asyncio
import time
from itertools import cycle
from asgiref.sync import async_to_sync

l = ['1', '2', '3']

def foo():
    print("Start foo")
    for i, v in cycle(enumerate(l)):
        print(i, v)
        if i + 1 == len(l):
            print('finish')
            async_to_sync(bot.bot.send_message)(761706095, i)
        time.sleep(1)


def main():
    foo()

main()
# asyncio.run(main())
# asyncio.get_event_loop().run_until_complete(main())



# def main():
#     while True:
#         pass

# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         print('Interrupted')

