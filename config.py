import configparser

def config(path):
    """Create a config file."""
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "dir", "/home/kaarel/Downloads/")
    config.set("Settings", "language", "English")
    config.set("Settings", "hi", "No")
    config.set("Settings", "sub_info",
    "You are using %(font)s at %(font_size)s pt")
    
    with open(path, "w") as config_file:
        config.write(config_file)
        
if __name__ == "__main__":
    createConfig("settings.ini")
