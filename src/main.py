import asyncio
import time

from asyncua import Client
from asyncua.ua.uaerrors import BadLicenseExpired

from agent import Agent
from configwriter import Config
from device import Device
from factory import Factory

async def main():
  try:
    config = Config()
    url = config.get_url()
    async with Client(url=url) as client:
      factory = Factory(client)
      factory = await factory.create(client)
      await factory.get_device_names()
      agents = []
      for device in factory.devices:
        connection_str = config.get_connection_string(device.name)
        agent = Agent(device, connection_str)
        await agent.telemetry_send()
        agents.append(agent)
      try:
        while True:
          tasks = []
          for agent in agents:
            agent_tasks = agent.taskPackgageF()
            for task in agent_tasks:
              tasks.append(task)

          await asyncio.gather(*tasks)
          time.sleep(5)
      except Exception as e:
        print(e) 
        for agent in agents:
          agent.close()
  except KeyboardInterrupt:
    print("Goodbye! ;)")
    for agent in agents:
      agent.close()
  except Exception as e:
    if isinstance(e, BadLicenseExpired):
      print("License expired! ;)")
    else:
      print(e)

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())