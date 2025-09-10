from oracle import OracleClient
from enums import Side, Tif
import asyncio

# haorzhe = OracleClient("ws://localhost:8000/ws")
haorzhe = OracleClient("wss://api.oracle.huqt.xyz/ws", "73d07237-0761-46e5-be6e-bd449a7bf19c")

async def trade_handler():
    print("\n\033[1;32m-------- Below are the logs for user algorithm --------\033[0m")
    # all user logic should go here
    # market states/open orders/everything is tracked nicely by the oracle client
    # you should have like a while True loop to keep updating
    # await haorzhe.
    await haorzhe.place_limit_order("book", Side.Buy, 10, 10, Tif.Alo)
    
    while True:
        print("hello world!")
        await asyncio.sleep(10)

async def main():
    ## change these lines for only the markets you want
    await haorzhe.start_client()
    await haorzhe.set_account_and_domain(account="joe", domain="test", print_metadata=True)

    await haorzhe.subscribe_market("book")

    ## DO NOT CHANGE BELOW THIS LINE
    task = asyncio.create_task(trade_handler())
    try:
        # CTRL-C to stop
        await asyncio.Event().wait()
    except:
        pass
    finally:
        task.cancel()
        await haorzhe.stop_client()
        print("\033[1;31mOracleClient stopped. See ya next time...\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())