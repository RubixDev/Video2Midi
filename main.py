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
    lowest_key = 0
    total_keys = 127
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
    # lowest_key
    while 1:
        try:
            lowest_key = int(input('What is the lowest note on the displayed keyboard? (0 - 127; C4 = 48)\n'))
        except ValueError:
            print('Incorrect Value!')
            continue
        if not (0 <= lowest_key <= 127):
            print('The number cannot be below 0 or higher than 127!')
            continue
        else:
            break
    # total_keys
    while 1:
        try:
            total_keys = int(input('How many Keys are on the displayed keyboard?\n'))
        except ValueError:
            print('Incorrect Value!')
            continue
        if total_keys + lowest_key > 127 or total_keys < 13:
            print('The number is either too high or too low!')
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
    # fps and video_width
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    video_width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    video.release()

    return {'video_path': video_path,
            'save_path': save_path,
            'start_sec': start_sec,
            'end_sec': end_sec,
            'lowest_key': lowest_key,
            'total_keys': total_keys,
            'bpm': bpm,
            'start_delay': start_delay,
            'fps': fps,
            'video_width': video_width,
            'pixel_search_height': pixel_search_height}


def calculate_pixel_coords():
    output = []
    lowest_key = info['lowest_key']

    # Count total white keys
    keys = list('WBWBWWBWBWBW')
    total_white_keys = 0
    for key in range(info['total_keys']):
        total_white_keys += 1 if keys[(key + lowest_key) % len(keys)] == 'W' else 0

    # Calculate average pixel width of white keys
    white_key_width = info['video_width'] / total_white_keys

    # Get x coordinate for each key
    counted_white_keys = 0

    for key in range(info['total_keys']):
        current_key = (key + lowest_key) % len(keys)

        white_offset = 0.5
        black_offset = 0
        if keys[current_key] == 'W':
            if keys[current_key - 1] == 'B' and keys[(current_key + 1) % len(keys)] == 'W':
                white_offset = 0.75
            elif keys[current_key - 1] == 'W' and keys[(current_key + 1) % len(keys)] == 'B':
                white_offset = 0.25
        elif keys[current_key] == 'B':
            if keys[current_key - 2] == 'B' and keys[(current_key + 2) % len(keys)] == 'W':
                black_offset = 0.1
            elif keys[current_key - 2] == 'W' and keys[(current_key + 2) % len(keys)] == 'B':
                black_offset = -0.1

        if keys[current_key] == 'W':
            output.append(round(white_key_width * (counted_white_keys + white_offset)))
            counted_white_keys += 1
        elif keys[current_key] == 'B':
            output.append(round(white_key_width * (counted_white_keys + black_offset)))

    return output


def process_video(video_path):
    video = cv2.VideoCapture(video_path)
    loops = 0
    saved_frames = 0

    while 1:
        ret, frame = video.read()
        if saved_frames % 100 == 0:
            print(saved_frames)
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            get_pressed_keys(Image.fromarray(frame), [])
            saved_frames += 1
        elif not ret:
            break
        loops += 1

    video.release()
    cv2.destroyAllWindows()


def get_pressed_keys(image, pixels):
    pass


if __name__ == '__main__':
    temp_folder = 'Video2Midi_temp/'
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)
    info = {'video_path': 'S:/Python/Midi/Video2Midi/Test_Videos/DK Summit (from Mario Kart Wii) - Piano Tutorial.mp4',
            'save_path': 'test.mid',
            'start_sec': 2,
            'end_sec': 120,
            'lowest_key': 9,
            'total_keys': 88,
            'bpm': 180,
            'start_delay': 4,
            'fps': 60,
            'video_width': 1920,
            'pixel_search_height': 333}
    # process_video(info['video_path'])
    print(calculate_pixel_coords())
