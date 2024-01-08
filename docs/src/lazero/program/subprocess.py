from typing import Union
import json, subprocess, traceback


def runCommandGetJson(
    commandLine: list[str],
    timeout: int = 5,
    debug: bool = False,
    shell: bool = False,
    workingDirectory: Union[str, None] = None,
):

    try:
        result = subprocess.run(
            commandLine,
            timeout=timeout,
            capture_output=True,
            shell=shell,
            cwd=workingDirectory,
        )
        assert result.returncode == 0
        stdout = result.stdout
        stdout = stdout.decode("utf-8")
        output = json.loads(stdout)
        return True, output
    except:
        if debug:
            traceback.print_exc()
    return False, {}
