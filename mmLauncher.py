#!/usr/bin/env python3

# ^^ Linux-executable init

# ### LEGAL ###

# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org/>

import json
import sys
import subprocess
import os
import threading
from ast import literal_eval
import base64
import shutil
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import filedialog
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import filedialog

try:
    from Crypto.Hash import SHA3_256
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pycryptodome"])
    from Crypto.Hash import SHA3_256


def relative_file(relative_path: str):
    script_dir = os.getcwd()
    absolute_path = os.path.join(script_dir, relative_path)
    return absolute_path


def t(x):
    with open(relative_file('src/config.json'), 'r') as f:
        config = json.loads(f.read())
        language = config["language"]
    with open(relative_file('src/resources/languages.json')) as f:
        languages = json.loads(f.read())
        try:
            word = languages[language][x]
        except KeyError:
            if x[0] == '_':
                return ''
            word = x
    return word


def log(x):
    with open(relative_file('src/userdata/log.txt'), 'r') as f:
        _log = f.read()
    _log += '[' + str(datetime.now()) + ']: ' + str(x) + '\n'
    with open(relative_file('src/userdata/log.txt'), 'w') as f:
        f.write(_log)


def extended_bubble_sort(main_list: list, secondary_list: list) -> (list, list):
    main_list2 = main_list
    secondary_list2 = secondary_list
    if len(main_list2) == len(secondary_list2):
        n = len(main_list2)
        for i in range(n - 1):
            for j in range(0, n - i - 1):
                if main_list2[j] < main_list2[j + 1]:
                    main_list2[j], main_list2[j + 1] = main_list2[j + 1], main_list2[j]
                    secondary_list2[j], secondary_list2[j + 1] = secondary_list2[j + 1], secondary_list2[j]
        return main_list2, secondary_list2
    else:
        raise Exception('list lengths do not match')


def get_favourites():
    with open(relative_file('src/userdata/favourites.list'), 'r') as f:
        return literal_eval(f.read())


def get_favourites_img(index: int):
    with open(relative_file('src/userdata/favourites.list'), 'r') as f:
        x = f.read()
        if len(literal_eval(x)) > index:
            if os.path.exists(relative_file('src/apps/' + literal_eval(x)[index] + '/icon_high.gif')):
                return relative_file('src/apps/' + literal_eval(x)[index] + '/icon_high.gif')
            else:
                return relative_file('src/resources/Empty_high.gif')
        else:
            return relative_file('src/resources/Empty_high.gif')


def get_favourites_name(index: int, link: bool = False):
    with open(relative_file('src/userdata/favourites.list'), 'r') as f:
        x = f.read()
        if len(literal_eval(x)) > index:
            return literal_eval(x)[index]
        else:
            if link:
                return 'None'
            return ''


def get_app_img(index: int):
    with open(relative_file('src/appdata/packages.list'), 'r') as f:
        x = f.read()
        if len(literal_eval(x)) > index:
            if os.path.exists(relative_file('src/apps/' + literal_eval(x)[index] + '/icon.gif')):
                return relative_file('src/apps/' + literal_eval(x)[index] + '/icon.gif')
            else:
                return relative_file('src/resources/Empty.gif')
        else:
            return relative_file('src/resources/Empty.gif')


def get_app_name(index: int, link: bool = False):
    with open(relative_file('src/appdata/packages.list'), 'r') as f:
        x = f.read()
        if len(literal_eval(x)) > index:
            return literal_eval(x)[index]
        else:
            if link:
                return 'None'
            return ''


def get_app_names():
    with open(relative_file('src/appdata/packages.list'), 'r') as f:
        return literal_eval(f.read())


def get_apps_usage():
    names = get_app_names()
    with open(relative_file('src/userdata/usage.json'), 'r') as f:
        file = json.loads(f.read())
    usage = []
    for i in range(len(names)):
        usage.append(file[names[i]])
    x, y = extended_bubble_sort(usage, names)
    return y


def get_app_attribute(index: int, attribute):
    name = get_app_name(index, True)
    if name == 'None':
        return ''
    with open(relative_file('src/appdata/packages.json')) as f:
        x = json.loads(f.read())
        return x[name][attribute]


def checksignature(signature, publickey):
    message = pow(signature, publickey[0], publickey[1])
    return message


def install_app_dialog():
    install_window = tk.Tk()
    install_window.title(t('Install app - mmLauncher'))
    install_window.option_add('*Font', 'Helvetica 21')
    a1_pressed = tk.BooleanVar()
    a1_pressed.set(False)
    a1 = tk.Button(install_window, text=t('Select file') + ' (.mmp)', command=lambda: a1_pressed.set(True), width=32)
    b1 = tk.Label(install_window, text='', width=32)
    c1 = tk.Label(install_window, text='', width=20)
    c2 = tk.Label(install_window, text='', width=12, font='Helvetica 21 bold')
    d1 = tk.Label(install_window, text='', width=64, font='Helvetica 10')
    e1_pressed = tk.BooleanVar()
    e1_pressed.set(False)
    e1 = tk.Button(install_window, text=t('Install'), width=32, state=tk.DISABLED, command=lambda: e1_pressed.set(True))
    a1.grid(row=0, column=0, columnspan=2)
    b1.grid(row=1, column=0, columnspan=2)
    c1.grid(row=2, column=0)
    c2.grid(row=2, column=1)
    d1.grid(row=3, column=0, columnspan=2)
    e1.grid(row=4, column=0, columnspan=2)
    loop = tk.BooleanVar()
    loop.set(True)
    path = ''
    while loop.get():
        try:
            install_window.update()
            if a1_pressed.get():
                a1_pressed.set(False)
                path = filedialog.askopenfilename()
                if path == ():
                    pass
                else:
                    try:
                        security = anti_virus(path)
                        if security < 0:
                            messagebox.showwarning(t('Warning - mmLauncher'), t('This app is not secure and probably contains malware!'))
                            b1.config(text='')
                            c1.config(text='')
                            c2.config(text='')
                            d1.config(text='')
                            e1.config(state=tk.DISABLED)
                        elif security == 0:
                            with open(path, 'r') as f:
                                original_file = f.read()
                            content = json.loads(original_file)
                            k = str(content['public_keys'][0]) + str(content['public_keys'][1])
                            h = SHA3_256.new()
                            h.update(k.encode())
                            b1.config(text=content['name'])
                            c1.config(text='author')
                            c2.config(text=t('Unknown source'))
                            d1.config(text=base64.urlsafe_b64encode(h.digest()).decode())
                            e1.config(state=tk.NORMAL)
                        elif security > 0:
                            with open(path, 'r') as f:
                                original_file = f.read()
                            content = json.loads(original_file)
                            k = str(content['public_keys'][0]) + str(content['public_keys'][1])
                            h = SHA3_256.new()
                            h.update(k.encode())
                            b1.config(text=content['name'])
                            c1.config(text=content['author'])
                            c2.config(text=t('Verified'))
                            d1.config(text=base64.urlsafe_b64encode(h.digest()).decode())
                            e1.config(state=tk.NORMAL)
                        else:
                            b1.config(text='')
                            c1.config(text='')
                            c2.config(text='')
                            d1.config(text='')
                            e1.config(state=tk.DISABLED)
                    except (FileNotFoundError, TypeError, ValueError):
                        b1.config(text='')
                        c1.config(text='')
                        c2.config(text='')
                        d1.config(text='')
                        e1.config(state=tk.DISABLED)
            if e1_pressed.get():
                e1_pressed.set(False)
                install_app(path)
                loop.set(False)
                install_window.destroy()
        except tk.TclError:
            loop.set(False)


def anti_virus(path):
    with open(path, 'r') as f:
        original_file = f.read()
    content = json.loads(original_file)
    with open(relative_file('src/resources/trusted_sources.json')) as f:
        trusted = json.loads(f.read())
    verified = False
    harmful = False
    if content['author'] in trusted:
        if content['public_keys'] == trusted[content['author']]:
            verified = True
        else:
            harmful = True
    for filename in content['files']:
        h = SHA3_256.new()
        h.update(content['files'][filename].encode())
        hashed = int(h.hexdigest(), 16)
        x = checksignature(int(content['signature'][filename], 16), content['public_keys'])
        if hashed != x:
            harmful = True
    if content['name'] == 'mmLauncher':
        if content['author'] == 'MartinMerkli':
            pass
        else:
            harmful = True
    if harmful:
        log('found harmful: ' + path)
        return -1
    elif verified:
        return 1
    else:
        return 0


def install_app(path):
    with open(path, 'rb') as f:
        original_file = f.read()
    content = json.loads(original_file)
    if content['name'] == 'mmLauncher':
        for filename in content['files']:
            with open(relative_file(filename), 'wb') as f:
                f.write(base64.urlsafe_b64decode(content['files'][filename].encode()))
        log('updated mmLauncher from ' + path)
        log('file content: ' + str(content).replace('\n', ''))
        return None
    if content['name'] in get_app_names():
        for filename in content['files']:
            with open(relative_file('src/apps/' + content['name'] + '/' + filename), 'wb') as f:
                f.write(base64.urlsafe_b64decode(content['files'][filename].encode()))
        log('updated ' + content['name'] + ' from ' + path)
        log('file content: ' + str(content).replace('\n', ''))
        return None
    os.makedirs(relative_file('src/apps/' + content['name']), exist_ok=True)
    for filename in content['files']:
        with open(relative_file('src/apps/' + content['name'] + '/' + filename), 'wb') as f:
            f.write(base64.urlsafe_b64decode(content['files'][filename].encode()))
    with open(relative_file('src/appdata/packages.json'), 'r') as f:
        x = json.loads(f.read())
    x[content['name']] = {'description': content['description']}
    with open(relative_file('src/appdata/packages.json'), 'w') as f:
        json.dump(x, f, indent=4)
    with open(relative_file('src/appdata/packages.list'), 'r') as f:
        x = literal_eval(f.read())
    x.append(content['name'])
    with open(relative_file('src/appdata/packages.list'), 'w') as f:
        f.write(str(x))
    with open(relative_file('src/userdata/usage.json'), 'r') as f:
        x = json.loads(f.read())
    x[content['name']] = 0
    with open(relative_file('src/userdata/usage.json'), 'w') as f:
        json.dump(x, f, indent=4)
    log('installed ' + content['name'] + ' from ' + path)
    log('file content: ' + str(content).replace('\n', ''))


def delete_app(name):
    shutil.rmtree(relative_file('src/apps/' + name))
    with open(relative_file('src/appdata/packages.list'), 'r') as f:
        c = literal_eval(f.read())
    c.remove(name)
    with open(relative_file('src/appdata/packages.list'), 'w') as f:
        f.write(str(c))
    with open(relative_file('src/userdata/favourites.list'), 'r') as f:
        favourites = literal_eval(f.read())
    if name in favourites:
        favourites.remove(name)
        with open(relative_file('src/userdata/favourites.list'), 'w') as f:
            f.write(str(favourites))
    log('deleted ' + name)


def setup():
    dirs = ['src', 'src/appdata', 'src/apps', 'src/resources', 'src/userdata']
    files = {'appdata/packages.json': '{\n}',
             'appdata/packages.list': '[]',
             'config.json': '{\n    "language": "English"\n}',
             'userdata/favourites.list': '[]',
             'userdata/log.txt': '',
             'userdata/usage.json': '{\n}',
             'resources/languages.json': '{\n  "Deutsch": {\n    "Store": "Shop",\n    "Library": "Bibliothek",\n    "mmLauncher": "mmLauncher",\n    "Launch": "",\n    "sort by": "Sortieren",\n    "Install app from file": "Programm aus Datei installieren",\n    "Select file": "Datei auswählen",\n    "Install": "Installieren",\n    "Verified": "Verifiziert",\n    "Unknown source": "Unbekannte Quelle",\n    "Install app - mmLauncher": "App installieren - mmLauncher",\n    "Warning - mmLauncher": "Warnung - mmLauncher",\n    "This app is not secure and probably contains malware!": "Diese App ist nicht sicher und enthält wahrscheinlich Schadsoftware!",\n    "settings": "Einstellungen",\n    "delete app": "App löschen",\n    "Language": "Sprache",\n    "_Launch2": "ausführen"\n  },\n  "English": {\n    "Store": "Store",\n    "Library": "Library",\n    "mmLauncher": "mmLauncher",\n    "Launch": "Launch",\n    "sort by": "sort by",\n    "Install app from file": "Install app from file",\n    "Select file": "Select file",\n    "Install": "Install",\n    "Verified": "Verified",\n    "Unknown source": "Unknown source",\n    "Install app - mmLauncher": "Install app - mmLauncher",\n    "Warning - mmLauncher": "Warning - mmLauncher",\n    "This app is not secure and probably contains malware!": "This app is not secure and probably contains malware!",\n    "settings": "settings",\n    "delete app": "delete app",\n    "Language": "Language",\n    "_Launch2": ""\n  }\n}',
             'resources/trusted_sources.json': '{\n  "MartinMerkli": [1362243165304578894309201688767474283592266294026201544306900624262889890297511073254423696592454595048158834568215857560047324283189865371862334921152712452681, 19465811633847345478716576471895580814724272792494896346734421115848937708468699935931458625530076436502570376864163733619192181123310237749886429086697051702724285437064022062047152276984176474287454286578111699623710852095119509127631132653874903045699522759404760012113920317344837274219410668005938844060017427702043]\n}',}
    files_64 = {'resources/Empty.gif': 'R0lGODlhQABAAIABAAAAAP8A_yH5BAEKAAEALAAAAABAAEAAAAJFjI-py-0Po5y02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jef6zvf-DwwKh8Si8YhMKpfMpvMJjUqn1Kr1is1qt9yuN1AAADs=',
                'resources/Empty_high.gif': 'R0lGODlhQAFAAYABAAAAAJpUMCH-EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAEALAAAAABAAUABAAL-jI-py-0Po5y02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jef6zvf-DwwKh8Si8YhMKpfMpvMJjUqn1Kr1is1qt9yu9wsOi8fksvmMTqvX7Lb7DY_L5_S6_Y7P6_f8vv8PGCg4SFhoeIiYqLjI2Oj4CBkpOUlZaXmJmam5ydnp-QkaKjpKWmp6ipqqusra6voKGys7S1tre4ubq7vL2-v7CxwsPExcbHyMnKy8zNzs_AwdLT1NXW19jZ2tvc3d7f0NHi4-Tl5ufo6err7O3u7-Dh8vP09fb3-Pn6-_z9_v_w8woMCBBAsaPIgwocKFDBs6fAgxosSJFCtavIgxo8bGjRw7evwIMqTIkSRLmjyJMqXKlSxbunwJM6bMmTRr2ryJM6fOnTx7-vwJNKjQoUSLGj2KNKnSpUybOn0KNarUqVSrWr2KNavWrVy7ev0KNqzYsWTLmj2LNq3atWzbun0LN67cuXTr2r2LN6_evXz7-v0LOLDgwYQLGz6MOLHixYwbO34MObLkyZQrW76MObPmzZw7e_4MOrTo0aRLmz6NOrXq1axbu34NO7bs2bRr276NO7fu3bx7-_4NPLjw4cSLGz-OXEMBADs=',
                'resources/Empty_small.gif': 'R0lGODlhMAAwAIAAAAAAAAAAACH5BAEKAAEALAAAAAAwADAAAAIxjI-py-0Po5y02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jef6zvf-DwwKh8Si8egpAAA7',
                'resources/settings_icon.gif': 'R0lGODlhMAAvAOcAAAAAAAEBAQICAgMDAwQEBAUFBQYGBgcHBwgICAkJCQoKCgsLCwwMDA0NDQ4ODg8PDxAQEBERERISEhMTExQUFBUVFRYWFhcXFxgYGBkZGRoaGhsbGxwcHB0dHR4eHh8fHyAgICEhISIiIiMjIyQkJCUlJSYmJicnJygoKCkpKSoqKisrKywsLC0tLS4uLi8vLzAwMDExMTIyMjMzMzQ0NDU1NTY2Njc3Nzg4ODk5OTo6Ojs7Ozw8PD09PT4-Pj8_P0BAQEFBQUJCQkNDQ0REREVFRUZGRkdHR0hISElJSUpKSktLS0xMTE1NTU5OTk9PT1BQUFFRUVJSUlNTU1RUVFVVVVZWVldXV1hYWFlZWVpaWltbW1xcXF1dXV5eXl9fX2BgYGFhYWJiYmNjY2RkZGVlZWZmZmdnZ2hoaGlpaWpqamtra2xsbG1tbW5ubm9vb3BwcHFxcXJycnNzc3R0dHV1dXZ2dnd3d3h4eHl5eXp6ent7e3x8fH19fX5-fn9_f4CAgIGBgYKCgoODg4SEhIWFhYaGhoeHh4iIiImJiYqKiouLi4yMjI2NjY6Ojo-Pj5CQkJGRkZKSkpOTk5SUlJWVlZaWlpeXl5iYmJmZmZqampubm5ycnJ2dnZ6enp-fn6CgoKGhoaKioqOjo6SkpKWlpaampqenp6ioqKmpqaqqqqurq6ysrK2tra6urq-vr7CwsLGxsbKysrOzs7S0tLW1tba2tre3t7i4uLm5ubq6uru7u7y8vL29vb6-vr-_v8DAwMHBwcLCwsPDw8TExMXFxcbGxsfHx8jIyMnJycrKysvLy8zMzM3Nzc7Ozs_Pz9DQ0NHR0dLS0tPT09TU1NXV1dbW1tfX19jY2NnZ2dra2tvb29zc3N3d3d7e3t_f3-Dg4OHh4eLi4uPj4-Tk5OXl5ebm5ufn5-jo6Onp6erq6uvr6-zs7O3t7e7u7u_v7_Dw8PHx8fLy8vPz8_T09PX19fb29vf39_j4-Pn5-fr6-vv7-_z8_P39_f7-_v___yH-EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP4ALAAAAAAwAC8AAAj-AP0JHEiwoMAcMAwSfJFDocOHDkMwAAAgg8MLFBeAgMhRIQ8OFENuLOghJEUNOjp2bAHBpEkWBFW4DNlhhUqFCxC4TFFkg0gFCkpSfBAEo0kDCW8O5GGSQkqBRmcyGBhCg0kaSgcOCKnCoFWXFgvaCJkg68CQDi2YxOAQrVmBbt_CpSjXX8gode3SlRtyQd2We83WCOmjLpGQJMzCCOkhrz8SIW9AvKF2ZgHHAg_MrMiDoIPNAJI8vDFCSJIVkh02AQ2BIOggDnuA7qywCGjXFEd0xAGaYmuOMgMHB9BxRMgMPwTuyGCyY0iY_lhQtMFxSMgiBndwBU6xxVwALjj-hjyiOq7DGW7NK5RBManDFBRLiKf7Qb3BGIEfUpQwH0CIECa9oF9-bRFI0AomiVAEASZdUCBx_TlUgUkCkBedS9gV1ICBBtknhEtdFUTBcQadQJEMEKEHgIAFaUcRBQ9NQNEEBjEFgIMPAWaEQQ9QhKNDL9jnTwI-OvQVdAWF5B1EQuoFgF8FmUjRDgo1ORANIc2g0GAmjdCCS1IotNh0TFLUwEMwaAbaUwopYCVkHBZUgpshNdCDcxShoJARIbmHmUFfUqSEQYBB-OeD_BVkHEVEHKpQECJVaSVmzSmUQ50tNqYUCA0RNFF7DyFIkYA51EdRBkx05MRXAGwgWZBdFInAEZy9ccBmQT100BtFG6hU2a4P9gbjTSZpgFdVIdFYkIz7UfkEq4aqVMQBsBX0aQwGuUDRBwYBcUBhf45oIKaOPsgBC-iyAFKc5foD7UxhtevVrhrIG-xMcgUEADs='}
    for i in range(len(dirs)):
        os.mkdir(relative_file(dirs[i]))
    for i in files:
        with open(relative_file('src/' + i), 'w') as f:
            f.write(files[i])
    for i in files_64:
        with open(relative_file('src/' + i), 'wb') as f:
            f.write(base64.urlsafe_b64decode(files_64[i].encode()))


def win_store():
    store_window = tk.Tk()
    store_window.title(t('mmLauncher'))
    store_window.option_add('*Font', 'Helvetica 32')
    a1_pressed = tk.BooleanVar()
    a1_pressed.set(False)
    a1 = tk.Button(store_window, text=t('Store'), command=lambda: a1_pressed.set(True), width=12, state=tk.DISABLED)
    a2_pressed = tk.BooleanVar()
    a2_pressed.set(False)
    a2 = tk.Button(store_window, text=t('Library'), command=lambda: a2_pressed.set(True), width=12)
    a3_img = tk.PhotoImage(master=store_window, file=relative_file('src/resources/settings_icon.gif'))
    a3_pressed = tk.BooleanVar()
    a3_pressed.set(False)
    a3 = tk.Button(store_window, image=a3_img, command=lambda: a3_pressed.set(True))
    b1_pressed = tk.BooleanVar()
    b1_pressed.set(False)
    b1 = tk.Button(store_window, text=t('Install app from file'), command=lambda: b1_pressed.set(True))
    a1.grid(row=0, column=0, columnspan=2)
    a2.grid(row=0, column=2)
    a3.grid(row=0, column=5)
    b1.grid(row=1, column=0, columnspan=5)
    loop = tk.BooleanVar()
    loop.set(True)
    while loop.get():
        try:
            store_window.update()
            if a1_pressed.get():
                a1_pressed.set(False)
            if a2_pressed.get():
                a2_pressed.set(False)
                loop.set(False)
                store_window.destroy()
                win_library_start()
            if a3_pressed.get():
                a3_pressed.set(False)
                win_settings()
            if b1_pressed.get():
                b1_pressed.set(False)
                install_app_dialog()
        except tk.TclError:
            loop.set(False)


def win_settings():
    settings_window = tk.Tk()
    settings_window.title(t('settings') + ' - ' + t('mmLauncher'))
    settings_window.option_add('*Font', 'Helvetica 21')
    with open(relative_file('src/config.json'), 'r') as f:
        config = json.loads(f.read())
    with open(relative_file('src/resources/languages.json'), 'r') as f:
        languages = json.loads(f.read())
    a1 = tk.Label(settings_window, text=t('Language') + ': ')
    a2_options = list(languages.keys())
    a2_selected = tk.StringVar(settings_window)
    a2_selected.set(config['language'])
    a2_changed = tk.BooleanVar()
    a2_changed.set(False)
    a2 = tk.OptionMenu(settings_window, a2_selected, *a2_options, command=lambda x: a2_changed.set(True))
    a1.grid(row=0, column=0)
    a2.grid(row=0, column=1)
    loop = tk.BooleanVar()
    loop.set(True)
    while loop.get():
        try:
            settings_window.update()
            if a2_changed.get():
                a2_changed.set(False)
                with open(relative_file('src/config.json'), 'r') as f:
                    config = json.loads(f.read())
                config['language'] = a2_selected.get()
                with open(relative_file('src/config.json'), 'w') as f:
                    json.dump(config, f, indent=4)
        except tk.TclError:
            loop.set(False)


def win_app_settings(name: str):
    if name == 'None':
        return None
    app_settings_window = tk.Tk()
    app_settings_window.title(name + ' ' + t('settings') + ' - ' + t('mmLauncher'))
    a1_pressed = tk.BooleanVar()
    a1_pressed.set(False)
    a1 = tk.Button(app_settings_window, text=t('delete app'), command=lambda: a1_pressed.set(True))
    b1_selected = tk.IntVar(app_settings_window)
    if name in get_favourites():
        b1_selected.set(1)
    else:
        b1_selected.set(0)
    b1_changed = tk.BooleanVar()
    b1_changed.set(False)
    b1 = tk.Checkbutton(app_settings_window, text=t('Favourite'), variable=b1_selected, onvalue=1, offvalue=0, command=lambda: b1_changed.set(True))
    a1.grid(row=0, column=0)
    b1.grid(row=1, column=0)
    loop = tk.BooleanVar()
    loop.set(True)
    while loop.get():
        try:
            app_settings_window.update()
            if a1_pressed.get():
                a1_pressed.set(False)
                option = messagebox.askyesnocancel(t('mmLauncher'), t('Do you want to proceed? This action cannot be undone!'))
                if option:
                    delete_app(name)
            if b1_changed.get():
                print(0)
                print(b1_selected.get() + 10)
                print(name in get_favourites())
                b1_changed.set(False)
                if b1_selected.get() == 1 and name not in get_favourites():
                    print(1)
                    x = get_favourites()
                    with open(relative_file('src/userdata/favourites.list'), 'w') as f:
                        f.write(str(x + [name]))
                elif b1_selected.get() == 0 and name in get_favourites():
                    print(2)
                    x = get_favourites()
                    x.remove(name)
                    with open(relative_file('src/userdata/favourites.list'), 'w') as f:
                        f.write(str(x))
        except tk.TclError:
            loop.set(False)


def launch_app_thread(name: str):
    os.system('python3 ' + relative_file('src/apps/' + name + '/main.py'))


def launch_app(name: str):
    with open(relative_file('src/userdata/usage.json'), 'r') as f:
        x = json.loads(f.read())
    x[name] += 1
    with open(relative_file('src/userdata/usage.json'), 'w') as f:
        json.dump(x, f, indent=4)
    if name == 'None':
        return None
    threading.Thread(target=launch_app_thread, args=(name, )).start()


def win_library_start():
    window_library_start = tk.Tk()
    window_library_start.title(t('mmLauncher'))
    window_library_start.option_add('*Font', 'Helvetica 32')
    a1_pressed = tk.BooleanVar()
    a1_pressed.set(False)
    a1 = tk.Button(window_library_start, text=t('Store'), command=lambda: a1_pressed.set(True), width=12)
    a2_pressed = tk.BooleanVar()
    a2_pressed.set(False)
    a2 = tk.Button(window_library_start, text=t('Library'), command=lambda: a2_pressed.set(True), width=12, state=tk.DISABLED)
    a3_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/settings_icon.gif'))
    a3_pressed = tk.BooleanVar()
    a3_pressed.set(False)
    a3 = tk.Button(window_library_start, image=a3_img, command=lambda: a3_pressed.set(True))
    bc1_pressed = tk.BooleanVar()
    bc1_pressed.set(False)
    b1_img = tk.PhotoImage(master=window_library_start, file=get_favourites_img(0))
    b1 = tk.Button(window_library_start, image=b1_img, command=lambda: bc1_pressed.set(True))
    bc2_pressed = tk.BooleanVar()
    bc2_pressed.set(False)
    b2_img = tk.PhotoImage(master=window_library_start, file=get_favourites_img(1))
    b2 = tk.Button(window_library_start, image=b2_img, command=lambda: bc2_pressed.set(True))
    bc3_pressed = tk.BooleanVar()
    bc3_pressed.set(False)
    b3_img = tk.PhotoImage(master=window_library_start, file=get_favourites_img(2))
    b3 = tk.Button(window_library_start, image=b3_img, command=lambda: bc3_pressed.set(True))
    bc4_pressed = tk.BooleanVar()
    bc4_pressed.set(False)
    b4_img = tk.PhotoImage(master=window_library_start, file=get_favourites_img(3))
    b4 = tk.Button(window_library_start, image=b4_img, command=lambda: bc4_pressed.set(True))
    window_library_start.option_add('*Font', 'Helvetica 12')
    c1 = tk.Button(window_library_start, text=t('Launch') + ' ' + get_favourites_name(0, False) + ' ' + t('_Launch2'), command=lambda: bc1_pressed.set(True), width=32)
    c2 = tk.Button(window_library_start, text=t('Launch') + ' ' + get_favourites_name(1, False) + ' ' + t('_Launch2'), command=lambda: bc2_pressed.set(True), width=32)
    c3 = tk.Button(window_library_start, text=t('Launch') + ' ' + get_favourites_name(2, False) + ' ' + t('_Launch2'), command=lambda: bc3_pressed.set(True), width=32)
    c4 = tk.Button(window_library_start, text=t('Launch') + ' ' + get_favourites_name(3, False) + ' ' + t('_Launch2'), command=lambda: bc4_pressed.set(True), width=32)
    if get_favourites_name(0, True) == 'None':
        c1.config(state=tk.DISABLED, text='')
        b1.config(state=tk.DISABLED)
    if get_favourites_name(1, True) == 'None':
        c2.config(state=tk.DISABLED, text='')
        b2.config(state=tk.DISABLED)
    if get_favourites_name(2, True) == 'None':
        c3.config(state=tk.DISABLED, text='')
        b3.config(state=tk.DISABLED)
    if get_favourites_name(3, True) == 'None':
        c4.config(state=tk.DISABLED, text='')
        b4.config(state=tk.DISABLED)
    d1 = tk.Label(window_library_start, text=t('sort by') + ':')
    d2_options = [t('name'), t('usage')]
    d2_selected = tk.StringVar(window_library_start)
    d2_selected.set(d2_options[0])
    d2_changed = tk.BooleanVar()
    d2_changed.set(False)
    d2 = tk.OptionMenu(window_library_start, d2_selected, *d2_options, command=lambda x: d2_changed.set(True))
    d2.config(width=6)
    d8_var = tk.DoubleVar()
    d8_var.set(0)
    d8_changed = tk.BooleanVar()
    d8_changed.set(False)
    d8 = tk.Scale(window_library_start, variable=d8_var, from_=0, to=1, command=lambda x: d8_changed.set(True), length=300)
    e1_img = tk.PhotoImage(master=window_library_start, file=get_app_img(0))
    e1 = tk.Label(window_library_start, image=e1_img)
    e2 = tk.Label(window_library_start, text=get_app_attribute(0, 'description'), wraplength=1024, justify=tk.LEFT)
    e6_pressed = tk.BooleanVar()
    e6_pressed.set(False)
    e6 = tk.Button(window_library_start, text=t('Launch'), command=lambda: e6_pressed.set(True), width=10, font='Helvetica 24')
    e7_pressed = tk.BooleanVar()
    e7_pressed.set(False)
    if get_app_name(0, True) == 'None':
        e6.config(state=tk.DISABLED, text='')
        e7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/Empty_small.gif'))
        e7 = tk.Button(window_library_start, image=e7_img, state=tk.DISABLED, command=lambda: e7_pressed.set(True))
    else:
        e7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/settings_icon.gif'))
        e7 = tk.Button(window_library_start, image=e7_img, command=lambda: e7_pressed.set(True))
    f1_img = tk.PhotoImage(master=window_library_start, file=get_app_img(1))
    f1 = tk.Label(window_library_start, image=f1_img)
    f2 = tk.Label(window_library_start, text=get_app_attribute(1, 'description'), wraplength=1024, justify=tk.LEFT)
    f6_pressed = tk.BooleanVar()
    f6_pressed.set(False)
    f6 = tk.Button(window_library_start, text=t('Launch'), command=lambda: f6_pressed.set(True), width=10, font='Helvetica 24')
    f7_pressed = tk.BooleanVar()
    f7_pressed.set(False)
    if get_app_name(1, True) == 'None':
        f6.config(state=tk.DISABLED, text='')
        f7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/Empty_small.gif'))
        f7 = tk.Button(window_library_start, image=f7_img, state=tk.DISABLED, command=lambda: f7_pressed.set(True))
    else:
        f7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/settings_icon.gif'))
        f7 = tk.Button(window_library_start, image=f7_img, command=lambda: f7_pressed.set(True))
    g1_img = tk.PhotoImage(master=window_library_start, file=get_app_img(2))
    g1 = tk.Label(window_library_start, image=g1_img)
    g2 = tk.Label(window_library_start, text=get_app_attribute(2, 'description'), wraplength=1024, justify=tk.LEFT)
    g6_pressed = tk.BooleanVar()
    g6_pressed.set(False)
    g6 = tk.Button(window_library_start, text=t('Launch'), command=lambda: g6_pressed.set(True), width=10, font='Helvetica 24')
    g7_pressed = tk.BooleanVar()
    g7_pressed.set(False)
    if get_app_name(2, True) == 'None':
        g6.config(state=tk.DISABLED, text='')
        g7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/Empty_small.gif'))
        g7 = tk.Button(window_library_start, image=g7_img, state=tk.DISABLED, command=lambda: g7_pressed.set(True))
    else:
        g7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/settings_icon.gif'))
        g7 = tk.Button(window_library_start, image=g7_img, command=lambda: g7_pressed.set(True))
    h1_img = tk.PhotoImage(master=window_library_start, file=get_app_img(3))
    h1 = tk.Label(window_library_start, image=h1_img)
    h2 = tk.Label(window_library_start, text=get_app_attribute(3, 'description'), wraplength=1024, justify=tk.LEFT)
    h6_pressed = tk.BooleanVar()
    h6_pressed.set(False)
    h6 = tk.Button(window_library_start, text=t('Launch'), command=lambda: h6_pressed.set(True), width=10, font='Helvetica 24')
    h7_pressed = tk.BooleanVar()
    h7_pressed.set(False)
    if get_app_name(3, True) == 'None':
        h6.config(state=tk.DISABLED, text='')
        h7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/Empty_small.gif'))
        h7 = tk.Button(window_library_start, image=h7_img, state=tk.DISABLED, command=lambda: h7_pressed.set(True))
    else:
        h7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/settings_icon.gif'))
        h7 = tk.Button(window_library_start, image=h7_img, command=lambda: h7_pressed.set(True))

    a1.grid(row=0, column=0, columnspan=2)
    a2.grid(row=0, column=2, columnspan=2)
    a3.grid(row=0, column=8, sticky='e')
    b1.grid(row=1, column=0, columnspan=2)
    b2.grid(row=1, column=2, columnspan=2)
    b3.grid(row=1, column=4, columnspan=2)
    b4.grid(row=1, column=6, columnspan=3)
    c1.grid(row=2, column=0, columnspan=2)
    c2.grid(row=2, column=2, columnspan=2)
    c3.grid(row=2, column=4, columnspan=2)
    c4.grid(row=2, column=6, columnspan=3)
    d1.grid(row=3, column=0, sticky='e')
    d2.grid(row=3, column=1, sticky='w')
    d8.grid(row=3, column=8, rowspan=5, sticky='e')
    e1.grid(row=4, column=0)
    e2.grid(row=4, column=1, columnspan=4)
    e6.grid(row=4, column=6, sticky='e')
    e7.grid(row=4, column=7, sticky='w')
    f1.grid(row=5, column=0)
    f2.grid(row=5, column=1, columnspan=4)
    f6.grid(row=5, column=6, sticky='e')
    f7.grid(row=5, column=7, sticky='w')
    g1.grid(row=6, column=0)
    g2.grid(row=6, column=1, columnspan=4)
    g6.grid(row=6, column=6, sticky='e')
    g7.grid(row=6, column=7, sticky='w')
    h1.grid(row=7, column=0)
    h2.grid(row=7, column=1, columnspan=4)
    h6.grid(row=7, column=6, sticky='e')
    h7.grid(row=7, column=7, sticky='w')

    favourites = get_favourites()
    while len(favourites) < 4:
        favourites.append('None')

    app_list = get_app_names()
    app_list.sort()
    while len(app_list) < 4:
        app_list.append('None')

    scroll = 0

    app_list_update = tk.BooleanVar()
    app_list_update.set(True)
    loop = tk.BooleanVar()
    loop.set(True)
    while loop.get():
        try:
            window_library_start.update()
            if a1_pressed.get():
                a1_pressed.set(False)
                window_library_start.destroy()
                loop.set(False)
                win_store()
            if a2_pressed.get():
                a2_pressed.set(False)
            if a3_pressed.get():
                a3_pressed.set(False)
                win_settings()
            if bc1_pressed.get():
                bc1_pressed.set(False)
                launch_app(favourites[0])
            if bc2_pressed.get():
                bc2_pressed.set(False)
                launch_app(favourites[1])
            if bc3_pressed.get():
                bc3_pressed.set(False)
                launch_app(favourites[2])
            if bc4_pressed.get():
                bc4_pressed.set(False)
                launch_app(favourites[3])
            if d2_changed.get():
                d2_changed.set(False)
                if d2_selected.get() == t('usage'):
                    app_list = get_apps_usage()
                    while len(app_list) < 4:
                        app_list.append('None')
                    app_list_update.set(True)
                else:
                    app_list = get_app_names()
                    app_list.sort()
                    while len(app_list) < 4:
                        app_list.append('None')
                    app_list_update.set(True)
            if d8_changed.get():
                d8_changed.set(False)
                scroll = d8.get()
                app_list_update.set(True)
            if e6_pressed.get():
                e6_pressed.set(False)
                launch_app(app_list[0 + scroll])
            if e7_pressed.get():
                e7_pressed.set(False)
                win_app_settings(app_list[0 + scroll])
            if f6_pressed.get():
                f6_pressed.set(False)
                launch_app(app_list[1 + scroll])
            if f7_pressed.get():
                f7_pressed.set(False)
                win_app_settings(app_list[1 + scroll])
            if g6_pressed.get():
                g6_pressed.set(False)
                launch_app(app_list[2 + scroll])
            if g7_pressed.get():
                g7_pressed.set(False)
                win_app_settings(app_list[2 + scroll])
            if h6_pressed.get():
                h6_pressed.set(False)
                launch_app(app_list[3 + scroll])
            if h7_pressed.get():
                h7_pressed.set(False)
                win_app_settings(app_list[3 + scroll])
            if app_list_update.get():
                app_list_update.set(False)
                d8_var.set(0)
                d8.config(to=len(app_list) - 4)
                if app_list[0 + scroll] != 'None':
                    e1_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/apps/' + app_list[0 + scroll] + '/icon.gif'))
                    e1.config(image=e1_img)
                    e2.config(text=get_app_attribute(get_app_names().index(app_list[0 + scroll]), 'description'))
                    e6.config(text=t('Launch'), state=tk.NORMAL)
                    e7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/settings_icon.gif'))
                    e7.config(state=tk.NORMAL, image=e7_img)
                else:
                    e1.config(image='')
                    e2.config(text='')
                    e6.config(text='', state=tk.DISABLED)
                    e7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/Empty_small.gif'))
                    e7.config(state=tk.DISABLED, image=e7_img)
                if app_list[1 + scroll] != 'None':
                    f1_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/apps/' + app_list[1 + scroll] + '/icon.gif'))
                    f1.config(image=f1_img)
                    f2.config(text=get_app_attribute(get_app_names().index(app_list[1 + scroll]), 'description'))
                    f6.config(text=t('Launch'), state=tk.NORMAL)
                    f7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/settings_icon.gif'))
                    f7.config(state=tk.NORMAL, image=f7_img)
                else:
                    f1.config(image='')
                    f2.config(text='')
                    f6.config(text='', state=tk.DISABLED)
                    f7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/Empty_small.gif'))
                    f7.config(state=tk.DISABLED, image=f7_img)
                if app_list[2 + scroll] != 'None':
                    g1_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/apps/' + app_list[2 + scroll] + '/icon.gif'))
                    g1.config(image=g1_img)
                    g2.config(text=get_app_attribute(get_app_names().index(app_list[2 + scroll]), 'description'))
                    g6.config(text=t('Launch'), state=tk.NORMAL)
                    g7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/settings_icon.gif'))
                    g7.config(state=tk.NORMAL, image=g7_img)
                else:
                    g1.config(image='')
                    g2.config(text='')
                    g6.config(text='', state=tk.DISABLED)
                    g7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/Empty_small.gif'))
                    g7.config(state=tk.DISABLED, image=g7_img)
                if app_list[3 + scroll] != 'None':
                    h1_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/apps/' + app_list[3 + scroll] + '/icon.gif'))
                    h1.config(image=h1_img)
                    h2.config(text=get_app_attribute(get_app_names().index(app_list[3 + scroll]), 'description'))
                    h6.config(text=t('Launch'), state=tk.NORMAL)
                    h7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/settings_icon.gif'))
                    h7.config(state=tk.NORMAL, image=h7_img)
                else:
                    h1.config(image='')
                    h2.config(text='')
                    h6.config(text='', state=tk.DISABLED)
                    h7_img = tk.PhotoImage(master=window_library_start, file=relative_file('src/resources/Empty_small.gif'))
                    h7.config(state=tk.DISABLED, image=h7_img)
        except tk.TclError:
            loop.set(False)


def main():
    try:
        root = tk.Tk()
        root.withdraw()
        if not os.path.exists(relative_file('src/')):
            setup()
        with open(__file__, 'rb') as f:
            x = f.read()
        h = SHA3_256.new()
        h.update(x)
        log('started mmLauncher: ' + h.hexdigest())
        win_library_start()
    except Exception as e:
        log('ERROR: ' + str(e).replace('\n', '\\n'))
        raise e


if __name__ == '__main__':
    main()
