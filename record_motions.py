from sic_framework.devices import Nao
from sic_framework.devices.common_naoqi.naoqi_text_to_speech import NaoqiTextToSpeechRequest
import time
from sic_framework.devices.common_naoqi.naoqi_stiffness import Stiffness
from sic_framework.devices.common_naoqi.common_naoqi_motion import NaoqiMotionTools
from sic_framework.devices.common_naoqi.naoqi_motion_recorder import NaoqiMotionRecorder, StartRecording, StopRecording, \
    PlayRecording, NaoqiMotionRecorderConf

# conf = NaoqiMotionRecorderConf(use_sensors=True)

# recorder = NaoqiMotionRecorder("192.168.0.242", conf=conf)
joints = ['RArm', 'LArm', 'Head']

nao = Nao(ip="10.0.0.89")
NaoqiMotionRecorderConf(replay_speed=0.5)

recordings = [
    'comp_lose',
    'supp_win',
    'supp_lose',
]

for each in recordings:
    nao.stiffness.request(Stiffness(0.0, joints))
    time.sleep(2)
    print('Now recording the motion: ' + str(each))

    nao.motion_record.request(StartRecording(joints))
    
    
    print("Start moving the robot!")

    record_time = 15

    time.sleep(record_time)

    recording = nao.motion_record.request(StopRecording())
    print("Done")
    nao.stiffness.request(Stiffness(0.6, joints))
    print(recording)
    print('Now playing the recording: ' + str(each))
    time.sleep(5)
    nao.motion_record.request(PlayRecording(recording))
    time.sleep(5)
    print('Saving the recording ' + str(each))


    recording.save('recorded_motions/' + str(each) + '.motion')