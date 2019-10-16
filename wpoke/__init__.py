import asyncio


def set_event_loop_policy():
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        # Falling back to default event loop policy
        pass
