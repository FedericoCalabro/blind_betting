import pyttsx3
from threading import Thread
from queue import Queue
from time import sleep

class Speaker(Thread):
    def __init__(self):
        self.queue = Queue()
        self.engine = None #l'inizializzazione qui non funge idk why
        self.should_run = True
        Thread.__init__(self)
        self.start()

    def onStart(self, name):
        return
        print ('starting', name)

    def onWord(self, name, location, length):
        return
        print ('word', name, location, length)

    def onEnd(self, name, completed):
        return
        print ('finishing', name, completed)

    def __new_engine(self):
        engine = pyttsx3.init()
        engine.connect('started-utterance', self.onStart)
        engine.connect('started-word', self.onWord)
        engine.connect('finished-utterance', self.onEnd)
        # voice
        for voice in engine.getProperty('voices'):
            id = str(voice.id).lower()
            if 'it-it' in id:
                engine.setProperty('voice', voice.id)
                break
        #speed
        engine.setProperty('rate', 110)
        return engine

    def speak(self, texts : list[str]):
        self.queue = Queue()
        if self.engine is not None:
            self.engine.stop()
        if 'exit' in texts:
            self.should_run = False
        for text in texts:
            self.queue.put_nowait(text)

    def run(self):
        self.engine = self.__new_engine()
        self.engine.startLoop(False)
        while self.should_run:
            sleep(0.10)
            if self.queue.empty():
                self.engine.iterate()
            else:
                text = self.queue.get_nowait()
                if text == "exit":
                    return
                else:
                    print(text)
                    self.engine.say(text, text)
        self.engine.endLoop()
