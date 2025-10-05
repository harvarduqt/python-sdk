from huqt_oracle_pysdk import OracleClient
# from enums import Side, Tif
import asyncio

# haorzhe = OracleClient("ws://localhost:8000/ws")
haorzhe = OracleClient("wss://api.oracle.huqt.xyz/ws", "b940f11f-5662-46e0-af58-d9ba446d7337")

async def trade_handler():
    print("\n\033[1;32m-------- Below are the logs for user algorithm --------\033[0m")
    print(haorzhe.get_self_positions())
    # await haorzhe.place_limit_order("110", Side.Buy, 150, 100, Tif.Gtc)
    
    # cancelling all open orders
    # orders = haorzhe.get_self_open_orders()
    # for key, value in orders.items():
    #     for order in value:
    #         await haorzhe.cancel_order(key, order['oid'])

async def main():
    ## change these lines for only the markets you want
    await haorzhe.start_client()
    await haorzhe.set_account_and_domain(account="10b0f98a-da5d-4c21-928f-6d8821333f11", domain="Oracle", print_metadata=True)

    # await haorzhe.subscribe_market("110")

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