from oracle import OracleClient
from enums import Side, Tif
import asyncio

# haorzhe = OracleClient("ws://localhost:8000/ws")
haorzhe = OracleClient("wss://api.oracle.huqt.xyz/ws", "3533f6c2-f662-40b4-975c-ef4c7ae80f3c")

async def trade_handler():
    print("\n\033[1;32m-------- Below are the logs for user algorithm --------\033[0m")
    # cancelling all open orders
    orders = haorzhe.get_self_open_orders()
    for key, value in orders.items():
        for order in value:
            await haorzhe.cancel_order(key, order['oid'])

async def main():
    ## change these lines for only the markets you want
    await haorzhe.start_client()
    await haorzhe.set_account_and_domain(account="323bdb13-6b2e-4466-9a0b-46f8de877d50", domain="test", print_metadata=True)

    await haorzhe.subscribe_market("DCE/USD")

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