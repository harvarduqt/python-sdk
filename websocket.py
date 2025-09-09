from typing import Optional, Awaitable, Callable
import asyncio
import websockets

OnMessage = Callable[[bytes], Awaitable[None]]

class WSClient:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._lock = asyncio.Lock()
        self._open_event = asyncio.Event()
        self._connecting_task: Optional[asyncio.Task] = None
        self.ready = asyncio.Event()
        self.api_key = api_key

    async def connect(self) -> None:
        """
        Ensure there's an open connection. If already connecting, wait for it.
        Mirrors the TS logic (OPEN / CONNECTING checks).
        """
        async with self._lock:
            if self._ws and self._ws.open:
                self._open_event.set()
                return
            if self._connecting_task and not self._connecting_task.done():
                # Someone else is connecting; wait outside the lock
                pass
            else:
                self._open_event.clear()
                self._connecting_task = asyncio.create_task(self._do_connect())

        # Wait (outside the lock) for open or failure
        await self._open_event.wait()
        # If connection failed, propagate the exception from the task
        if self._connecting_task and self._connecting_task.done() and self._ws is None:
            self._connecting_task.result()  # raises

    async def _do_connect(self) -> None:
        try:
            # If your SDK needs attaching, do it here after connect.
            headers = {
                "Authorization": f"Bearer {API_KEY}"
            }
            self._ws = await websockets.connect(self.url, extra_headers=headers)
            # Example: oracle_py_sdk.attach(self._ws)  # if required
        except Exception:
            # Signal waiters that we won't open; leave ws as None
            self._ws = None
            self._open_event.set()
            raise
        else:
            self._open_event.set()

    async def send(self, data: bytes) -> None:
        await self.connect()
        if not self._ws or not self._ws.open:
            print("WebSocket not open — message dropped")
            return
        await self._ws.send(data)
    
        """Coroutine (not a generator): receive frames and call on_message(msg)."""
    async def listen(self, on_message, *, reconnect=True, retry_base=1, retry_max=30):
        backoff = retry_base
        try:
            while True:
                try:
                    await self.connect()
                    self.ready.set()  # signal connected
                    async for msg in self._ws:
                        await on_message(msg)
                    if not reconnect:
                        return
                except asyncio.CancelledError:
                    raise
                except (OSError, websockets.ConnectionClosed):
                    await self.close()
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, retry_max)
                else:
                    backoff = retry_base
        finally:
            await self.close()

    async def close(self) -> None:
        if self._ws:
            await self._ws.close()
            self._ws = None