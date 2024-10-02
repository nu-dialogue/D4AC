#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# d4ac.py
#   main module
# (c) Nagoya University

import socket
import subprocess
import TkEasyGUI as sg
import os
import yaml


def execute(poet,windows,cmd):
    if poet:
        if windows:
            cmd = ['powershell','-Command','poetry','run', 'python'] + [cmd]
        else:
            cmd = ['poetry', 'run', 'python'] + [cmd]
    else:
        cmd = ['python'] + [cmd]
    pid = subprocess.Popen(cmd)
    return pid


def main():
    # sg.theme('DarkAmber')
    f = os.path.abspath(__file__)
    dir = os.path.dirname(f)
    os.chdir(dir)
    if os.name == 'nt':
        windows = True
    else:
        windows = False

    if(os.environ.get('POETRY_ACTIVE') is None):
        poetry = False
    else:
        poetry = True
    if os.path.isfile('config.yml'):
        with open('config.yml') as fp:
            config = yaml.safe_load(fp)
    else:
        with open('config-template.yml') as fp:
            config = yaml.safe_load(fp)

    video_input = config['video_input']
    user_status = config['user_status']
    silence = user_status['silence']
    amazon = config['amazon_polly']
    dialog = config['dialog_server']
    post = config['post_server']
    facepp = config['facepp']

    fppid = None
    vipid = None
    dmpid = None
    dspid = None
    mppid = None
    uspid = None
    host = socket.gethostname()
    ip = socket.gethostbyname(host)

    user_layout=[[sg.Text("Camera device ID"),
                  sg.Input(video_input['device_id'], key='-cameraDeviceId-')],
                 [sg.Checkbox("Recognize speech continuously",
                              default=config['continuous_voice_recognition'],
                              key='-continuousVoiceRecognition-')],
                 [sg.Text("Sending user states")],
                 [sg.Checkbox("Send at the end of user utterances",
                              default=user_status['uu_end']['send'],
                              key='-uu_end-')],
                 [sg.Checkbox("Send at the end of system utterances",
                              default=user_status['su_end']['send'],
                              key='-su_end-')],
                 [sg.Checkbox("Send between system utterance and user utterance",
                              default=silence['send'],
                              key='-silence-',
                              enable_events=True)],
                 [sg.Text('interval (sec.)'), sg.Slider(range=(1,60),
                                                     default_value=silence['period'],
                                                     disabled=not silence['send'],
                                                     orientation='horizontal',
                                                     key='-silenceperiod-')],
                 [sg.Checkbox('Do not send if user status does not change',
                              default=silence['only_upon_changes'],
                              disabled=not silence['send'],
                              key='-silencechanged-')],
                 [sg.Checkbox("Send only when requested",
                              default=user_status['on_request'],
                              key='-on_request-',
                              enable_events=True)],
                 [sg.Checkbox('Send gender and age',
                              default=user_status['send_gender_and_age'],
                              key='-genderage-')]]
    dialog_layout =[[sg.Text("Dialog server settings")],
                    [sg.Text("server_type"),
                     sg.Combo(values=['dummy_dialog', 'xaiml_sunaba', 'dialbb', 'test_dialog'],
                              default_value=dialog['server_type'],
                              key='-serverType-')],
                    [sg.Text("BotId (for xaiml_sunaba)"),
                     sg.Input(dialog['botId'],key='-botId-')],
                    [sg.Text("initTopicId (for xaiml_sunaba)"),
                     sg.Input(dialog['initTopicId'],
                           key='-initTopicId-')]]
    postServer_layout = [[sg.Text('Posting to the external server')],
                         [sg.Checkbox('Post dialog server outputs to the external server',
                                      key='-postServer-',
                                      default=post['enable'],
                                      enable_events=True)],
                         [sg.Text('External server URL'),
                          sg.Input(post['url'], key='-postServerUrl-',
                                   disabled=not post['enable'])]]
    main_col = sg.Column([[sg.Frame('D4AC', [
        [sg.Text("IP address of this PC: " + ip)],
        [sg.Text('Path of D4AC package: ' + dir)],
        [sg.Text('dialog_server'),
         sg.Button('start',key='-dsStart-'),
         sg.Text('stopeed', key='-dsStatus-'),
         sg.Button('stop', key='-dsEnd-', disabled=True)],
        [sg.Text('d4ac_main'),
         sg.Button('start', key='-dmStart-'),
         sg.Text('stopped', key='-dmStatus-'),
         sg.Button('stop', key='-dmEnd-', disabled=True)],
        [sg.Text('video_input'),
         sg.Button('start',key='-viStart-'),
         sg.Text('stopped',key='-viStatus-'),
         sg.Button('stop',key='-viEnd-', disabled=True),
         sg.Text("Web client only")]])]])
    
    userstatus_col = sg.Column([
                 [sg.Frame('face++',[[sg.Text('face++'),
                                      sg.Button('start', key='-fpStart-'),
                                      sg.Text('stopped', key='-fpStatus-'),
                                      sg.Button('stop', key='-fpEnd-',disabled = True)]] )],
                 [sg.Frame('mediapipe (Windows only)',
                           [[sg.Text('mediapipe'),
                             sg.Button('stop', key='-mpStart-', disabled=not windows),
                             sg.Text('stopped', key='-mpStatus-'),
                             sg.Button('stop', key='-mpEnd-', disabled = True)],
                    [sg.Text('userstatus'),
                     sg.Button('stop', key='-usStart-', disabled=not windows),
                     sg.Text('stopped', key='-usStatus-'),
                     sg.Button('stop', key='-usEnd-',disabled= True)]
                ])]
                ])
    start_layout = [
                    [main_col],
                    [userstatus_col]
                 ]
    amazon_layout=[[sg.Text("Amazon")],
                   [sg.Text("identityPoolId"),
                    sg.Input(amazon['identityPoolId'], key='-identityPoolId-')],
                   [sg.Text("region"),
                    sg.Input(amazon['region'], key='-region-')]]
    facepp_layout=[[sg.Text('Face++')],
                   [sg.Text("API Key"),
                    sg.Input(facepp['apikey'], key='-faceppapikey-')],
                   [sg.Text("API Secret"),
                    sg.Input(facepp['secret'], key='-faceppsecret-')]]

    layout = [[sg.TabGroup([[sg.Tab('User states', user_layout),
                             sg.Tab('Dialog server', dialog_layout),
                             sg.Tab('Amazon Polly TTS', amazon_layout),
                             sg.Tab('Post to external server', postServer_layout),
                             sg.Tab('Face++', facepp_layout),
                             sg.Tab('Start processes', start_layout)]])],
              [sg.Button('Save', key='-update-'),
               sg.Button('Close', key='-cancel-')]]

    window = sg.Window("D4AC", layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "-cancel-":
            break
        elif event == '-update-':
            video_input['device_id'] = values['-cameraDeviceId-']
            user_status['uu_end']['send'] = values['-uu_end-']
            user_status['su_end']['send'] = values['-su_end-']
            silence['send'] = values['-silence-']
            silence['period'] = values['-silenceperiod-']
            silence['only_upon_changes'] = values['-silencechanged-']
            user_status['send_gender_and_age'] = values['-genderage-']
            user_status['on_request'] = values['-on_request-']
            amazon['identityPoolId'] = values['-identityPoolId-']
            amazon['region'] = values['-region-']
            dialog['botId'] = values['-botId-']
            dialog['initTopicId'] = values['-initTopicId-']
            dialog['server_type'] = values['-serverType-']
            post['enable'] = values['-postServer-']
            post['url'] = values['-postServerUrl-']
            facepp['apikey'] = values['-faceppapikey-']
            facepp['secret'] = values['-faceppsecret-']
            config['facepp'] = facepp
            config['continuous_voice_recognition'] = values['-continuousVoiceRecognition-']
            user_status['silence'] = silence
            config['user_status'] = user_status
            config['amazon_polly'] = amazon
            config['post_server'] = post
            config['dialog_server'] = dialog
            with open('config.yml', 'w') as file:
                yaml.dump(config, file, encoding='utf-8')
        elif event == '-silence-':
            disabled = not values['-silence-']
            window['-silenceperiod-'].update(disabled=disabled)
            window['-silencechanged-'].update(disabled=disabled)
        elif event == '-postServer-':
            disabled = not values['-postServer-']
            window['-postServerUrl-'].update(disabled=disabled)
        elif event == '-dsStart-':
            dspid = execute(poetry, windows,'dialog_server/dialog_server.py')
            if not (windows and poetry):
                window['-dsEnd-'].update(disabled=False)
            window['-dsStatus-'].update("running")
            window['-dsStart-'].update(disabled=True)
        elif event == '-dsEnd-':
            dspid.terminate()
            window['-dsEnd-'].update(disabled=True)
            window['-dsStatus-'].update("stopped")
            window['-dsStart-'].update(disabled=False)
            dspid = None
        elif event == '-dmStart-':
            dmpid = execute(poetry,windows,'d4ac_main/d4ac_main.py')
            if not (windows and poetry):
                window['-dmEnd-'].update(disabled = False)
            window['-dmStatus-'].update("running")
            window['-dmStart-'].update(disabled=True)
        elif event == '-dmEnd-':
            dmpid.terminate()
            window['-dmEnd-'].update(disabled=True)
            window['-dmStatus-'].update("stopped")
            window['-dmStart-'].update(disabled=False)
            dmpid = None
        elif event == '-viStart-':
            vipid = execute(poetry,windows,'video_input/video_input.py')
            if not (windows and poetry):
                window['-viEnd-'].update(disabled = False)
            window['-viStatus-'].update("running")
            window['-viStart-'].update(disabled = True)
        elif event == '-viEnd-':
            vipid.terminate()
            window['-viEnd-'].update(disabled=True)
            window['-viStatus-'].update("stopped")
            window['-viStart-'].update(disabled=False)
            vipid = None
        elif event == '-fpStart-':
            fppid = execute(poetry,windows, 'facepp/facepp_client.py')
            if not (windows and poetry):
                window['-fpEnd-'].update(disabled=False)
            window['-fpStatus-'].update("running")
            window['-fpStart-'].update(disabled=True)
        elif event == '-fpEnd-':
            fppid.terminate()
            window['-fpEnd-'].update(disabled=True)
            window['-fpStatus-'].update("stopped")
            window['-fpStart-'].update(disabled=False)
            fppid = None
        elif event == '-usStart-':
            uspid = execute(poetry,windows,'user_status/facepp_client.py')
            if not (windows and poetry):
                window['-usEnd-'].update(disabled=False)
            window['-usStatus-'].update("running")
            window['-usStart-'].update(disabled=True)
        elif event == '-usEnd-':
            uspid.terminate()
            window['-usEnd-'].update(disabled=True)
            window['-usStatus-'].update("stopped")
            window['-usStart-'].update(disabled=False)
            uspid = None
        elif event == '-mpStart-':
            mppid = execute(poetry,windows,'mediapipe/mesh.py')
            if not (windows and poetry):
                window['-mpEnd-'].update(disabled=False)
            window['-mpStatus-'].update("running")
            window['-mpStart-'].update(disabled=True)
        elif event == '-mpEnd-':
            mppid.terminate()
            window['-mpEnd-'].update(disabled=True)
            window['-mpStatus-'].update("stopped")
            window['-mpStart-'].update(disabled=False)
            mppid = None

    window.close()

    if fppid is not None:
        fppid.terminate()
    if vipid is not None:
        vipid.terminate()
    if dmpid is not None:
        dmpid.terminate()
    if dspid is not None:
        dspid.terminate()
    if uspid is not None:
        uspid.terminate()
    if mppid is not None:
        mppid.terminate()


if __name__ == "__main__":
    main()
