import PySimpleGUI as sg
import json

class Saver:
    
    saved_patterns = {}

    @classmethod
    def makeSave(cls,rows,name):
        print('saved_patterns')
        cls.saved_patterns[name] = [row for row in rows]
        return cls.saved_patterns
    
    @classmethod
    def JsonSave(cls):
        with open ('data.json','w') as outfile:
            json.dump(cls.saved_patterns,outfile)
        print(cls.saved_patterns)

    @classmethod
    def makeKeysList(cls):
        print('saved_patterns')
        if cls.saved_patterns:
            loader = [x for x in cls.saved_patterns.keys()]
        else:
            empty_list = []
            return empty_list
        return loader
    
    @classmethod
    def getValues(cls, name):
        print('saved_patterns')
        mline_text = ''
        if cls.saved_patterns:
            d_values = cls.saved_patterns[name]
            for i in range(len(d_values)):
                temp_text = f'Name: {d_values[i][0]}\nBPM: {d_values[i][1]}, Signature: {d_values[i][2]}, Note: {d_values[i][3]}, Repeats: {d_values[i][4]}, Accents: {d_values[i][5]}\n\n'
                mline_text += temp_text
        else:
            pass
        return mline_text
    
    
    @classmethod
    def save_load_window(cls):
                    
        layout_sll = [[sg.Listbox(values=cls.makeKeysList(),size=(20, 6),enable_events=True,key='-W2SLBOX-')],
                      [sg.Button('Load',key='-W2SLOAD-')]
                        ]
        layout_slr =[[sg.Output(key='-W2OUTPUT-', size=(50,10))],
                     [sg.Button('Exit')]
                        ]
        layout_slf = [[sg.Col(layout_sll,p=20), sg.VerticalSeparator(p=10),sg.Col(layout_slr,p=20)]
                        ]
        
        return sg.Window('Save / Load',layout_slf,resizable=True,finalize=True,keep_on_top=True,modal=True)

