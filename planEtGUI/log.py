import os
import sys
import time
import datetime
import errno
from socket import error as socket_error
import paho.mqtt.client as mqtt


class Log(mqtt.Client):
    """
    The log class, is used by planEtGUI but can also
    be used independently in the terminal
    """

    def __init__(self, topic, host, path, title, id_pause, id_stop):
        mqtt.Client.__init__(self)

        self.topic = topic
        self.host = host
        self.path = path
        self.title = title
        self.id_stop = id_stop
        self.id_pause = id_pause
        self.on_connect = self._on_connect
        self.on_message = self._on_message
        self.file_name = time.strftime("%Y%m%d_%H%M%S") + '.csv'
        print self.file_name
        # self.file_name = title + '_' + self.file_name
        self.base_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        # self.log_path = path + self.topic
        self.log_path = path + '/' + self.title
        print self.log_path
        self.is_connected = False
        self.is_paused = False

        # try to connect
        try:
            self.connect(self.host, 1883, 60)
        except socket_error as serr:
            if serr.errno != errno.ECONNREFUSED:
                # unhandled error, re-raise
                raise serr
            self.is_connected = False
        except ValueError:
            # TODO: make some action on ValueError
            pass
        else:
            # when connection is made create dirs and log file
            self.is_connected = True
            if not os.path.exists(self.log_path + '/'):
                os.makedirs(self.log_path + '/')
            self.file = open(self.log_path + '/' + self.file_name, "w")

    def _on_connect(self, client, userdata, flags, rc):
        """on connect callback, subscribes to the specified topic"""
        self.subscribe(self.topic)

    def _on_message(self, client, userdata, msg):
        """on message callback, receives mqtt messages"""
        # print 'receiving message'
        epoch_time = self._get_epoch_time()
        time_string = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        if not self.file.closed:
            self.file.write(str(epoch_time) + ',' + time_string + "," + msg.topic + "," + str(msg.payload) + '\n')

    @staticmethod
    def _get_epoch_time():
        t = datetime.datetime.now()
        return time.mktime(t.timetuple())+(t.microsecond/1000000.)

    def log_start(self):
        """start logging"""
        self.loop_start()
        self.is_paused = False

    def log_stop(self):
        """stop logging"""
        self.file.close()
        self.loop_stop()
        self.disconnect()

    def log_pause(self):
        self.loop_stop()
        self.is_paused = True

    def get_id_stop(self):
        return self.id_stop

    def get_id_pause(self):
        return self.id_pause

if __name__ == '__main__':
    log = None
    try:
        topic_cli = sys.argv[1]
        host_cli = sys.argv[2]
        path_cli = sys.argv[3]

        log = Log(topic_cli, host_cli, path_cli, -1, -1, -1)
        if log.is_connected:
            log.log_start()
        else:
            print 'connection refused'
            quit()
        while True:
            pass

    except KeyError:
        pass
    except KeyboardInterrupt:
        log.log_stop()
        quit()
