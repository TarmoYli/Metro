import threading
import PySimpleGUI as sg

class Worker:
    def __init__(self, from_que, window : sg.Window, locker):
        self.run = False
        self.window = window 
        self.from_que = from_que
        self.locker = locker
        
    def start_thread(self) :
        if not self.run :
            self.blueCollar = threading.Thread(target=self.play_thread, daemon=True)
            self.blueCollar.start()
    
    def stop_thread(self):
        self.run = False
        self.locker.ReleaseLock()

    def play_thread(self):
        self.locker.ApplyLock()
        self.run = True
        while self.run:
            if not self.from_que.empty():
                pat_inst = self.from_que.get()
                pat_inst.play_pattern()
            else:
                self.stop_thread()

class PlaybackLocker:               # wrapperi, käytetään play/play all nappulan toiminnan estämiseen/sallimiseen,
                                    # muutoin voi spämmiklikkauksella pumpata queueen holtittoman määrän tavaraa säikeelle.
    def __init__(self):             # esim. play_all x 6 klikkiä toistaisi kaikki rivit kuudesti jne.
        self.locked = False         # lähtökohtaisesti False jotta päästään liikkeelle

    def ApplyLock(self):
        self.locked = True

    def ReleaseLock(self):
        self.locked = False