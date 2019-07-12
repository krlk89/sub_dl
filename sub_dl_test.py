"""Test functions for Subscene subtitle downloader (sub_dl)
   Author: https://github.com/krlk89/sub_dl
"""

import pytest

import sub_dl


def test_check_release_tag():
    assert sub_dl.check_release_tag("test") == "test"
    assert sub_dl.check_release_tag("test[ettv]") == "test"
    assert sub_dl.check_release_tag("test[ettv]-") == "test[ettv]-"

def test_tv_series_or_movie():
   assert sub_dl.tv_series_or_movie("test") == ""
   assert sub_dl.tv_series_or_movie("test.S01E01.") == ".s01e01."
   assert sub_dl.tv_series_or_movie("test.S1E01.") == ".s1e01."
   assert sub_dl.tv_series_or_movie("test.S1E1.") == ".s1e1."
   assert sub_dl.tv_series_or_movie("test.S01E1.") == ".s01e1."