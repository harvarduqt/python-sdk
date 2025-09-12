from oracle import OracleClient
from enums import Side, Tif
import numpy as np
import asyncio

MARKET_NAME = "ABC/USD"

# haorzhe = OracleClient("ws://localhost:8000/ws")
WEB_URL = "wss://api.oracle.huqt.xyz/ws"
API_KEY = "3533f6c2-f662-40b4-975c-ef4c7ae80f3c"
haorzhe = OracleClient(WEB_URL, API_KEY)

class market_param:
    def __init__(self, name):
        self.name = name
    
    async def send_trade(self, book):
        base_qty = 50
        coin = np.random.randint(2)
        if coin == 0:
            # buy
            if book['asks']:
                best_ask = book['asks'][0]['price']

                print("sending buy")
                
                await haorzhe.place_limit_order(
                    self.name,
                    Side.Buy,
                    best_ask,
                    base_qty,
                    Tif.Ioc
                )
                
        if coin == 1:
            # sell
            if book['bids']:
                best_bid = book['bids'][0]['price']
                print("sending sell")
                
                await haorzhe.place_limit_order(
                    self.name,
                    Side.Sell,
                    best_bid,
                    base_qty,
                    Tif.Ioc
                )


dce = market_param(MARKET_NAME)

async def trade_handler():
    print("\n\033[1;32m-------- Below are the logs for user algorithm --------\033[0m")
    while True:
        book = haorzhe.get_book()[MARKET_NAME]
        await dce.send_trade(book)
        await asyncio.sleep(0.5)

async def main():
    ## change these lines for only the markets you want
    await haorzhe.start_client()
    await haorzhe.set_account_and_domain(account="323bdb13-6b2e-4466-9a0b-46f8de877d50", domain="test", print_metadata=True)

    await haorzhe.subscribe_market(MARKET_NAME)

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