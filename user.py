from oracle import OracleClient
from enums import Side, Tif
import asyncio

haorzhe = OracleClient("ws://localhost:8000/ws")

async def trade_handler():
    # all user logic should go here
    # market states/open orders/everything is tracked nicely by the oracle client
    # you should have like a while True loop to keep updating
    await haorzhe.place_limit_order(market='book', side=Side.Buy, price=100000, size=100000, tif=Tif.Gtc)
    await haorzhe.place_limit_order(market='book', side=Side.Buy, price=10, size=10, tif=Tif.Gtc)

    # await haorzhe.cancel_order(market='book', order_id=22)
    while True:
        print("hello world!")
        await asyncio.sleep(10)

async def main():
    ## change these lines for only the markets you want
    await haorzhe.start_client()
    await haorzhe.set_account_and_domain(account="andrew", domain="test")

    print()
    await haorzhe.subscribe_market("book")
    await haorzhe.subscribe_market("book2")

    await haorzhe.enter_conversions_market("Split")
    await haorzhe.enter_options_market("Yes Call")

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