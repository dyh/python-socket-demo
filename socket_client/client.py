# coding:utf-8
import datetime
import os
import socket
import time
import cv2
import numpy as np
from socket_client.message import Message


class Client:
    def __init__(self, host='127.0.0.1', port=65432):
        """
        init socket server
        :param host: ip
        :param port: port
        """
        self.host = host
        self.port = port
        pass

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            address = (self.host, self.port)
            client.connect(address)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            print("connecting {0}:{1} ...".format(self.host, self.port))

            image_folder = './images/'
            files = os.listdir(image_folder)
            files.sort()

            message = Message(client, address)

            for file_name in files:
                # 判断是否为png文件
                if file_name[-4:] == '.png':
                    image_path = image_folder + file_name

                    # 读取原始图片
                    image_file = cv2.imread(image_path)
                    # ret, img_encode = cv2.imencode('.jpg', image_file)
                    # str_encode = img_encode.tostring()

                    # 根据文件传输协议，创建数据包，返回 dict()
                    message.clear()

                    message.write(img_obj=image_file, text=None)

                    # get text message
                    try:
                        message.read()
                    except RuntimeError as ex:
                        print('RuntimeError:', ex)
                        break
                    pass

                    # print text message
                    print(message.get_result())

                    message.clear()

                    # get image message
                    try:
                        message.read()
                    except RuntimeError as ex:
                        print('RuntimeError:', ex)
                        break
                    pass

                    # convert buffer to array via numpy
                    array_data = np.frombuffer(message.get_result(), dtype=np.uint8)

                    message.clear()

                    # convert array to image via cv2
                    image_origin = cv2.imdecode(array_data, cv2.IMREAD_COLOR)
                    image_tmp = cv2.resize(image_origin, (960, 540))

                    # 不阻塞，显示这个图片或多个图片，能多快，就多快
                    cv2.imshow('client', image_tmp)
                    cv2.waitKey(1)

                    pass
                pass
            pass
            cv2.destroyWindow('client')
            input()


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
                # record time point
                server_time = datetime.datetime.now()

                # print('server time: ' + str(server_time) + ', ', end='')
                str_text = 'thread name: ' + thread_name + ', server time:' + str(server_time)
                print(str_text)

                # send
                message.write(image_copy, str_text)

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
