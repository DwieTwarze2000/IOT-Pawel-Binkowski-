from device import Device


class Factory:
    def __init__(self, client):
      self.devices = []
      self.client = client

    async def create(self, client):
      self.client = client
      objects = self.client.get_node("i=85") 
      for child in await objects.get_children():
          child_name = await child.read_browse_name()
          if child_name.Name != "Server":
              device = Device(self.client, child)
              self.devices.append(await device.create(self.client, child))
      return self

    async def get_device_names(self):
      for device in self.devices:
          print(device.name)
