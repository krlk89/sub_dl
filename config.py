import configparser

def create_config(path):
    """Create a config file."""
    path = str(path)
    
    config = configparser.ConfigParser()
    config.add_section("Settings")
    directory = input("Type your media directory: ")
    language = input("Type your preferred subtitle language (e.g. English): ")
    config.set("Settings", "dir", directory)
    config.set("Settings", "language", language)
    
    with open(path, "w") as config_file:
        config.write(config_file)
            
def read_config(path):
    """Read configuration file."""
    path = str(path)
    
    config = configparser.ConfigParser()
    config.read(path)
    
    return config.get("Settings", "dir"), config.get("Settings", "language")
