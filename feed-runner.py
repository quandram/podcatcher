import configparser
import os

from podcatcher import podcatcher
import configKeys

def update_last_processed_date(config, configSection, lastDownloadedDate):
    config.set(configSection, configKeys.LAST_DOWNLOADED_DATE, lastDownloadedDate.strftime("%Y-%m-%d %H:%M:%S %Z"))
    with open(os.path.join(os.path.dirname(__file__), "config.ini"), "w") as configFile:
        config.write(configFile)

def main():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

    for configSection in config.sections():
        if configSection != configKeys.SETTINGS_NAME:
            update_last_processed_date(config, configSection, podcatcher(config[configKeys.SETTINGS_NAME], configSection, config[configSection]).get_new_pods());

if __name__ == "__main__":
    main()
