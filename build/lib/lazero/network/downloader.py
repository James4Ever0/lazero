# from argparse import ArgumentParser
import requests

import enum
import os
from tqdm import tqdm


class sizeUnit(enum.Enum):
    # class to store the various units
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4


def unitConvertor(sizeInBytes, unit):
    # Cinverts the file unit
    if unit == sizeUnit.KB:
        return sizeInBytes / 1024
    elif unit == sizeUnit.MB:
        return sizeInBytes / (1024 * 1024)
    elif unit == sizeUnit.GB:
        return sizeInBytes / (1024 * 1024 * 1024)
    else:
        return sizeInBytes


def fileSize(filePath, size_type):
    """File size in KB, MB and GB"""
    size = os.path.getsize(filePath)
    return unitConvertor(size, size_type)


def pyCURLFileSizeProbe(url):
    from io import StringIO

    STATUS_OK = (200, 203, 206)
    STATUS_ERROR = range(400, 600)
    import pycurl

    ss = StringIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.MAXREDIRS, 5)
    curl.setopt(pycurl.CONNECTTIMEOUT, 30)
    curl.setopt(pycurl.TIMEOUT, 300)
    curl.setopt(pycurl.NOSIGNAL, 1)
    curl.setopt(pycurl.NOPROGRESS, 1)
    curl.setopt(pycurl.NOBODY, 1)
    curl.setopt(pycurl.HEADERFUNCTION, ss.write)
    curl.setopt(pycurl.URL, url)

    try:
        curl.perform()
    except:
        pass
    size = None
    if curl.errstr() == "" and curl.getinfo(pycurl.RESPONSE_CODE) in STATUS_OK:
        # url_info['url'] = curl.getinfo(pycurl.EFFECTIVE_URL)
        # url_info['file'] = os.path.split(url_info['url'])[1]
        size = int(curl.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD))
    else:
        try:
            size = int(curl.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD))
        except:
            pass
        print("PYCURL ERROR:", curl.errstr())
        try:
            print("RESPONSE CODE:", curl.getinfo(pycurl.RESPONSE_CODE))
        except:
            print("FAILED TO GET RESPONSE CODE")
    curl.close()
    return size


def pyCURLDownload(url, download_path, timeout: int = 120):
    import pycurl

    file_name = download_path
    file_src = url

    with open(file_name, "wb") as f:
        cl = pycurl.Curl()
        cl.setopt(pycurl.URL, file_src)
        cl.setopt(pycurl.WRITEDATA, f)
        cl.setopt(pycurl.TIMEOUT, timeout)
        cl.perform()
        cl.close()


# from retry import retry
# @retry(tries=2)


def download_external():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=True, help="URL to download")
    parser.add_argument(
        "--filename", type=str, required=True, help="filename to write content to"
    )
    parser.add_argument("--config", type=str, default="{}", help="config json string")
    args = parser.parse_args()
    import json

    config_input = json.loads(args.config)
    assert type(config_input) == dict
    config = {
        "allow_redirects": True,
        "show_progress": True,
        "use_multithread": True,
        "threads": 6,
        "max_threads": 100,
        "min_threads": 4,
        "redownload": False,
        "timeout": 30,  # will that work?
        "size_filter": {},  # in megabytes?
        "skip_verification": True,
    }
    config.update(config_input)
    config.update({"external": False})
    download(args.url, args.filename, **config)


def download(
    url,
    filename,
    allow_redirects=True,
    show_progress=True,
    use_multithread=True,
    threads: float = 6,
    use_proxy: bool = False,
    max_threads=100,
    min_threads=4,
    redownload=False,
    timeout=30,  # will that work?
    size_filter: dict = {},  # in megabytes?
    skip_verification: bool = True,
    external: bool = True,  # set it to True in our damn project.
):
    if external:
        print("using external downloader")
        import subprocess

        commandArgs = {
            "allow_redirects": allow_redirects,
            "show_progress": show_progress,
            "use_multithread": use_multithread,
            "threads": threads,
            "max_threads": max_threads,
            "min_threads": min_threads,
            "redownload": redownload,
            "timeout": timeout,  # will that work?
            "size_filter": size_filter,  # in megabytes?
            "skip_verification": skip_verification,
            "external": False,
        }
        import json

        commandArgs = json.dumps(commandArgs)
        try:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "lazero.network.downloader",
                    "--url",
                    url,
                    "--filename",
                    filename,
                    "--config",
                    commandArgs,
                ],
                shell=False,
                timeout=timeout,
            )
            return result.returncode == 0 and os.path.exists(
                filename
            )  # check if this succeeds
        except:
            print("downloader timeout")
            return False
    if skip_verification:
        import requests_skip_verify
        requests_skip_verify.set(True)
    if not use_proxy:
        os.environ["http_proxy"] = ""
        os.environ["https_proxy"] = ""
    min_size_filter = size_filter.get("min", None)
    max_size_filter = size_filter.get("max", None)
    use_requests = True
    # try:
    with requests.get(
        url,
        stream=True,
        allow_redirects=allow_redirects,
        timeout=timeout,
        verify=skip_verification,
    ) as response:
        total = response.headers.get("content-length")
        # except:
        #     use_requests = False
        # import traceback

        # traceback.print_exc()
        # print("unknown requests error. might be open files limit")
        # total = pyCURLFileSizeProbe(url)
        if not redownload:
            if os.path.exists(filename):
                if total:
                    filesize = os.path.getsize(filename)
                    if filesize == total:
                        return True
                else:
                    return True

        basename = os.path.basename(filename)
        one_megabyte = 1024**2

        if total is None:
            if min_size_filter or max_size_filter:
                print(
                    "Not downloading since don't know how to filter file size without server response"
                )
                return False
        else:
            total = int(total)
            size = unitConvertor(total, sizeUnit.MB)
            size = float(size)
            if min_size_filter:
                if size < min_size_filter:
                    print("Min size filter is %.5f MB" % min_size_filter)
                    print("File Size is %.5f MB" % size)
                    print("Not downloading since filtered by min size filter")
                    return False
            if max_size_filter:
                if size > max_size_filter:
                    print("Max size filter is %.5f MB" % max_size_filter)
                    print("File Size is %.5f MB" % size)
                    print("Not downloading since filtered by max size filter")
                    return False
        try:
            # main download section.
            if total is None:
                if use_requests:
                    with open(filename, "wb") as f:
                        print("Downloading %s" % filename)
                        f.write(response.content)
                else:
                    pyCURLDownload(url, filename, timeout=timeout)
            else:
                print("Downloading %s of size %.5f MB" % (basename, size))
                print("Saving at %s" % filename)
                if use_multithread:
                    if threads == 0:
                        threads = 6
                    if threads < 0:
                        # print("TOTAL", total)
                        # print("ONE_MEGABYTE", one_megabyte)
                        # print("-THREADS", -threads)
                        a = one_megabyte * (-threads)
                        # print("ONE_MEGABYTE*(-THREADS)", a)
                        b = total / a
                        # print("TOTAL/A",b)
                        c = round(b)
                        # print("ROUND(B)", c)
                        threads = c
                    threads = int(threads)
                    threads = min(max_threads, max(min_threads, threads))
                    print("using %d threads" % threads)
                    import multithread

                    download_object = multithread.Downloader(
                        url,
                        filename,
                        progress_bar=show_progress,
                        threads=threads,
                        aiohttp_args={
                            "method": "GET",
                            "allow_redirects": allow_redirects,
                            "timeout": timeout,
                            "verify_ssl": skip_verification,
                            "ssl": skip_verification if not skip_verification else None,
                        },
                    )
                    try:
                        import time

                        time.sleep(0.1)  # wtf?
                        download_object.start()
                        time.sleep(0.1)  # wtf?
                        # it might have issue.
                    except:
                        import traceback

                        traceback.print_exc()
                        print("error when using multithread download")
                        import asyncio

                        asyncio.set_event_loop(asyncio.new_event_loop())
                        pyCURLDownload(url, filename, timeout=timeout)
                else:
                    if use_requests:
                        with open(filename, "wb") as f:
                            if show_progress:
                                for data in tqdm(
                                    response.iter_content(
                                        chunk_size=max(int(total / 1000), 1024 * 1024)
                                    )
                                ):
                                    f.write(data)
                            else:
                                f.write(response.content)
                    else:
                        pyCURLDownload(url, filename)
                print("Finished downloading %s of size %.2f MB" % (basename, size))
                print("Saved at %s" % filename)
            return True
        except:
            import traceback

            traceback.print_exc()
            print("Failed to download file %s" % filename)
            print("File URL: %s" % url)
            return False


if __name__ == "__main__":
    download_external()
