import argparse
import tempfile
import queue
import sys

import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)

import time

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'filename', nargs='?', metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument(
    '-c', '--channels', type=int, default=1, help='number of input channels')
parser.add_argument(
    '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
args = parser.parse_args(remaining)

q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())

# read file text
f = open("news.txt", "r")
news = f.read()
parts = news.split(".")
print(parts[0])

# record
i = 0
for p in parts:
    print("\nPlease read this sentence: \n", p, "\n")
    
    # wait time before record, can skip if want to record continuosly
    print("type 'ok' + enter to start recording")
    inp = input('')
    if inp.strip().lower() != 'ok':
        time.sleep(2)

    # start record
    i += 1
    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])
        args.filename = tempfile.mktemp(prefix='news_record_'+str(i)+'_',
                                            suffix='_17021346.wav', dir='record')

        # Make sure the file is opened before recording anything:
        with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,
                        channels=args.channels, subtype=args.subtype) as file:
            with sd.InputStream(samplerate=args.samplerate, device=args.device,
                                channels=args.channels, callback=callback):
                print('_' * 10 + '♪⁽⁽٩( ᐖ )۶⁾⁾ RECORDING ₍₍٩( ᐛ )۶₎₎♪' + '_' * 10 )
                print('\npress Ctrl+C to stop the recording\n')
                print('_' * 10 + '♪⁽⁽٩( ᐖ )۶⁾⁾ RECORDING ₍₍٩( ᐛ )۶₎₎♪' + '_' * 10 )
                while True:
                    file.write(q.get())

    except KeyboardInterrupt:
        print('\nRecording finished: ' + repr(args.filename))
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))

print("\n▒▓█▇▅▂∩(・ω・)∩▂▅▇█▓▒▒ Finish reading, thank you for your cooperation!")