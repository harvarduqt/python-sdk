from oracle import OracleClient
from enums import Side, Tif
import asyncio

haorzhe = OracleClient("ws://localhost:8000/ws")


async def trade_handler():
    print("\n\033[1;32m-------- Below are the logs for user algorithm --------\033[0m")
    # all user logic should go here
    # market states/open orders/everything is tracked nicely by the oracle client
    # you should have like a while True loop to keep updating
    
    while True:
        await asyncio.sleep(0.1)

        """a simple arbitrage detection and execution"""
        book = haorzhe.get_book()
        if book['book']['bids'] and book['book2']['bids']:
            # means both buy markets exist
            best_bid_book = book['book']['bids'][0]['price']
            best_bid_book2 = book['book2']['bids'][0]['price']
            if best_bid_book + best_bid_book2 > 100:
                # if can sell for more than 100, execute arb for the smaller quantity
                # then immediately convert that into QTC
                execute_size = min(book['book']['bids'][0]['size'], book['book2']['bids'][0]['size'])
                await haorzhe.convert('Split', execute_size)
                await haorzhe.place_limit_order('book', Side.Sell, best_bid_book, execute_size, Tif.Ioc)
                await haorzhe.place_limit_order('book2', Side.Sell, best_bid_book2, execute_size, Tif.Ioc)
                print('Buy side arbitrage found!')
        
        if book['book']['asks'] and book['book2']['asks']:
            # means both sell markets exist
            best_ask_book = book['book']['asks'][0]['price']
            best_ask_book2 = book['book2']['asks'][0]['price']
            if best_ask_book + best_ask_book2 < 100:
                # if can buy for less than 100, execute arb for the smaller quantity
                # then immediately convert that into QTC
                execute_size = min(book['book']['asks'][0]['size'], book['book2']['asks'][0]['size'])
                await haorzhe.place_limit_order('book', Side.Buy, best_ask_book, execute_size, Tif.Ioc)
                await haorzhe.place_limit_order('book2', Side.Buy, best_ask_book2, execute_size, Tif.Ioc)
                await haorzhe.convert('Merge', execute_size)
                print('Sell side arbitrage found!')



async def main():
    ## change these lines for only the markets you want
    await haorzhe.start_client()
    await haorzhe.set_account_and_domain(account="joe", domain="test")

    await haorzhe.subscribe_market("book")
    await haorzhe.subscribe_market("book2")

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