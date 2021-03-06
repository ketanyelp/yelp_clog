# -*- coding: utf-8 -*-
# Copyright 2015 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import subprocess
import sys

import pytest
from staticconf.testing import MockConfiguration

from clog import config


class BlankObject(object):
    pass


class TestConfigure(object):

    @pytest.yield_fixture(autouse=True)
    def setup_config(self):
        with MockConfiguration(namespace=config.namespace) as self.mock_config:
            yield

    def test_clog_enable_stdout_logging_true(self):
        config_data = {
            'clog_enable_stdout_logging': True,
        }
        config.configure_from_dict(config_data)
        assert config.clog_enable_stdout_logging

    def test_clog_enable_stdout_logging_false(self):
        config_data = {
            'clog_enable_stdout_logging': False,
        }
        config.configure_from_dict(config_data)
        assert not config.clog_enable_stdout_logging

    def test_configure_from_dict(self):
        config_data = {
            'scribe_host': 'example.com',
            'scribe_port': '5555',
        }
        config.configure_from_dict(config_data)
        assert config.scribe_host == config_data['scribe_host']
        assert not config.clog_enable_stdout_logging

    def test_configure_from_object(self):
        config_obj = BlankObject()
        config_obj.scribe_host = 'example.com',
        config_obj.scribe_port = 5555
        config.configure_from_object(config_obj)
        assert config.scribe_port == 5555
        assert not config.clog_enable_stdout_logging

    def test_configure(self):
        config.configure('what', '111', scribe_disable=True)
        assert config.scribe_port == 111
        assert config.scribe_host == 'what'
        assert config.scribe_disable == True
        assert not config.clog_enable_stdout_logging

    def test_configure_from_object_changes_scribe_disable(self):
        proc = subprocess.Popen(
            (
                sys.executable, '-c',
                'import clog.config\n'
                'print(clog.config.scribe_disable)\n'
                'class C(object):\n'
                '    scribe_disable = False\n'
                'clog.config.configure_from_object(C)\n'
                'print(clog.config.scribe_disable)\n'
            ),
            stdout=subprocess.PIPE,
        )
        out = proc.communicate()[0].decode('UTF-8')
        assert out == 'True\nFalse\n'
