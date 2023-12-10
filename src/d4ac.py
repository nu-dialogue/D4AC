from email.policy import default
import socket
import subprocess
import PySimpleGUI as sg
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
    fapid = None
    vipid = None
    dmpid = None
    dspid = None
    mppid = None
    uspid = None
    host = socket.gethostname()
    ip = socket.gethostbyname(host)

    user_layout=[[sg.T("Camera device ID"),
                  sg.In(video_input['device_id'], key='-cameraDeviceId-')],
                 [sg.Checkbox("Recognize speech continuously",
                              default=config['continuous_voice_recognition'],
                              key='-continuousVoiceRecognition-')],
                 [sg.T("Sending user status")],
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
                 [sg.T('interval (sec.)'), sg.Slider(range=(1,60),
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
    dialog_layout =[[sg.T("Dialog server settings")],
                    [sg.T("server_type"),
                     sg.Combo(values=['dummy_dialog', 'xaiml_sunaba', 'dialbb', 'test_dialog'],
                              default_value=dialog['server_type'],
                              key='-serverType-')],
                    [sg.T("BotId (for xaiml_sunaba)"),
                     sg.In(dialog['botId'],key='-botId-')],
                    [sg.T("initTopicId (for xaiml_sunaba)"),
                     sg.In(dialog['initTopicId'],
                           key='-initTopicId-')]]
    postServer_layout = [[sg.T('Posting to the external server')],
                         [sg.Checkbox('Post dialog server outputs to the external server',
                                      key='-postServer-',
                                      default=post['enable'],
                                      enable_events=True)],
                         [sg.T('External server URL'),
                          sg.Input(post['url'], key='-postServerUrl-',
                                   disabled=not post['enable'])]]
    main_col = sg.Column([[sg.Frame('D4AC', [
        [sg.T("IP address of this PC: " + ip)],
        [sg.T('Path of D4AC package: ' + dir)],
        [sg.T('dialog_server'),
         sg.Button('start',key='-dsStart-'),
         sg.T('stopeed', key='-dsStatus-'),
         sg.Button('stop', key='-dsEnd-',disabled = True)],
        [sg.T('d4ac_main'),
         sg.Button('start', key='-dmStart-'),
         sg.T('stopped', key='-dmStatus-'),
         sg.Button('stop', key='-dmEnd-', disabled = True)],
        [sg.T('video_input'),
         sg.Button('start',key='-viStart-'),
         sg.T('stopped',key='-viStatus-'),
         sg.Button('stop',key='-viEnd-',disabled = True),
         sg.T("Web client only")]])]])
    
    userstatus_col = sg.Column([
                 [sg.Frame('face++',[[sg.T('face++'),
                                      sg.Button('start', key='-fpStart-'),
                                      sg.T('stopped', key='-fpStatus-'),
                                      sg.Button('stop', key='-fpEnd-',disabled = True)]] )],
                 [sg.Frame('mediapipe (Windows only)',
                           [[sg.T('mediapipe'),
                             sg.Button('stop', key='-mpStart-', disabled=not windows),
                             sg.T('stopped', key='-mpStatus-'),
                             sg.Button('stop', key='-mpEnd-', disabled = True)],
                    [sg.T('userstatus'),
                     sg.Button('stop', key='-usStart-', disabled=not windows),
                     sg.T('stopped', key='-usStatus-'),
                     sg.Button('stop', key='-usEnd-',disabled= True)]
                ])]
                ])
    start_layout = [
                    [main_col],
                    [userstatus_col]
                 ]
    amazon_layout=[[sg.T("Amazon")],
                [sg.T("identityPoolId"),
                 sg.In(amazon['identityPoolId'], key='-identityPoolId-')],
                [sg.T("region"),
                 sg.In(amazon['region'], key='-region-')]]
    facepp_layout=[[sg.T('Face++')],
                [sg.T("API Key"),
                 sg.In(facepp['apikey'], key='-faceppapikey-')],
                [sg.T("API Secret"),
                 sg.In(facepp['secret'], key='-faceppsecret-')]
                ]

    layout = [[sg.TabGroup([[sg.Tab('User status', user_layout),
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
            window['-silenceperiod-'].Update(disabled=disabled)
            window['-silencechanged-'].Update(disabled=disabled)
        elif event == '-postServer-':
            disabled = not values['-postServer-']
            window['-postServerUrl-'].Update(disabled=disabled)
        elif event == '-dsStart-':
            dspid = execute(poetry,windows,'dialog_server/dialog_server.py')
            if not (windows and poetry):
                window['-dsEnd-'].Update(disabled=False)
            window['-dsStatus-'].Update("running")
            window['-dsStart-'].Update(disabled=True)
        elif event == '-dsEnd-':
            dspid.terminate()
            window['-dsEnd-'].Update(disabled=True)
            window['-dsStatus-'].Update("stopped")
            window['-dsStart-'].Update(disabled=False)
            dspid = None
        elif event == '-dmStart-':
            dmpid = execute(poetry,windows,'d4ac_main/d4ac_main.py')
            if not (windows and poetry):
                window['-dmEnd-'].Update(disabled = False)
            window['-dmStatus-'].Update("running")
            window['-dmStart-'].Update(disabled=True)
        elif event == '-dmEnd-':
            dmpid.terminate()
            window['-dmEnd-'].Update(disabled=True)
            window['-dmStatus-'].Update("stopped")
            window['-dmStart-'].Update(disabled=False)
            dmpid = None
        elif event == '-viStart-':
            vipid = execute(poetry,windows,'video_input/video_input.py')
            if not (windows and poetry):
                window['-viEnd-'].Update(disabled = False)
            window['-viStatus-'].Update("running")
            window['-viStart-'].Update(disabled = True)
        elif event == '-viEnd-':
            vipid.terminate()
            window['-viEnd-'].Update(disabled=True)
            window['-viStatus-'].Update("stopped")
            window['-viStart-'].Update(disabled=False)
            vipid = None
        elif event == '-fpStart-':
            fppid = execute(poetry,windows, 'facepp/facepp_client.py')
            if not (windows and poetry):
                window['-fpEnd-'].Update(disabled=False)
            window['-fpStatus-'].Update("running")
            window['-fpStart-'].Update(disabled=True)
        elif event == '-fpEnd-':
            fppid.terminate()
            window['-fpEnd-'].Update(disabled=True)
            window['-fpStatus-'].Update("stopped")
            window['-fpStart-'].Update(disabled=False)
            fppid = None
        elif event == '-usStart-':
            uspid = execute(poetry,windows,'user_status/facepp_client.py')
            if not (windows and poetry):
                window['-usEnd-'].Update(disabled=False)
            window['-usStatus-'].Update("running")
            window['-usStart-'].Update(disabled=True)
        elif event == '-usEnd-':
            uspid.terminate()
            window['-usEnd-'].Update(disabled=True)
            window['-usStatus-'].Update("stopped")
            window['-usStart-'].Update(disabled=False)
            uspid = None
        elif event == '-mpStart-':
            mppid = execute(poetry,windows,'mediapipe/mesh.py')
            if not (windows and poetry):
                window['-mpEnd-'].Update(disabled=False)
            window['-mpStatus-'].Update("running")
            window['-mpStart-'].Update(disabled=True)
        elif event == '-mpEnd-':
            mppid.terminate()
            window['-mpEnd-'].Update(disabled=True)
            window['-mpStatus-'].Update("stopped")
            window['-mpStart-'].Update(disabled=False)
            mppid = None

    window.close()

    if fppid is not None:
        fppid.terminate()
    if fapid is not None:
        fapid.terminate()
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
