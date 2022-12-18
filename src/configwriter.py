from configparser import ConfigParser

class Config:
    def __init__(self):
        self.config = ConfigParser()
        self.read()

    def read(self):
        self.config.read("./config.ini")
        return self.config

    def save(self):
        with open("./config.ini", "w") as config_file:
            self.config.write(config_file)

    def get_connection_string(self, device_name):
        if self.config.has_option(device_name, "connection_string"):
            connection_string = self.config[device_name]["connection_string"]
        else:
            connection_string = str(input("Enter connection string for device {}: ".format(device_name)))
            self.config[device_name] = {
                "connection_string": connection_string
            }
            self.save()
        return connection_string

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