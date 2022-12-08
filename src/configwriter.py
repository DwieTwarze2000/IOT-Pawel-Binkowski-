from configparser import ConfigParser

config = ConfigParser()

config['DEFAULT'] = {
    'ClientURL': 'opc.tcp://localhost:4840/',
}

with open("config.ini", "w") as config_file:
    config.write(config_file)