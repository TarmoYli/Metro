import time
import simpleaudio

class Pattern:

    stop_loop = False

    def __init__(self):
        self.base_bpm = 120
        self.base_note = '1/4'
        self.base_signature = 4
        self.base_repeats = 4
        self.base_accent = [1]                  # täytyy olla []-muodossa... kts. SoundPlayback()
        self.metroSoundA = simpleaudio.WaveObject.from_wave_file('metroClick.wav')
        self.metroSoundB = simpleaudio.WaveObject.from_wave_file('metroTick.wav')

    def set_pattern(self,bpm,note,signature,reps,accents):
        self.base_bpm = bpm
        self.base_note = note
        self.base_signature = signature
        self.base_repeats = reps
        self.base_accent = accents
    
    def set_note(self):                         # lasketaan ja palautetaan nuotin pituus
        if self.base_note == '1/1':
            return 60 / self.base_bpm * 4
        elif self.base_note == '1/2':
            return 60 / self.base_bpm * 2
        elif self.base_note == '1/4':
            return 60 / self.base_bpm
        elif self.base_note == '1/8':
            return 60 / self.base_bpm / 2
        elif self.base_note == '1/16':
            return 60 / self.base_bpm / 4
        elif self.base_note == '1/32':
            return 60 / self.base_bpm / 8
        elif self.base_note == '1/64':
            return 60 / self.base_bpm / 16
        else:
            return 0

    def SoundPlayback(self, i):                 # äänen toisto
        if i in self.base_accent:               # tämän takia accentit TÄYTYY olla muodossa "[x]" eli listana
            self.metroSoundA.play()
        else:
            self.metroSoundB.play()
    
    def play_pattern(self):
        length = self.set_note()
        for x in range(self.base_repeats):
            if Pattern.stop_loop:
                break
            i = 1
            while i <= self.base_signature:
                if Pattern.stop_loop:
                    break
                #print(x+1,i)       
                self.SoundPlayback(i)
                time.sleep(length)
                i += 1
