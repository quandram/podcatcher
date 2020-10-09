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

    def GetNewPods(self):
        feed = feedparser.parse(self.config[configKeys.FEED])
        lastProcessed = self.GetConfigLastProcessedDate()
        podLastDownloaded = lastProcessed

        print ("Downloading %s: " % (self.configSection), end = '')
        podsDownloaded = 0
        for pod in reversed(feed.entries):
            podPublishedOn = self.GetUTCDate(pod.published)

            if  podPublishedOn > lastProcessed and (self.maxEpisodesToDownload == 0 or podsDownloaded < self.maxEpisodesToDownload):
                print (".", end = '')

                try:
                    req = requests.get(pod.links[1]["href"], allow_redirects=True, timeout=(3.05, 27))
                    open(os.path.join(self.podCatcherConfig[configKeys.OUTPUT], self.configSection, self.GetPodFileName(pod)),
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

        print ("\n%s: %d episodes downloaded" % (self.configSection, podsDownloaded ))
        return podLastDownloaded

    def GetPodFileName(self, pod):
        podPublishedOn = self.GetUTCDate(pod.published)
        podExtension = self.GetPodFileExtension(pod)
        if "?" in podExtension:
            podExtension = podExtension.rpartition("?")[0]
        return sanitize(podPublishedOn.strftime("%Y-%m-%dT%H-%M-%SZ") + "_" + self.configSection + "_" + pod.title + "." + podExtension)

    def GetPodFileExtension(self, pod):
        return pod.links[1]["href"].rpartition(".")[-1]

    def GetUTCDate(self, date):
        return parse(date, tzinfos=self.timezone_info).astimezone(timezone('UTC'))

    def GetConfigLastProcessedDate(self):
        return self.GetUTCDate(self.config[configKeys.LAST_DOWNLOADED_DATE])