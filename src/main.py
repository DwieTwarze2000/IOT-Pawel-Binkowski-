import asyncio
from asyncua import Client
from factory import Factory
from agent import Agent
from device import Device
from configwriter import Config
# from configparser import ConfigParser

async def test():
  config = Config()
  async with Client(url="opc.tcp://localhost:4840/") as client:
    factory = Factory(client)
    factory = await factory.create(client)
    await factory.get_device_names()

    agents = []
    for device in factory.devices:
      connection_str = config.get_connection_string(device.name)
      agent = Agent(device, connection_str)
      await agent.telemetry_send()
      agents.append(agent)
    print(agents)
  
if __name__ == "__main__":
  asyncio.run(test())