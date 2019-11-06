import cv2
import time
import threading
import logging
import uuid
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident

_logger = logging.getLogger(__name__)

class InvalidRecordingId(Exception):
    pass

class RecordingIdAlreadyExists(Exception):
    pass

class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """
    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()


class Camera(object):
    instances = {}

    def __new__(cls, uri):
        if uri not in cls.instances:
            cls.instances[uri] = object.__new__(cls)
        return cls.instances[uri]
        
    def __init__(self, uri):
        self.uri = uri
        self.event = CameraEvent()
        self.frame = None

        self.last_access = time.time()

        self.thread = threading.Thread(target=self._thread)

        self.recording_callbacks = {}

        # start background frame thread
        self.thread.start()

        # wait until frames are available
        while self.get_frame() is None:
            time.sleep(0)
        
    def get_frame(self):
        """Return the current camera frame."""
        self.last_access = time.time()

        # wait for a signal from the camera thread
        self.event.wait()
        self.event.clear()

        return self.frame

    def _thread(self):
        """Camera background thread."""
        _logger.debug('Starting camera thread.')
        frames_iterator = self.frames()
        for frame in frames_iterator:
            self.frame = frame
            self.event.set()  # send signal to clients
            time.sleep(0)

            # if anything is recording
            if self.recording_callbacks:
                self.last_access = time.time()

                recording_ids_to_stop = []
                for recording_id, recording_callback in self.recording_callbacks:
                    try:
                        if not recording_callback(recording_id, frame):
                            _logger.debug("Stopped recording #{} due to request".format(recording_id))
                            recording_ids_to_stop.append(recording_id)
                    except Exception:
                        recording_ids_to_stop.append(recording_id)
                        _logger.exception("Stopped recording #{} due to exception".format(recording_id))

                for recording_id in recording_ids_to_stop:
                    try:
                        del self.recording_callbacks[recording_id]
                    except KeyError:
                        pass

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - self.last_access > 10:
                frames_iterator.close()
                _logger.debug('Stopping camera thread due to inactivity.')
                break
        self.thread = None

    @staticmethod
    def unlink(uri):
        # TODO: destroy threads (it will also stop recoding)
        # TODO: use __del__ maybe?
        del cls.instances[uri]

    def frames(self):
        camera = cv2.VideoCapture(self.uri)
        if not camera.isOpened():
            # TODO: return picture
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            data = cv2.imencode('.jpg', img)[1].tobytes()
            yield data
            del data

    def start_recording(self, recording_id, callback):
        if not recording_id:
            raise InvalidRecordingId(recording_id)
        
        if recording_id in self.recording_callbacks:
            raise RecordingIdAlreadyExists(recording_id)
        
        self.recording_callbacks[recording_id] = callback
        _logger.debug("Started recording #{}...".format(recording_id))
