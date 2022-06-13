import feedparser
import os
import requests

from datetime import datetime
from dateutil.parser import parse
from dateutil import tz
from pytz import timezone

from sanitize_filename import sanitize
import configKeys

class podcatcher:
    def __init__(self, podConfig, configSection, configData):
        self.podCatcherConfig = podConfig
        self.configSection = configSection
        self.config = configData
        try:
            self.maxEpisodesToDownload = int(self.podCatcherConfig[configKeys.MAX_EPISODES_TO_DOWNLOAD])
        except:
            self.maxEpisodesToDownload = 0

        if not os.path.exists(os.path.join(self.podCatcherConfig[configKeys.OUTPUT])):
            try:
                os.mkdir(os.path.join(self.podCatcherConfig[configKeys.OUTPUT]))
            except OSError as e:
                print ("Creation of the directory %s failed" % self.podCatcherConfig[configKeys.OUTPUT], e.data)
                return
            else:
                print ("Successfully created the directory %s " % self.podCatcherConfig[configKeys.OUTPUT])

        if not os.path.exists(os.path.join(self.podCatcherConfig[configKeys.OUTPUT], self.configSection)):
            try:
                os.mkdir(os.path.join(self.podCatcherConfig[configKeys.OUTPUT], self.configSection))
            except OSError as e:
                print ("Creation of the directory %s failed" % self.configSection, e.data)
            else:
                print ("Successfully created the directory %s " % self.configSection)

        PACIFIC = tz.gettz("America/Los_Angeles")
        self.timezone_info = {"PST": PACIFIC, "PDT": PACIFIC}

    def get_new_pods(self):
        feed = feedparser.parse(self.config[configKeys.FEED])
        lastProcessed = self.get_config_last_processed_date()
        podLastDownloaded = lastProcessed

        print ("Downloading %s: " % self.configSection, end = '')
        podsDownloaded = 0
        for pod in reversed(feed.entries):
            podPublishedOn = self.get_utc_date(pod.published)

            if  podPublishedOn > lastProcessed and (self.maxEpisodesToDownload == 0 or podsDownloaded < self.maxEpisodesToDownload):
                print (".", end = '')

                try:
                    podAudioLink = self.get_pod_audio_link(pod)
                    req = requests.get(podAudioLink, allow_redirects=True, timeout=(3.05, 27))
                    open(os.path.join(self.podCatcherConfig[configKeys.OUTPUT], self.configSection, self.get_pod_file_name(pod) + "." + self.get_pod_file_extension(podAudioLink)),
                        "wb").write(req.content)
                    podLastDownloaded = podPublishedOn
                    podsDownloaded += 1
                    if self.maxEpisodesToDownload > 0 and podsDownloaded == self.maxEpisodesToDownload:
                        break

                except requests.exceptions.ConnectionError:
                    print ("\nError: Request timedout: %s" % pod.title)
                    break
                except Exception as e:
                    print ("\nError: catching pod: %s" % pod.title)
                    print(type(e))
                    print(e)
                    break

        print (" | %d episodes downloaded\n" % podsDownloaded )
        return podLastDownloaded

    def get_pod_audio_link(self, pod):
        for link in pod.links:
            if link.type == "audio/mpeg":
                return link["href"]
        print ("\nError: Finding Audio Link: %s" % pod.title)

    def get_pod_file_name(self, pod):
        podPublishedOn = self.get_utc_date(pod.published)
        return sanitize(podPublishedOn.strftime("%Y-%m-%dT%H-%M-%SZ") + "_" + self.configSection + "_" + pod.title)

    def get_pod_file_extension(self, podUrl):
        podExtension = podUrl.rpartition(".")[-1]
        if "?" in podExtension:
            podExtension = podExtension.rpartition("?")[0]
        return sanitize(podExtension)

    def get_utc_date(self, date):
        return parse(date, tzinfos=self.timezone_info).astimezone(timezone('UTC'))

    def get_config_last_processed_date(self):
        return self.get_utc_date(self.config[configKeys.LAST_DOWNLOADED_DATE])