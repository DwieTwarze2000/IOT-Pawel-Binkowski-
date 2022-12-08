from azure.iot.device import IoTHubDeviceClient
from device import Device
class Agent:
  def __init__(self, device, connection_string):
    self.device = device
    self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
    self.client.connect()
    print("Agent created for device: " + self.device.name)
  
  async def telemetry_send(self):

    sendData = {
      "ProductionStatus": await self.device.read("ProductionRate"),
      "WorkorderId": await self.device.read("WorkorderId"),
      "GoodCount":await self.device.read("GoodCount"),
      "BadCount":await self.device.read("BadCount"),
      "Temperature":  await self.device.read("Temperature")
    }

    self.client.send_message(sendData)
    print(sendData)
    
