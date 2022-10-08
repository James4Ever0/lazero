import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--search", action='store_true', default=False)
    parser.add_argument("-i","--index", type=str,help='create search index for files in given directory', default=None)
    parser.add_argument("-f",'--ffmpeg-filters', help="show ffmpeg filters", action="store_true", default=False)
    parser.add_argument('-r','--randomize', help='randomize output', action='store_true', default=False)
    flags = parser.parse_args()
    # print(dir(flags))
    randomize=False

    if flags.index:
        from lazero.search.api import mainIndexer
        mainIndexer(flags.index)
    elif flags.search:
        from lazero.search.terminal_interface import run
        run() # default to search for our dearly documents.
    elif flags.ffmpeg_filters:
        if flags.randomize:
            randomize=True
        if randomize:
            command = """ffmpeg -filters 2>/dev/null | grep "\\->" | awk '{print $2}' | shuf | xargs -iabc bash -e -c "ffmpeg -h filter=abc 2>/dev/null ; echo '________________________________________';echo;if [ $? -ne 0 ] ; then exit 255; fi" | less"""
        else:
            command = """ffmpeg -filters 2>/dev/null | grep "\\->" | awk '{print $2}' | xargs -I abc bash -c "ffmpeg -h filter=abc 2>/dev/null ; echo '________________________________________'; echo ; if [ $? -ne 0 ] ; then exit 255; fi" | less"""
        # os.system(command)
        import subprocess
        subprocess.run(command, shell=True)
    else:
        parser.print_help()
