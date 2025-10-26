import asyncio


async def scheduler_loop():
    # Placeholder loop (no-op) so container stays healthy
    while True:
        await asyncio.sleep(1.0)


def main():
    asyncio.run(scheduler_loop())


if __name__ == "__main__":
    main()

