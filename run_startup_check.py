import asyncio, traceback, sys

try:
    from backend.app.main import app, on_startup
    print("✅ backend.app.main imported")
except Exception as e:
    print("❌ Import error:")
    traceback.print_exc()
    sys.exit(1)

async def run():
    try:
        await on_startup()
        print("✅ on_startup completed without error")
    except Exception as e:
        print("❌ on_startup raised an exception")
        traceback.print_exc()
        sys.exit(1)

asyncio.run(run())
