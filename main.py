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

    return {'video_path': video_path,
            'save_path': save_path,
            'start_sec': start_sec,
            'end_sec': end_sec,
            'lowest_key': lowest_key,
            'total_keys': total_keys,
            'bpm': bpm,
            'start_delay': start_delay}


def calculate_pixel_coords(video_width):
    coords = []
    key_colors = []
    lowest_key = info['lowest_key']

    # Count total white keys
    keys = list('WBWBWWBWBWBW')
    total_white_keys = 0
    for key in range(info['total_keys']):
        total_white_keys += 1 if keys[(key + lowest_key) % len(keys)] == 'W' else 0

    # Calculate average pixel width of white keys
    white_key_width = video_width / total_white_keys

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
            coords.append(round(white_key_width * (counted_white_keys + white_offset)))
            key_colors.append('W')
            counted_white_keys += 1
        elif keys[current_key] == 'B':
            coords.append(round(white_key_width * (counted_white_keys + black_offset)))
            key_colors.append('B')

    return [coords, key_colors]


def colors_similar(color1, color2, threshold=15):
    # Calculate differences
    differences = [color1[i] - color2[i] for i in range(3)]
    differences = [int((i ** 2) ** 0.5) for i in differences]  # Make everything positive

    # Test if similar
    return [i < threshold for i in differences] == [True, True, True]


def gray_color(mode, color, threshold=30):
    test1 = [i > 150 for i in color] if mode == 'white' else [i < 105 for i in color]
    test2 = max(color) - min(color) < threshold
    return [test1, test2] == [[True, True, True], True]


def get_pressed_keys(image, pixels, pixel_y):
    output = []

    for key, coord in enumerate(pixels):
        new_color = image.getpixel((coord, pixel_y))
        if colors_similar([0, 0, 0], new_color, 50) or gray_color('white', new_color):
            continue
        else:
            output.append(key)
            for saved_color in saved_colors:
                if not colors_similar(new_color, saved_color):
                    saved_colors.append(new_color)

    return output


def keys_visible(image, pixels, key_colors):
    pixel_y = round(image.height * 0.95)
    results = []
    for pixel in range(len(pixels)):
        key_color = key_colors[pixel]
        if key_color == 'B':
            continue
        results.append(gray_color('white', image.getpixel((pixels[pixel], pixel_y))))
    return results.count(True) > len(results) * 2/3


def convert_note_list(note_list):
    output = []
    not_new = []
    note_list.append([])
    for frame, pressed_keys in enumerate(note_list):
        output.append([])
        for count, key in enumerate(not_new):
            if key not in pressed_keys:
                del not_new[count]
        for key in pressed_keys:
            if key in not_new:
                continue
            else:
                not_new.append(key)
                duration = 1
                while key in note_list[frame + duration]:
                    duration += 1
                output[frame].append([key, duration])
    return output


def process_video():
    video_path = info['video_path']
    video = cv2.VideoCapture(video_path)
    loops = 0
    saved_frames = 0
    pixels, key_colors = calculate_pixel_coords(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    pixel_y = round(video.get(cv2.CAP_PROP_FRAME_HEIGHT) * 20 / 27)
    pressed_keys = []
    midi_started = False

    while 1:
        ret, frame = video.read()
        if saved_frames % 500 == 0:
            print(saved_frames)
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(frame)

            if not keys_visible(pil_frame, pixels, key_colors) and not midi_started:
                saved_frames += 1
                continue
            elif not keys_visible(pil_frame, pixels, key_colors) and midi_started:
                break
            elif keys_visible(pil_frame, pixels, key_colors) and not midi_started:
                midi_started = True

            pressed_keys.append(get_pressed_keys(pil_frame, pixels, pixel_y))
            saved_frames += 1
        elif not ret:
            break
        loops += 1

    video.release()
    cv2.destroyAllWindows()

    print('Writing file...')
    with open('pressed_keys.txt', 'w') as file:
        pressed_keys_text = ''
        for line in pressed_keys:
            pressed_keys_text += str(line) + '\n'
        file.write(pressed_keys_text)

    print('Writing 2nd file...')
    with open('pressed_keys_converted.txt', 'w') as file:
        pressed_keys_text = ''
        for line in convert_note_list(pressed_keys):
            pressed_keys_text += str(line) + '\n'
        file.write(pressed_keys_text)


if __name__ == '__main__':
    temp_folder = 'Video2Midi_temp/'
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    saved_colors = []
    info = {'video_path': 'S:/Python/Midi/Video2Midi/Test_Videos/'
                          'DK Summit (from Mario Kart Wii) - Piano Tutorial_480p.mp4',
            'save_path': 'test.mid',
            'start_sec': 2,
            'end_sec': 120,
            'lowest_key': 9,
            'total_keys': 88,
            'bpm': 180,
            'start_delay': 4}
    process_video()
