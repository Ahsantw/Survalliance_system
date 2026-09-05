from threading import Thread, Condition, Lock
from queue import Queue # Assumes Python3
import os
import cv2
import sys
import time
from abc import ABC, abstractmethod
from ultralytics import YOLO
#https://github.com/jrosebr1/imutils/blob/master/imutils/video/filevideostream.py
model_face = YOLO('pretrained/yolov8n-face.pt').cuda()
class FileVideoStream(ABC):
    def __init__(self, path, transform=None, queueSize=512, thread_init=None):
        self.stopped = False
        self.has_read = False
        self.transform = transform
        self.thread_init = thread_init
        self.Q = Queue(maxsize=queueSize)
        self.thread = Thread(target=self._update, args=())
        self.thread.daemon = True

    def start(self):
        self.thread.start()
        return self

    @abstractmethod
    def _read(self):
        raise NotImplementedError 

    @abstractmethod
    def _release(self):
        raise NotImplementedError

    def _update(self):
        if self.thread_init:
            self.thread_init()
        frame_number = -1

        while True:
            if self.stopped:
                self._release()
                return
            frame_number = frame_number + 1

            (grabbed, frame) = self._read()
            if frame_number%5==0:
                continue
            # if the `grabbed` is `False`, then we have reached the end of the video file.
            if not grabbed:
                self.stopped = True
            else:
                self.has_read = True
                # if self.transform:
                #     frame = self.transform(frame)
                frame = cv2.resize(frame, (1920,1080), cv2.INTER_LINEAR)
                results = model_face(frame.copy(), verbose = False)[0]

                boxes = results.boxes.xyxy.cpu().numpy()
                face_imgs = []
                for box in boxes:
                    xmin, ymin, xmax, ymax = map(int,box)
                    face_img = frame[ymin:ymax,xmin:xmax]
                    face_img = cv2.resize(face_img,(112,112))
                    face_imgs.append(face_img)   

                self.Q.put((face_imgs,boxes,frame), block=True, timeout=None) # Blocks this thread when Q is full.
        self._release()

    # pre: Will throw queue.Empty, so check if more().
    def read(self):
        return self.Q.get() 

    def task_done(self):
        self.Q.task_done()

    def more(self):
        tries = 0
        while self.Q.qsize() == 0 and not self.stopped and tries < 5:
            time.sleep(0.0001) # TODO: Replace with condition.wait
            tries += 1
        return self.Q.qsize() > 0

    def _clear_queue(self):
        while not self.Q.empty():
            try:
                self.Q.get(False)
            except Empty:
                continue
            self.Q.task_done()

    def stop(self):
        self.stopped = True
        self._clear_queue() # Will unblock helper thread if the queue is full.
        self.thread.join()

    def running(self):
        return self.more() or not self.stopped


class Cv2FileVideoStream(FileVideoStream):
    def __init__(self, path, transform=None, queueSize=512, thread_init=None):
        super(Cv2FileVideoStream, self).__init__(path, transform, queueSize, thread_init)
        self.capture = cv2.VideoCapture(path)
        self.transform = transform
        self.width = 704 #int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = 480 #int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def _read(self):
        return self.capture.read()

    def _release(self):
        self.capture.release()
