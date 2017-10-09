"""Configuration file creation and reading for Subscene subtitle downloader (sub_dl)
   Author: https://github.com/krlk89/sub_dl
"""

import configparser

def create_config(path):
    """Create a config file."""
    config = configparser.ConfigParser()
    config.add_section("Settings")
    directory = input("Type your media directory: ")
    config.set("Settings", "dir", directory)
    
    with open(str(path), "w") as config_file:
        config.write(config_file)
            
def read_config(path):
    """Read configuration file."""
    config = configparser.ConfigParser()
    config.read(str(path))
    
    return config.get("Settings", "dir")

