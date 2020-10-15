from PIL import Image
# from midiutil import MIDIFile
# import threading
import cv2
import os
import shutil


def get_info():
    video_path = ''
    save_path = ''
    start_sec = 0
    end_sec = 10
    lowest_note = 0
    highest_note = 127
    bpm = 120
    start_delay = 4
    pixel_search_height = 333

    # video_path
    while 1:
        try:
            video_path = input('Where is your video located?\n')
            test_file = open(video_path, 'r')
            test_file.close()
        except Exception as e:
            print('Incorrect path given: ' + str(e))
            continue
        break
    # save_path
    while 1:
        try:
            save_path = input('Where should the MIDI file be saved?\n')
            test_file = open(save_path, 'wb')
            test_file.close()
            os.remove(save_path)
        except Exception as e:
            print('Incorrect path given: ' + str(e))
            continue
        break
    # start_sec
    while 1:
        try:
            start_sec = int(input('At what second do the first falling notes appear?\n'))
        except ValueError:
            print('Incorrect Value!')
            continue
        if start_sec < 0:
            print('The number cannot be below 0!')
            continue
        else:
            break
    # end_sec
    while 1:
        try:
            end_sec = int(input('At what second does the song end?\n'))
        except ValueError:
            print('Incorrect Value!')
            continue
        if end_sec < 0 or end_sec <= start_sec:
            print('The number cannot be below 0 or below the starting second!')
            continue
        else:
            break
    # lowest_note
    while 1:
        try:
            lowest_note = int(input('What is the lowest note on the displayed keyboard? (0 - 127; C4 = 48)\n'))
        except ValueError:
            print('Incorrect Value!')
            continue
        if not (0 <= lowest_note <= 127):
            print('The number cannot be below 0 or higher than 127!')
            continue
        else:
            break
    # highest_note
    while 1:
        try:
            highest_note = int(input('What is the highest note on the displayed keyboard? (0 - 127; C4 = 48)\n'))
        except ValueError:
            print('Incorrect Value!')
            continue
        if not (0 <= highest_note <= 127):
            print('The number cannot be below 0 or higher than 127!')
            continue
        else:
            break
    # bpm
    while 1:
        try:
            bpm = int(input('What bpm is the song played at?\n'))
        except ValueError:
            print('Incorrect Value!')
            continue
        if not (1 <= bpm <= 500):
            print('The number is either too high or too low!')
            continue
        else:
            break
    # start_delay
    while 1:
        start_delay_input = input('How many empty beats should be at the beginning of the MIDI file? (defaults to 4)\n')
        if start_delay_input == '':
            start_delay = 4
            break
        try:
            start_delay = int(start_delay_input)
        except ValueError:
            print('Incorrect Value!')
            continue
        if start_delay < 0:
            print('The number cannot be below 0!')
            continue
        else:
            break
    # fps
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.release()

    return {'video_path': video_path,
            'save_path': save_path,
            'start_sec': start_sec,
            'end_sec': end_sec,
            'lowest_note': lowest_note,
            'highest_note': highest_note,
            'bpm': bpm,
            'start_delay': start_delay,
            'fps': fps,
            'pixel_search_height': pixel_search_height}


def process_video(video_path, width=854, height=480):
    os.makedirs(temp_folder + 'frames')
    video = cv2.VideoCapture(video_path)
    loops = 0
    saved_frames = 0

    while 1:
        ret, frame = video.read()
        if saved_frames % 100 == 0:
            print(saved_frames)
        if ret:
            resized_frame = cv2.resize(frame, (width, height), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
            resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            # cv2.imwrite(temp_folder + 'frames/frame%d.jpg' % saved_frames, resized_frame)
            process_image(Image.fromarray(resized_frame))
            saved_frames += 1
        elif not ret:
            break
        loops += 1

    video.release()
    cv2.destroyAllWindows()


def process_image(image):
    pass


if __name__ == '__main__':
    temp_folder = 'Video2Midi_temp/'
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)
    process_video('S:/Python/Midi/Video2Midi/Test_Videos/DK Summit (from Mario Kart Wii) - Piano Tutorial.mp4')
