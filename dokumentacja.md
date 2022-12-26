# DOKUMENTACJA – PROJEKT IOT 
### PAWEŁ BIŃKOWSKI

## Jak uruchomić program
```
python -m venv ./venv
source ./venv/Scripts/activate
pip install -r req.txt
python src/main.py
```

## Wymagania
Żeby program się wykonał należy utworzyć urządzenie na platforimie azure

## Połączenie z OPC UA severL
Żeby połączyć się z serwerem została użyta biblioteka asyncua. Została ona użyta na instancji klasy Klienta.
Żeby configuracja działa należy uzupełnić url. Po uruchumieniu programu wykona się funkcja get_url().

```
def get_url(self):
    if self.config.has_option("opcua", "url"):
        url = self.config["opcua"]["url"]
    else:
        url = str(input("Enter url: "))
        self.config["opcua"] = {
            "url": url
        }
        self.save()
    return url
```
Url zostanie zapisane do pliku config.ini.

Połączenie odbywa się w głównej funkcji programu main() w pliku ./src/main.py

```
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
```
## Konfiguracja Agenta i D2C Message
Żeby agent mógł wysyłać dane do Iot Hub należy uzupełnić connection string. Po uruchomieniu programu wykona się funkcja get_connection_string().

```
def get_connection_string(self, device_name):
    if self.config.has_option("iot_hub", device_name):
        connection_str = self.config["iot_hub"][device_name]
    else:
        connection_str = str(input("Enter connection string: "))
        self.config["iot_hub"] = {
            device_name: connection_str
        }
        self.save()
    return connection_str
```
Connection string zostanie zapisany do pliku config.ini.

Agent jest odpowiedzialny za wysyłanie danych do Iot Hub. Wysyłanie odbywa się w funkcji telemetry_send().
Wysyłana data zawiera: ProductionStatus, WorkorderId, GoodCount, BadCount, Temperature, ProductionRate, DeviceError (nazwa błędu i kod błędu).

```
  async def telemetry_send(self):
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

    if await self.device.read("DeviceError") == 1:
      print("Failed to send message, emergency stopped! :(")
    else:
      msg = Message(json.dumps(sendData), "UTF-8", "JSON")
      self.client.send_message(msg)

```

Dodatkowo na device twinie agent zapisuje informacje o deviceErrors, LastMintananceDate, ProductionRate (desire, reported)


## Direct Method

Agent obsługuje następujące direct methody: emergency_stop, reset_error_status, maintenace_done 

```
 def methods(self, method):
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
  
```

## Data Calculations and buisness logic

Kalkulacje oraz logika biznesowa została zrobiona za pomocą kwerend znajdujących się w ./stream_analitycs_explorer/IOT_PROJECT_SAJ/Transofrmation.asaql
