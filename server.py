# coding:utf-8

import cv2
import time
import socket
import datetime
import numpy as np
from threading import Thread
from multiprocessing import Manager

from message import Message


class Server:
    def __init__(self, host='0.0.0.0', port=65432, timeout=30):
        """
        init socket server
        :param host: ip
        :param port: port
        :param timeout: default 30 secs
        """
        sync_manager = Manager()
        # record the latest timestamp of each socket message
        self.dict_latest_message_timestamp = sync_manager.dict()
        # record the flag of loop, set its value to False when you want to close a socket
        self.dict_loop_flag = sync_manager.dict()

        self.host = host
        self.port = port
        # timeout value of socket
        self.timeout = timeout

        # thread of timeout daemon
        self.thread_timeout_daemon = Thread(target=self._timeout_handle)
        # terminated with main thread
        self.thread_timeout_daemon.daemon = True
        pass

    def _timeout_handle(self):
        # to judge whether the socket has timeout
        while True:
            for key, value in self.dict_latest_message_timestamp.items():

                if (time.time() - value) > self.timeout:
                    print('#' * 5, 'socket {0} timeout.'.format(key), '#' * 5)
                    # remove loop flag, close socket
                    self.dict_loop_flag.pop(key)
                    # remove timestamp
                    self.dict_latest_message_timestamp.pop(key)
                pass

            time.sleep(self.timeout)
        pass

    def start(self):
        # start the timeout daemon thread
        self.thread_timeout_daemon.start()

        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

                server.bind((self.host, self.port))
                server.listen()
                print("listening {0}:{1} ...".format(self.host, self.port))

                socket_obj, address_obj = server.accept()

                # begin time of one socket
                begin_time = time.time()

                thread_name = str(begin_time)

                thread_obj = Thread(target=self._socket_handle, args=(socket_obj, address_obj, thread_name))
                thread_obj.daemon = True

                self.dict_loop_flag[thread_name] = True

                # start socket thread
                thread_obj.start()
            pass
        pass

    def _socket_handle(self, socket_obj, address_obj, thread_name):
        """
        function of handle socket
        :param thread_name:
        :param socket_obj:
        :param address_obj:
        :return:
        """
        # receive messages from tcp-client
        with socket_obj:
            print("accepted connection from", address_obj)
            message = Message(socket_obj, address_obj)

            # flag of loop
            while True:
                # if this thread has not timeout
                if self.dict_loop_flag.get(thread_name) is True:
                    pass
                else:
                    print('process {0} closed'.format(thread_name))
                    break
                pass

                # clear socket buffer
                message.clear()

                try:
                    message.read()
                except RuntimeError as ex:
                    print('RuntimeError:', ex)
                    break
                pass

                # convert buffer to array via numpy
                array_data = np.frombuffer(message.get_result(), dtype=np.uint8)
                # convert array to image via cv2
                image_origin = cv2.imdecode(array_data, cv2.IMREAD_COLOR)

                # do some image processing here
                image_copy = image_origin.copy()

                # record server time
                server_time = datetime.datetime.now()

                text_message = 'thread name: ' + thread_name + ', server time: ' + str(server_time)
                print(text_message)

                # send image object
                message.write(image_copy, text_message)

                if self.dict_loop_flag.get(thread_name) is True:
                    # update the timestamp of each latest message
                    self.dict_latest_message_timestamp[thread_name] = time.time()
                else:
                    # if there is no more loop flag, then close socket
                    print('process {0} closed'.format(thread_name))
                    break
                pass

                time.sleep(0.00001)
            pass

            # close socket
            socket_obj.shutdown(socket.SHUT_RDWR)
            socket_obj.close()
            pass
