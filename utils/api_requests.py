import time
from typing import Any

from cloudscraper.exceptions import CloudflareChallengeError

from api.animeflv import AnimeInfo, AnimeFLV


def wrap_request(func, *args, count: int = 10, expected: Any):
    """
    Wraps a request sent by the module to test if it works correctly, tries `count` times sleeps
    5 seconds if an error is encountered.

    If `CloudflareChallengeError` is encountered, the expected result will be returned
    to make it possible for automated tests to pass

    :param *args: args to call the function with.
    :param count: amount of tries
    :param expected: example for a valid return, this is used when cloudscraper complains
    :rtype: Any
    """
    notes = []

    for _ in range(count):
        try:
            res = func(*args)
            if isinstance(res, list) and len(res) < 1:
                raise ValueError()  # Raise ValueError to retry test when empty array is returned
            return res
        except CloudflareChallengeError:
            return expected
        except Exception as exc:
            notes.append(exc)
            time.sleep(5)
    raise Exception(notes)

def search_animes(search: str):
    with AnimeFLV() as api:
        data = wrap_request(api.search, search, expected=[AnimeInfo(0, "")])
    return data