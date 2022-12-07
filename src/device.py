class Device:
  def __init__(self, client, id):
    self.client = client
    self.id = id
    self.raports = {}
    self.name = ""

  async def create(self, client, id):
    self.client = client
    node = client.get_node(id)
    self.name = (await node.read_browse_name()).Name
    node_children = await node.get_children()
    for child in node_children:
      node_name = await client.get_node(child).read_browse_name()
      self.raports[node_name] = child
    return self

  async def read(self, id):
    node = self.client.get_node(id)
    return await node.read_value()

  async def write(self, id, value):
    node = self.client.get_node(id)
    await node.write_value(value)

 