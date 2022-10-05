import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f",'--ffmpeg-filters', help="show ffmpeg filters", action="store_true", default=False)
    parser.add_argument('-r','--randomize', help='randomize output', action='store_true', default=False)
    flags = parser.parse_args()
    # print(dir(flags))
    randomize=False

    if flags.randomize:
        randomize=True

    if flags.ffmpeg_filters:
        if randomize:
            command = """ffmpeg -filters 2>/dev/null | grep "\\->" | awk '{print $2}' | shuf | xargs -iabc bash -e -c "ffmpeg -h filter=abc 2>/dev/null ; echo '________________________________________';echo;if [ $? -ne 0 ] ; then exit 255; fi" | less"""
        else:
            command = """ffmpeg -filters 2>/dev/null | grep "\\->" | awk '{print $2}' | xargs -I abc bash -c "ffmpeg -h filter=abc 2>/dev/null ; echo '________________________________________'; echo ; if [ $? -ne 0 ] ; then exit 255; fi" | less"""
        # os.system(command)
        import subprocess
        subprocess.run(command, shell=True)
    else:
        parser.print_help()