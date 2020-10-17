from midiutil import MIDIFile
import cv2
import os


def get_info():
    video_path = ''
    save_path = ''
    lowest_key = 0
    total_keys = 127
    bpm = 120
    search_height = 0.74

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
            save_path += '.mid' if save_path[-4:] != '.mid' else ''
            test_file = open(save_path, 'wb')
            test_file.close()
            os.remove(save_path)
        except Exception as e:
            print('Incorrect path given: ' + str(e))
            continue
        break
    # lowest_key
    while 1:
        lowest_key_input = input('What is the lowest note on the displayed keyboard? (0 - 127; defaults to 21 = A1)\n')
        if lowest_key_input == '':
            lowest_key = 21
            break
        try:
            lowest_key = int(lowest_key_input)
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
        total_keys_input = input('How many Keys are on the displayed keyboard? (defaults to 88)\n')
        if total_keys_input == '':
            total_keys = 88
            break
        try:
            total_keys = int(total_keys_input)
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
        bpm_input = input('What bpm is the song played at? (defaults to 120)\n')
        if bpm_input == '':
            bpm = 120
            break
        try:
            bpm = int(bpm_input)
        except ValueError:
            print('Incorrect Value!')
            continue
        if not (1 <= bpm <= 500):
            print('The number is either too high or too low!')
            continue
        else:
            break
    # search_height
    while 1:
        search_height_input = input('What height should be scanned on? (0 - 1 in %; defaults to 0.74)\n')
        if search_height_input == '':
            search_height = 0.74
            break
        try:
            search_height = float(search_height_input)
        except ValueError:
            print('Incorrect Value!')
            continue
        if not (0 <= search_height <= 1):
            print('The number is either too high or too low!')
            continue
        else:
            break

    return {'video_path': video_path,
            'save_path': save_path,
            'lowest_key': lowest_key,
            'total_keys': total_keys,
            'bpm': bpm,
            'search_height': search_height}


def frames_to_beats(frames, fps, bpm):
    return (frames / fps) * (bpm / 60)


def get_pixel(image, x, y):
    return [rgb for rgb in image[y][x]]


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

        def adjacent_key(previous, offset=1):
            return keys[current_key - offset] if previous else keys[(current_key + offset) % len(keys)]

        white_offset = 1/2
        black_offset = 0
        if keys[current_key] == 'W':
            if adjacent_key(True) == 'B' and adjacent_key(False) == 'W':
                white_offset = 3/4
            elif adjacent_key(True) == 'W' and adjacent_key(False) == 'B':
                white_offset = 1/4
            elif adjacent_key(True) == 'B' and adjacent_key(False) == 'B':
                if adjacent_key(True) == 'B' and adjacent_key(False, 3) == 'B':
                    white_offset = 1/3
                elif adjacent_key(True, 3) == 'B' and adjacent_key(False) == 'B':
                    white_offset = 2/3
        elif keys[current_key] == 'B':
            if adjacent_key(True, 2) == 'B' and adjacent_key(False, 2) == 'W':
                black_offset = 1/10
            elif adjacent_key(True, 2) == 'W' and adjacent_key(False, 2) == 'B':
                black_offset = -1/10

        if keys[current_key] == 'W':
            coord = round(white_key_width * (counted_white_keys + white_offset))
            coord = video_width if coord > video_width else coord
            coords.append(coord)
            key_colors.append('W')
            counted_white_keys += 1
        elif keys[current_key] == 'B':
            coord = round(white_key_width * (counted_white_keys + black_offset))
            coord = video_width if coord > video_width else coord
            coords.append(coord)
            key_colors.append('B')

    return [coords, key_colors]


def colors_similar(color1, color2, threshold=15):
    # Calculate differences
    differences = [color1[i] - color2[i] for i in range(3)]
    differences = [int((i ** 2) ** 0.5) for i in differences]  # Make everything positive

    # Test if similar
    return [i < threshold for i in differences] == [True, True, True]


def gray_color(mode, color, threshold=50):
    test1 = [i > 150 for i in color] if mode == 'white' else [i < 105 for i in color]
    test2 = max(color) - min(color) < threshold
    return [test1, test2] == [[True, True, True], True]


def get_pressed_keys(image, pixels, pixel_y):
    output = []

    for key, coord in enumerate(pixels):
        new_color = get_pixel(image, coord, pixel_y)
        if gray_color('black', new_color) or gray_color('white', new_color):
            continue
        else:
            output.append(key)

    return output


def keys_visible(image, pixels, key_colors, video_height):
    pixel_y = round(video_height * 0.95)
    results = []
    for pixel, pixel_x in enumerate(pixels):
        key_color = key_colors[pixel]
        if key_color == 'B':
            continue
        results.append(gray_color('white', get_pixel(image, pixel_x, pixel_y)))
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
    return output[1:]


def write_midi(note_list, fps):
    # Create midi object
    midi = MIDIFile(1, file_format=1)

    # Add Tempo
    midi.addTempo(0, 0, info['bpm'])
    # Add instrument
    midi.addProgramChange(0, 0, 0, 0)  # Piano

    # Add notes
    for frame in range(len(note_list)):
        for note in note_list[frame]:
            midi.addNote(0, 0, note[0] + info['lowest_key'], frames_to_beats(frame, fps, info['bpm']),
                         frames_to_beats(note[1], fps, info['bpm']), 100)

    # Save MIDI file
    with open(info['save_path'], 'wb') as file:
        midi.writeFile(file)


def process_video():
    video_path = info['video_path']
    video = cv2.VideoCapture(video_path)
    video_height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    loops = 0
    saved_frames = 0
    pixels, key_colors = calculate_pixel_coords(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    pixel_y = round(video_height * 23/27)
    pressed_keys = []
    midi_started = False

    while 1:
        ret, frame = video.read()
        if saved_frames % 500 == 0:
            print('Scanned through %d frames' % saved_frames)
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if not keys_visible(frame, pixels, key_colors, video_height) and not midi_started:
                saved_frames += 1
                continue
            elif not keys_visible(frame, pixels, key_colors, video_height) and midi_started:
                break
            elif keys_visible(frame, pixels, key_colors, video_height) and not midi_started:
                midi_started = True

            pressed_keys.append(get_pressed_keys(frame, pixels, pixel_y))
            saved_frames += 1
        elif not ret:
            print('Scanned through %d frames' % saved_frames)
            break
        loops += 1

    write_midi(convert_note_list(pressed_keys), video.get(cv2.CAP_PROP_FPS))

    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    info = get_info()
    process_video()
