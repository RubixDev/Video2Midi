from midiutil import MIDIFile
import cv2
import os


def get_info():
    video_path = ''
    save_path = ''
    lowest_key = 0
    total_keys = 127
    bpm = 120
    max_tracks = 2
    black_mode = False
    old_style = True
    search_height = 0.85

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
    # max_tracks
    while 1:
        max_tracks_input = input('How many different colors are used? (defaults to 2; max 16)\n')
        if max_tracks_input == '':
            max_tracks = 2
            break
        try:
            max_tracks = int(max_tracks_input)
        except ValueError:
            print('Incorrect Value!')
            continue
        if not (1 <= max_tracks <= 16):
            print('The number is either too high or too low!')
            continue
        else:
            break
    # black_mode
    while 1:
        black_mode_input = input('Is your video black MIDI? (y/N)\n')
        if black_mode_input == '' or black_mode_input.upper() == 'N':
            black_mode = False
            break
        elif black_mode_input.upper() == 'Y':
            black_mode = True
            break
        else:
            print('Incorrect Input!')
            continue
    # old_style
    while 1:
        old_style_input = input('Is your video in the old SMB style? (Y/n)\n')
        if old_style_input == '' or old_style_input.upper() == 'Y':
            old_style = True
            break
        elif old_style_input.upper() == 'N':
            old_style = False
            search_height = 0.9
            break
        else:
            print('Incorrect Input!')
            continue

    return {'video_path': video_path,
            'save_path': save_path,
            'lowest_key': lowest_key,
            'total_keys': total_keys,
            'bpm': bpm,
            'max_tracks': max_tracks,
            'black_mode': black_mode,
            'old_style': old_style,
            'search_height': search_height}


def frames_to_beats(frames, fps):
    return (frames / fps) * (info['bpm'] / 60)


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

    distortion = -1

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
                    white_offset = 2/5
                elif adjacent_key(True, 3) == 'B' and adjacent_key(False) == 'B':
                    white_offset = 3/5
        elif keys[current_key] == 'B':
            if adjacent_key(True, 2) == 'B' and adjacent_key(False, 2) == 'W':
                black_offset = 1/10
            elif adjacent_key(True, 2) == 'W' and adjacent_key(False, 2) == 'B':
                black_offset = -1/10

        if keys[current_key] == 'W':
            coord = round(white_key_width * (counted_white_keys + white_offset)
                          + ((distortion * white_key_width/3) if not info['old_style'] else 0))
            coord = video_width if coord > video_width else coord
            coords.append(coord)

            key_colors.append('W')
            counted_white_keys += 1
        elif keys[current_key] == 'B':
            coord = round(white_key_width * (counted_white_keys + black_offset)
                          + ((distortion * white_key_width/2) if not info['old_style'] else 0))
            coord = video_width if coord > video_width else coord
            coords.append(coord)

            key_colors.append('B')

        distortion += 2 / info['total_keys']

    return [coords, key_colors]


def colors_similar(color1, color2, threshold=20):
    return [k > j for j, k in enumerate([len([i for i in [abs(int(color1[d]) - int(color2[d])) for d in range(3)]
                                              if i < (threshold * n)]) for n in [1, 2.5, 4]])] == [True, True, True]


def gray_color(mode, color, variation=50, threshold=105):
    test1 = [True, True, True] if mode == 'gray' else\
        ([i > 255 - threshold for i in color] if mode == 'white' else [i < threshold for i in color])
    test2 = max(color) - min(color) < variation
    return [test1, test2] == [[True, True, True], True]


def nearest_color(color, color_list):
    return min(color_list, key=lambda subject: sum((int(rgb1) - int(rgb2)) ** 2 for rgb1, rgb2 in zip(subject, color)))


def get_pressed_keys(image, pixels, pixel_y):
    pressed_keys = []
    pixel_colors = []

    for key, coord in enumerate(pixels):
        new_color = get_pixel(image, coord, pixel_y)

        if gray_color('black', new_color) or gray_color('white', new_color) or gray_color('gray', new_color):
            continue

        pressed_keys.append(key)
        pixel_colors.append(new_color)

    return [pressed_keys, pixel_colors]


def keys_visible(image, pixels, key_colors, video_height):
    black_mode = info['black_mode']
    pixel_y = round(video_height * 0.95)
    results = []
    for pixel, pixel_x in enumerate(pixels):
        pixel_x = 0 if pixel_x < 0 else pixel_x
        if key_colors[pixel] == 'B':
            continue
        pixel_color = get_pixel(image, pixel_x, pixel_y)
        if not black_mode:
            if True in [colors_similar(saved_color, pixel_color) for saved_color in saved_colors]:
                results.append(True)
            else:
                results.append(gray_color('white', pixel_color))
        else:
            results.append(not gray_color('black', pixel_color))
    return results.count(True) > len(results) * 2/3


def convert_note_list(note_list, tracks):
    output = []
    not_new = []
    note_list.append([])
    for frame, pressed_keys in enumerate(note_list):
        output.append([])

        not_new = [i for i in not_new if i in pressed_keys]

        for count, key in enumerate(pressed_keys):
            if key in not_new:
                continue

            not_new.append(key)
            duration = 1
            while key in note_list[frame + duration]:
                duration += 1
            output[frame].append([key, duration, tracks[frame][count]])
            
    return output[1:]


def get_tracks(pixel_colors, key_colors):
    tracks = []

    for frame, frame_colors in enumerate(pixel_colors):
        tracks.append([])
        for key, color in enumerate(frame_colors):
            if True not in [colors_similar(color, saved_color, (28 if key_colors[key] == 'B' else 20))
                            for saved_color in saved_colors]:
                saved_colors.append(color)
                track = len(saved_colors) - 1
            else:
                track = 0
                while track < 16 and not colors_similar(saved_colors[track], color, 45):
                    track += 1
            tracks[frame].append(track)

    while len([i for i in saved_colors if i != []]) > info['max_tracks']:
        counts = [[frame.count(track) for track in range(len(saved_colors))] for frame in tracks]
        counts = [sum([frame[track] for frame in counts]) for track in range(len(saved_colors))]

        index_to_del = counts.index(min([i for i in counts if i != 0]))
        color_to_del = saved_colors[index_to_del]

        saved_colors[index_to_del] = []

        new_track = saved_colors.index(nearest_color(color_to_del, [i for i in saved_colors if i != []]))
        tracks = [[new_track if i == index_to_del else i for i in frame] for frame in tracks]

    while [] in saved_colors:
        index_to_del = saved_colors.index([])
        del saved_colors[index_to_del]

        if len(saved_colors) == index_to_del:
            break

        for color in range(len(saved_colors) - index_to_del):
            tracks = [[i - 1 if i == index_to_del + color + 1 else i for i in frame] for frame in tracks]

    return tracks


def write_midi(note_list, fps):
    midi = MIDIFile(len(saved_colors))  # Create midi object

    midi.addTempo(0, 0, info['bpm'])  # Add Tempo
    midi.addProgramChange(0, 0, 0, 0)  # Add instrument: Piano

    # Add notes
    for frame in range(len(note_list)):
        for note in note_list[frame]:
            midi.addNote(note[2], 0, note[0] + info['lowest_key'], frames_to_beats(frame, fps),
                         frames_to_beats(note[1], fps), 100)

    # Save MIDI file
    try:
        with open(info['save_path'], 'wb') as file:
            midi.writeFile(file)
    except PermissionError:
        print('No permission to write file!')


def process_video():
    video_path = info['video_path']
    video = cv2.VideoCapture(video_path)
    video_height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    pixels, key_colors = calculate_pixel_coords(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    pixel_y = round(video_height * info['search_height'])

    pressed_keys = []
    pixel_colors = []

    midi_started = False
    loops = 0
    saved_frames = 0
    while 1:
        ret, frame = video.read()
        if saved_frames % 500 == 0:
            print('Scanned through %d frames' % saved_frames)
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            keyboard_visible = keys_visible(frame, pixels, key_colors, video_height)
            if not keyboard_visible and not midi_started:
                saved_frames += 1
                continue
            elif not keyboard_visible and midi_started:
                break
            elif keyboard_visible and not midi_started:
                midi_started = True

            keys_return = get_pressed_keys(frame, pixels, pixel_y)
            pressed_keys.append(keys_return[0])
            pixel_colors.append(keys_return[1])

            saved_frames += 1
        elif not ret:
            break
        loops += 1

    print('Scanned through %d frames' % saved_frames)
    write_midi(convert_note_list(pressed_keys, get_tracks(pixel_colors, key_colors)), video.get(cv2.CAP_PROP_FPS))

    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    saved_colors = []
    info = get_info()
    process_video()
