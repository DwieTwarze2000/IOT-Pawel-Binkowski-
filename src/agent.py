from azure.iot.device import IoTHubDeviceClient, Message, MethodRequest, MethodResponse
import json
from device import Device
from datetime import datetime
import asyncio
class Agent:
  def __init__(self, device, connection_string):
    self.device = device
    self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
    self.client.connect()
    self.client.on_method_request_received = self.methods
    self.tasks = []
    print("Agent created for device: " + self.device.name)
  
  async def telemetry_send(self):
    sendData = {
      "ProductionStatus": await self.device.read("ProductionRate"),
      "WorkorderId": await self.device.read("WorkorderId"),
      "GoodCount":await self.device.read("GoodCount"),
      "BadCount":await self.device.read("BadCount"),
      "Temperature":  await self.device.read("Temperature")
    }
    print("Sending...")
    print(sendData)
    msg = Message(json.dumps(sendData), "UTF-8", "JSON")
    self.client.send_message(msg)
  
  def methods(self, method):
    """
    emergency_stop
    reset_error_status
    maintenance_done
    """
    print("Method called: " + method.name)
    if method.name == "maintenance_done":
      print("maintenance done")
      self.client.patch_twin_reported_properties({"LastMaintenanceDate":  datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    
    elif method.name == "reset_error_status":
      node = self.device.client.get_node(self.device.id)
      self.tasks.append(node.call_method("ResetErrorStatus"))
  
    elif method.name == "emergency_stop":
      node = self.device.client.get_node(self.device.id)
      self.tasks.append(node.call_method("EmergencyStop"))
      print("taski",self.tasks)
    
    self.client.send_method_response(MethodResponse(method.request_id, 0))
  

  def close(self):
    self.client.shutdown()

  def taskPackgageF(self):
    taskPackgage = []
    for task in self.tasks:
      taskPackgage.append(asyncio.create_task(task))
    taskPackgage.append(asyncio.create_task(self.telemetry_send()))
    self.tasks = []
    return taskPackgage

    