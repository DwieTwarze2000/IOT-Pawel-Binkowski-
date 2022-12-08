from azure.iot.device import IoTHubDeviceClient
class Agent:
  def __init__(self, device, connection_string):
    self.device = device
    self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
    self.client.connect()
    print("Agent created for device: " + self.device.name)
