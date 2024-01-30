import PySimpleGUI as sg
import metrologic
import queue
import metroWorker
import save
import copy

# todolist:
# - mahdollisesti rivin editointi tablessa... (ei todellakaan (tai ehkä joskus))
# - Save/Load toiminto... ehkä... (vie/tuo rowlist -> update rowlist.) (edit: välilehteen lista tallennetuista jotka haetaan JSONista nimellä?)


def make_pattern_instance(num, rows):
    pat_stats = rows[num]
    pat_temp = metrologic.Pattern()
    tempacc = [int(i) for i in pat_stats[5].split(',')]
    pat_temp.set_pattern(
        bpm=int(pat_stats[1]),
        signature=int(pat_stats[2]),
        note=pat_stats[3],
        reps=int(pat_stats[4]),
        accents=tempacc)
    return pat_temp

def IntValidation(values_input):
    if values_input:
        if len(values_input) and values_input[-1] not in ('0123456789'):
            return True
    else:
        return False

def main():
    sg.theme('DarkBlue12')

    queMain = queue.Queue()

    note_list = ['Meny',['1/1','1/2','1/4','1/8','1/16','1/32','1/64']]

    tempo_pick, note_pick, sig_pick, rep_pick, act_pick, name_pick, display_content, play_once = '','','','','','','',''

    row_list = []

    header_list = ['Name', 'BpM', 'signature', 'note', 'repeats', 'Accents']

    pattern_rdy_tbl = sg.Table(values=row_list,
        headings=header_list,
        display_row_numbers=False,
        auto_size_columns=False,
        justification='center',
        key='-TABLE-',
        col_widths=[10,8,8,8,8,8],
        enable_events=True,
        expand_x=True,
        expand_y=True)
    #    enable_click_events=True)

    layout_l = [[sg.Push(),sg.Text('Variables:',font=(20),pad=((0, 0), (0, 20))),sg.Push()],
                [sg.Text('Name Pattern: ',p=5),sg.Push(),sg.Input('',enable_events=True,key='-NAMEINPUT-',size=(10,10))],
                [sg.Text('Enter BPM: ',p=5),sg.Push(), sg.Input('',enable_events=True, key='-TEMPOINPUT-',size=(10,10))],
                [sg.Text('Enter signature: ',p=5),sg.Push(),sg.Input('',enable_events=True,key='-SIGINPUT-',size=(10,10))],
                [sg.Text('Select Note: ',p=5), sg.ButtonMenu('Click',note_list,key='-NOTEBTN-'),sg.Push(),sg.Text('Selected: '),sg.Text(key='-NOTEPICK-')],
                [sg.Text('Enter repeat: ',p=5),sg.Push(),sg.Input('',enable_events=True,key='-REPINPUT-',size=(10,10))],
                [sg.Text('Accent location/s(use "," to separate values): ',p=5),sg.Push(),sg.Input('',enable_events=True,key='-ACCENTINPUT-',size=(10,10))],
                [sg.Button('Exit',pad=10),sg.Push(),sg.Button('Add',pad=10,key='-ADD-')]]

    layout_r = [[sg.Push(),sg.Text('Patterns:',font=(20)),sg.Push()],
                [pattern_rdy_tbl],
                [sg.Button('Play',disabled=False, key='-PLAY-'),sg.Button('Play All',key='-PLAYALL-'),sg.Button('Stop', key='-STOP-'),sg.Push(),sg.Button('Remove',key='-REMOVE-')],
                [sg.Button('Save Patterns', key='-SAVE-'),sg.Button('Load Patterns', key='-LOAD-')]]

    layout =   [[sg.Titlebar('MetroGnome')],
                [sg.Push(),sg.Text('M E T R O G N O M I C A L', font=('',20,'bold',)),sg.Push()],
                [sg.Col(layout_l,p=20), sg.VerticalSeparator(p=10) ,sg.Col(layout_r,p=20)]]

    window1,window2 = sg.Window("MetroGnome", layout, resizable=True, finalize=True), None # tsekkaa finalize

    lock = metroWorker.PlaybackLocker()
    play = metroWorker.Worker(from_que=queMain, window=window1, locker=lock)
    use_save = save.Saver()
    
    use_save.GetFromJson()

    isRunning = True                                    # ÄLÄ KOSKE NÄIHIN!!!

    while isRunning:                                    # ÄLÄ KOSKE NÄIHIN!!!
        window, event, values = sg.read_all_windows()   # ÄLÄ KOSKE NÄIHIN!!!
        if event == sg.WIN_CLOSED or event == "Exit":   # ÄLÄ KOSKE NÄIHIN!!!
            window.close()
            if window == window2:                       # ÄLÄ KOSKE NÄIHIN!!!
                window2 = None                          # ÄLÄ KOSKE NÄIHIN!!!
            elif window == window1:                     # ÄLÄ KOSKE NÄIHIN!!!
                isRunning = False                       # ÄLÄ KOSKE NÄIHIN!!!
        if event == '-NOTEBTN-':
            note_pick = values['-NOTEBTN-']
            window['-NOTEPICK-'].update(note_pick)

        elif event == '-TEMPOINPUT-':            
            if IntValidation(values['-TEMPOINPUT-']):
                window['-TEMPOINPUT-'].update(values['-TEMPOINPUT-'][:-1])
            else:
                tempo_pick = values['-TEMPOINPUT-']

        elif event == '-SIGINPUT-':
            if IntValidation(values['-SIGINPUT-']):
                window['-SIGINPUT-'].update(values['-SIGINPUT-'][:-1])
            else:
                sig_pick = values['-SIGINPUT-']

        elif event == '-REPINPUT-':
            if IntValidation(values['-REPINPUT-']):
                window['-REPINPUT-'].update(values['-REPINPUT-'][:-1])
            else:
                rep_pick = values['-REPINPUT-']

        elif event == '-ACCENTINPUT-':
            if len(values['-ACCENTINPUT-']) and values['-ACCENTINPUT-'][-1] not in ('0123456789,'):
                window['-ACCENTINPUT-'].update(values['-ACCENTINPUT-'][:-1])
            else:
                act_pick = values['-ACCENTINPUT-']

        elif event == '-NAMEINPUT-':
            name_pick = values['-NAMEINPUT-']

        
        elif event == '-ADD-': # melko himmeitä lauseita:
            
            if any(value == '0' for key, value in values.items() if key != '-TABLE-' and key != '-NAMEINPUT-' and key != '-ACCENTINPUT-'): # any tarkistaa onko arvo 0 missään kentässä, ei oteta huomioon kenttiä table, name ja accent
                sg.popup_ok('Values cannot be 0 in Tempo, Signature or Repeats',title='CHECK VALUES',keep_on_top=True)
                pass

            elif any(value == '' or not 1 <= int(value) <= 999 for key,value in values.items() if key in ('-TEMPOINPUT-', '-SIGINPUT-','-REPINPUT-')): # any tarkistaa onko arvo 1-999 missään kentissä tempo, signature ja repeat.
                sg.popup_ok('Values must be in range 1-999 in Tempo, Signature and Repeats.',title='CHECK VALUES',keep_on_top=True)
                pass
            
            elif ',,' in act_pick or act_pick[0] == ',' or act_pick[-1] == ',':                                                                 # tarkistetaan että ei ala eikä lopu pilkulla eikä ole useita pilkkuja peräkkäin.
                sg.popup_ok('Accents value must NOT start or end with " , " or have " , " after another " , "','Do not use:\n,1,3\n1,3,\n1,,3',title='CHECK ACCENT',keep_on_top=True)

            elif all(bool(value) for key, value in values.items() if key != '-TABLE-'):                 # all tarkistaa että kaikissa kentissä on JOKU arvo. paitsi tablessa (jonne ne viedään).
                row_list.append([name_pick,tempo_pick,sig_pick,note_pick,rep_pick,act_pick])            
                window['-TABLE-'].update(values=row_list)
            else:
                sg.popup_ok('All Fields must have a valid value!',title='MISSING VALUES',keep_on_top=True)

        elif event == '-TABLE-':
            if not values['-TABLE-']:               # jos arvo on tyhjä ei tehdä mitään
                pass
            else:
                play_once = values['-TABLE-'][0]

        elif event == '-PLAY-':
            if not lock.locked:                                     # workerissa asetetaan lukko päälle/pois säikeen tilan mukaan, ei haluta ketjuttaa joten estetään.
                metrologic.Pattern.stop_loop = False                # poistetaan loopin toiston esto
                if play_once == '':                                 # jos mitään ei ole valittu tablesta, play_once jää tyhjäksi.
                    pass
                else:
                    temp_pattern = make_pattern_instance(play_once,row_list)
                    queMain.put(temp_pattern)
                    play.start_thread()
            else:                                                                                           # tämän elsen voinee poistaa 
                sg.popup_ok('Spam Prevention! Please, patience grasshopper!',title='WAIT',keep_on_top=True) # ellei keksi tähän jotain...

        elif event == '-PLAYALL-':
            if not lock.locked:
                metrologic.Pattern.stop_loop = False                # poistetaan loopin toisto esto
                if not row_list:
                    pass
                else:
                    for row in range(len(row_list)):
                        playall = make_pattern_instance(row, row_list)  # tehdään patterneja ja lisätään niitä queueen
                        queMain.put(playall)
                play.start_thread()                                     # jonka jälkeen start_thread() aloittaa säikeen joka hakee queuesta patternit.
            else:                                                                                           # tämänkin elsen voi poistaa
                sg.popup_ok('Spam Prevention! Please, patience grasshopper!',title='WAIT',keep_on_top=True) # kts ed.

            
        elif event == '-STOP-':
            play.stop_thread()
            metrologic.Pattern.stop_loop = True                     # pysäytetään looppi
            with queMain.mutex:                                     # lukitaan que (varmuuden vuoksi, ehkä turha, koska mikään muu ei sitä käytä kuin worker)
                queMain.queue.clear()                               # tyhjätään que

        elif event == '-REMOVE-':
            if not values['-TABLE-']:
                pass
            else:
                del row_list[values['-TABLE-'][0]]
                window['-TABLE-'].update(values=row_list)
                play_once = ''

        elif event == '-SAVE-':
            if not row_list:
                sg.popup('nothing to save')
            else:
                savename = sg.popup_get_text('Enter name:',title='Save', keep_on_top=True)
                if savename in use_save.saved_patterns.keys():
                    if sg.popup_yes_no(f'{savename} already exists,\nDo you want to overwrite it?') != 'Yes':
                        sg.popup('Save Cancelled')
                    else:
                        use_save.makeSave(rows=row_list, name=savename)
                        use_save.JsonSave()
                else:
                    use_save.makeSave(rows=row_list, name=savename)
                    use_save.JsonSave()

        elif event == '-LOAD-' and not window2:
            window2 == use_save.save_load_window()
        
        elif event == '-W2SLBOX-':  # päivittää sisällön output ikkunaan
            if values['-W2SLBOX-']:
                display_content = values['-W2SLBOX-'][0]
                window['-W2OUTPUT-'].update(use_save.getValues(display_content))
        
        elif event == '-W2SLOAD-':
            if values['-W2SLBOX-']:
                get_name = values['-W2SLBOX-'][0]
                patterns_to_load = use_save.saved_patterns[get_name]
                row_list = copy.deepcopy(patterns_to_load)              # pff referenssi
                window1['-TABLE-'].update(values=row_list)

        elif event == '-W2SDELETE-':
            if values['-W2SLBOX-']:
                name_to_delete = values['-W2SLBOX-'][0]
                use_save.removeSave(name=name_to_delete)
                window['-W2SLBOX-'].update(values=use_save.makeKeysList())

    window.close()

if __name__ == '__main__':
    main()