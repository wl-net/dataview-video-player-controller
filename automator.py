from threading import Thread
from queue import Queue
import subprocess

from pyautomator import BaseController, prompt


class VideoPlayerThread(Thread):
    def __init__(self, configuration, queue):
        Thread.__init__(self)
        self.configuration = configuration
        self.queue = queue
        self.player_process = None

    def run(self):
        while True:
            url = self.queue.get()

            if self.player_process:
                self.player_process.terminate()
                self.player_process = None

            if url:
                self.player_process = subprocess.Popen([
                    self.configuration.player_path, self.configuration.get_options(),
                    url, self.configuration.player_location]
                )


class VideoController(BaseController):
    class VideoPlayerConfiguration():
        def __init__(self, player_path='/home/pi/omxplayer-sync/omxplayer-sync',
                     player_location='', master=True, slave=False):
            self.player_path = player_path
            self.player_location = player_location
            self.master = master
            self.slave = slave

        def set_master(self):
            self.master = True
            self.slave = False

        def set_slave(self):
            self.master = False
            self.slave = True

        def set_fullscreen(self):
            self.player_location = ''

        def get_options(self):
            opt = '-'
            if self.master:
                opt += 'm'
            else:
                opt += 'l'
            return opt

    def __init__(self):
        self.configuration = VideoController.VideoPlayerConfiguration(player_location='--win 395,360,1525,1050')
        self.player_thread = None
        self.player_queue = Queue()

    def get_mapping(self):
        mapping = {
            'health': lambda: self.health(),
            'play': lambda url, configuration: self.play(url, configuration),
            'stop': lambda : self.stop(),
        }

        return mapping

    def play(self, url, options={}):
        if options.get('master', False):
            self.configuration.set_master()
        else:
            self.configuration.set_slave()

        if options.get('fullscreen', False):
            self.configuration.set_fullscreen()
        else:
            self.configuration.player_location='--win 395,360,1525,1050'

        if not self.player_thread:
            self.player_thread = VideoPlayerThread(self.configuration, self.player_queue)
            self.player_thread.start()
        self.player_queue.put(url)

        return "Player started"

    def stop(self):
        self.player_queue.put(None)

if __name__ == '__main__':
    prompt(VideoController())
