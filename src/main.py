import asyncio

from asyncua import Client

from factory import Factory

async def test():
    async with Client(url="opc.tcp://localhost:4840/") as client:
      factory = Factory(client)
      factory = await factory.create(client)
      await factory.list_devices()

if __name__ == "__main__":
  asyncio.run(test())