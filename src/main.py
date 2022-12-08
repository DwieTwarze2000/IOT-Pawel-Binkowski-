import asyncio
from asyncua import Client
from factory import Factory
from agent import Agent
from device import Device
from configparser import ConfigParser

config = ConfigParser()
config.read("../config.ini")

async def test():
    async with Client(url="opc.tcp://localhost:4840/") as client:
      factory = Factory(client)
      factory = await factory.create(client)
      await factory.get_device_names()

      agents = []
      for device in factory.devices:
        # check if connection string in config.ini 
        if device.name in config:
          connection_str = config[device.name]["connection_string"]
        else:
          connection_str = str(input("Enter connection string for device: " + device.name + ": "))
          with open("../config.ini", "a") as config_file:
            config_file.write("[" + device.name + "]\n")
            config_file.write("connection_string = " + connection_str + "\n")
        agent = Agent(device, connection_str)
        await agent.telemetry_send()
        agents.append(Agent(device, connection_str))
      print(agents)
    

if __name__ == "__main__":
  asyncio.run(test())