import asyncio
import json
from datetime import datetime

from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

from device import Device

class Agent:
  def __init__(self, device, connection_string):
    self.device = device
    self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
    self.client.connect()
    self.client.on_method_request_received = self.methods
    self.tasks = []
    self.client.patch_twin_reported_properties({'DeviceError': None})
    self.client.patch_twin_reported_properties({'ProductionRate': None})

    print("Agent created for device: " + self.device.name)
  
  async def telemetry_send(self):
    # deviceErrors = await self.getErrorName(await self.device.read("DeviceError"))
    sendData = {
      "ProductionStatus": await self.device.read("ProductionStatus"),
      "WorkorderId": await self.device.read("WorkorderId"),
      "GoodCount":await self.device.read("GoodCount"),
      "BadCount":await self.device.read("BadCount"),
      "Temperature":  await self.device.read("Temperature"),
      "ProductionRate": await self.device.read("ProductionRate"),
      "DeviceError": { 
        "errors": self.getErrorName(await self.device.read("DeviceError")),
        "errorCode": await self.device.read("DeviceError")
      }
    }
    await self.updateReportedTwin(sendData)
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
      print("reset error status")
      node = self.device.client.get_node(self.device.id)
      self.tasks.append(node.call_method("ResetErrorStatus"))
  
    elif method.name == "emergency_stop":
      print("emergency stop")
      node = self.device.client.get_node(self.device.id)
      self.tasks.append(node.call_method("EmergencyStop"))
      # print("taski",self.tasks)
    
    self.client.send_method_response(MethodResponse(method.request_id, 0))
  
  def getErrorName(self, number):
    errors = []
    bin_num = bin(number)[2:].rjust(4, "0")
    if bin_num[-1] == "1":
      errors.append("Emergency stop")
    if bin_num[-2] == "1":
      errors.append("Power failure")
    if bin_num[-3] == "1":
      errors.append("Sensor failure")
    if bin_num[-4] == "1":
      errors.append("Unknown")
    if bin_num.count("1") == 0:
      return "No errors"
    return errors

  def close(self):
    self.client.shutdown()

  def taskPackgageF(self):
    taskPackgage = []
    for task in self.tasks:
      taskPackgage.append(asyncio.create_task(task))
    taskPackgage.append(asyncio.create_task(self.telemetry_send()))
    self.tasks = []
    return taskPackgage

  async def updateReportedTwin(self, data):
    self.client.patch_twin_reported_properties({'DeviceError': data["DeviceError"]})
    self.client.patch_twin_reported_properties({'ProductionRate': data["ProductionRate"]})
