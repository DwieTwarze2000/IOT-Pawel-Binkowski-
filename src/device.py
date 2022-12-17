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
      node_name = (await client.get_node(child).read_browse_name()).Name
      self.raports[node_name] = child
    return self

  async def read(self, data_nodes):
    node = self.client.get_node(self.raports[data_nodes])
    return await node.read_value()

  async def write(self, data_nodes, value):
    node = self.client.get_node(self.raports[data_nodes])
    await node.write_value(value)