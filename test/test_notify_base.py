# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Chris Caron <lead2gold@gmail.com>
# All rights reserved.
#
# This code is licensed under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import six
from datetime import datetime
from datetime import timedelta

from apprise.plugins.NotifyBase import NotifyBase
from apprise import NotifyType
from apprise import NotifyImageSize
from timeit import default_timer

# Disable logging for a cleaner testing output
import logging
logging.disable(logging.CRITICAL)


def test_notify_base():
    """
    API: NotifyBase() object

    """

    # invalid types throw exceptions
    try:
        NotifyBase(**{'format': 'invalid'})
        # We should never reach here as an exception should be thrown
        assert(False)

    except TypeError:
        assert(True)

    # invalid types throw exceptions
    try:
        NotifyBase(**{'overflow': 'invalid'})
        # We should never reach here as an exception should be thrown
        assert(False)

    except TypeError:
        assert(True)

    # Bad port information
    nb = NotifyBase(port='invalid')
    assert nb.port is None

    nb = NotifyBase(port=10)
    assert nb.port == 10

    try:
        nb.url()
        assert False

    except NotImplementedError:
        # Each sub-module is that inherits this as a parent is required to
        # over-ride this function. So direct calls to this throws a not
        # implemented error intentionally
        assert True

    try:
        nb.send('test message')
        assert False

    except NotImplementedError:
        # Each sub-module is that inherits this as a parent is required to
        # over-ride this function. So direct calls to this throws a not
        # implemented error intentionally
        assert True

    # Throttle overrides..
    nb = NotifyBase()
    nb.request_rate_per_sec = 0.0
    start_time = default_timer()
    nb.throttle()
    elapsed = default_timer() - start_time
    # Should be a very fast response time since we set it to zero but we'll
    # check for less then 500 to be fair as some testing systems may be slower
    # then other
    assert elapsed < 0.5

    # Concurrent calls should achieve the same response
    start_time = default_timer()
    nb.throttle()
    elapsed = default_timer() - start_time
    assert elapsed < 0.5

    nb = NotifyBase()
    nb.request_rate_per_sec = 1.0

    # Set our time to now
    start_time = default_timer()
    nb.throttle()
    elapsed = default_timer() - start_time
    # A first call to throttle (Without telling it a time previously ran) does
    # not block for any length of time; it just merely sets us up for
    # concurrent calls to block
    assert elapsed < 0.5

    # Concurrent calls could take up to the rate_per_sec though...
    start_time = default_timer()
    nb.throttle(last_io=datetime.now())
    elapsed = default_timer() - start_time
    assert elapsed > 0.5 and elapsed < 1.5

    nb = NotifyBase()
    nb.request_rate_per_sec = 1.0

    # Set our time to now
    start_time = default_timer()
    nb.throttle(last_io=datetime.now())
    elapsed = default_timer() - start_time
    # because we told it that we had already done a previous action (now)
    # the throttle holds out until the right time has passed
    assert elapsed > 0.5 and elapsed < 1.5

    # Concurrent calls could take up to the rate_per_sec though...
    start_time = default_timer()
    nb.throttle(last_io=datetime.now())
    elapsed = default_timer() - start_time
    assert elapsed > 0.5 and elapsed < 1.5

    nb = NotifyBase()
    start_time = default_timer()
    nb.request_rate_per_sec = 1.0
    # Force a time in the past
    nb.throttle(last_io=(datetime.now() - timedelta(seconds=20)))
    elapsed = default_timer() - start_time
    # Should be a very fast response time since we set it to zero but we'll
    # check for less then 500 to be fair as some testing systems may be slower
    # then other
    assert elapsed < 0.5

    # Force a throttle time
    start_time = default_timer()
    nb.throttle(wait=0.5)
    elapsed = default_timer() - start_time
    assert elapsed > 0.5 and elapsed < 1.5

    # our NotifyBase wasn't initialized with an ImageSize so this will fail
    assert nb.image_url(notify_type=NotifyType.INFO) is None
    assert nb.image_path(notify_type=NotifyType.INFO) is None
    assert nb.image_raw(notify_type=NotifyType.INFO) is None

    # Color handling
    assert nb.color(notify_type='invalid') is None
    assert isinstance(
        nb.color(notify_type=NotifyType.INFO, color_type=None),
        six.string_types)
    assert isinstance(
        nb.color(notify_type=NotifyType.INFO, color_type=int), int)
    assert isinstance(
        nb.color(notify_type=NotifyType.INFO, color_type=tuple), tuple)

    # Create an object
    nb = NotifyBase()
    # Force an image size since the default doesn't have one
    nb.image_size = NotifyImageSize.XY_256

    # We'll get an object this time around
    assert nb.image_url(notify_type=NotifyType.INFO) is not None
    assert nb.image_path(notify_type=NotifyType.INFO) is not None
    assert nb.image_raw(notify_type=NotifyType.INFO) is not None

    # But we will not get a response with an invalid notification type
    assert nb.image_url(notify_type='invalid') is None
    assert nb.image_path(notify_type='invalid') is None
    assert nb.image_raw(notify_type='invalid') is None

    # Static function testing
    assert NotifyBase.escape_html("<content>'\t \n</content>") == \
        '&lt;content&gt;&apos;&emsp;&nbsp;\n&lt;/content&gt;'

    assert NotifyBase.escape_html(
        "<content>'\t \n</content>", convert_new_lines=True) == \
        '&lt;content&gt;&apos;&emsp;&nbsp;&lt;br/&gt;&lt;/content&gt;'

    assert NotifyBase.split_path(
        '/path/?name=Dr%20Disrespect', unquote=False) == \
        ['path', '?name=Dr%20Disrespect']

    assert NotifyBase.split_path(
        '/path/?name=Dr%20Disrespect', unquote=True) == \
        ['path', '?name=Dr', 'Disrespect']

    # Give nothing, get nothing
    assert NotifyBase.escape_html("") == ""
    assert NotifyBase.escape_html(None) == ""
    assert NotifyBase.escape_html(object()) == ""

    # Test quote
    assert NotifyBase.unquote('%20') == ' '
    assert NotifyBase.quote(' ') == '%20'
    assert NotifyBase.unquote(None) == ''
    assert NotifyBase.quote(None) == ''


def test_notify_base_urls():
    """
    API: NotifyBase() URLs

    """

    # Test verify switch whih is used as part of the SSL Verification
    # by default all SSL sites are verified unless this flag is set to
    # something like 'No', 'False', 'Disabled', etc.  Boolean values are
    # pretty forgiving.
    results = NotifyBase.parse_url('https://localhost:8080/?verify=No')
    assert 'verify' in results
    assert results['verify'] is False

    results = NotifyBase.parse_url('https://localhost:8080/?verify=Yes')
    assert 'verify' in results
    assert results['verify'] is True

    # The default is to verify
    results = NotifyBase.parse_url('https://localhost:8080')
    assert 'verify' in results
    assert results['verify'] is True

    # Password Handling

    # pass keyword over-rides default password
    results = NotifyBase.parse_url('https://user:pass@localhost')
    assert 'password' in results
    assert results['password'] == "pass"

    # pass keyword over-rides default password
    results = NotifyBase.parse_url(
        'https://user:pass@localhost?pass=newpassword')
    assert 'password' in results
    assert results['password'] == "newpassword"

    # Options
    results = NotifyBase.parse_url('https://localhost?format=invalid')
    assert 'format' not in results
    results = NotifyBase.parse_url('https://localhost?format=text')
    assert 'format' in results
    assert results['format'] == 'text'
    results = NotifyBase.parse_url('https://localhost?format=markdown')
    assert 'format' in results
    assert results['format'] == 'markdown'
    results = NotifyBase.parse_url('https://localhost?format=html')
    assert 'format' in results
    assert results['format'] == 'html'

    results = NotifyBase.parse_url('https://localhost?overflow=invalid')
    assert 'overflow' not in results
    results = NotifyBase.parse_url('https://localhost?overflow=upstream')
    assert 'overflow' in results
    assert results['overflow'] == 'upstream'
    results = NotifyBase.parse_url('https://localhost?overflow=split')
    assert 'overflow' in results
    assert results['overflow'] == 'split'
    results = NotifyBase.parse_url('https://localhost?overflow=truncate')
    assert 'overflow' in results
    assert results['overflow'] == 'truncate'

    # User Handling

    # user keyword over-rides default password
    results = NotifyBase.parse_url('https://user:pass@localhost')
    assert 'user' in results
    assert results['user'] == "user"

    # user keyword over-rides default password
    results = NotifyBase.parse_url(
        'https://user:pass@localhost?user=newuser')
    assert 'user' in results
    assert results['user'] == "newuser"

    # Test invalid urls
    assert NotifyBase.parse_url('https://:@/') is None
    assert NotifyBase.parse_url('http://:@') is None
    assert NotifyBase.parse_url('http://@') is None
    assert NotifyBase.parse_url('http:///') is None
    assert NotifyBase.parse_url('http://:test/') is None
    assert NotifyBase.parse_url('http://pass:test/') is None
