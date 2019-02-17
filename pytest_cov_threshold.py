# -*- coding: utf-8 -*-
import json
import re
from collections import defaultdict, namedtuple
from pprint import pformat
from pathlib import Path


ThresholdGroup = namedtuple('ThresholdGroup', 'regex pattern threshold')


class ThresholdPlugin:
    """Plugin to support coverage thresholds per module/packet."""

    def __init__(self, config, threshold_data):

        self.config = config
        self.passed = None
        self.failed = None
        self.threshold_groups = {
            pattern: ThresholdGroup(
                regex=re.compile(pattern),
                pattern=pattern,
                threshold=threshold,
            )
            for pattern, threshold in threshold_data.items()
        }

    def pytest_sessionfinish(self, session, exitstatus):
        if not self.threshold_groups:
            # return early if no thresholds
            return

        plugin = session.config.pluginmanager.getplugin('_cov')
        cov = plugin.cov_controller.cov

        if plugin._disabled:
            # coverage plugin disabled return
            return

        file_reporters = cov._get_file_reporters([])

        groups_matches = defaultdict(list)
        for fr in file_reporters:
            relative_filename = fr.relative_filename()
            analysis = cov._analyze(fr)
            pc_covered = analysis.numbers.pc_covered

            for threshold_group in self.threshold_groups.values():
                if threshold_group.regex.match(relative_filename):
                    groups_matches[threshold_group.pattern].append(
                        (relative_filename, pc_covered)
                    )

        self.passed = []
        self.failed = []
        for pattern, matches in groups_matches.items():
            threshold_group = self.threshold_groups[pattern]
            coverage = sum(pc_covered for _, pc_covered in matches) / len(matches)
            if coverage < threshold_group.threshold:
                self.failed.append((threshold_group, coverage, matches))
            else:
                self.passed.append((threshold_group, coverage, matches))

        if self.failed and session.exitstatus == 0:
            session.exitstatus = 1

    def pytest_terminal_summary(self, terminalreporter):
        if self.failed:
            messages = []
            for tg, coverage, matches in self.failed:

                msg = (
                    'FAIL Required test coverage of %(threshold)d%% '
                    'for %(pattern)s not reached. '
                    'coverage: %(coverage).2f%%:\n%(explain)s'
                )

                ctx = {
                    'threshold': tg.threshold,
                    'pattern': tg.pattern,
                    'coverage': coverage,
                    'explain': pformat(matches),
                }
                messages.append(msg % ctx)

            msg = '\nFailed thresholds:\n%(report)s\n'
            ctx = {
                'report': '\n'.join(messages)
            }
            terminalreporter.write(
                msg % ctx,
                **{'red': True, 'bold': True},
            )

        if self.passed:
            messages = []
            for tg, coverage, matches in self.passed:
                msg = (
                    'Required test coverage of %(threshold)d%% '
                    'for %(pattern)s reached. '
                    'Total coverage: %(coverage).2f%%\n'
                )
                ctx = {
                    'threshold': tg.threshold,
                    'pattern': tg.pattern,
                    'coverage': coverage,
                }
                messages.append(msg % ctx)

            msg = '\nPassed thresholds:\n%(report)s\n'
            ctx = {
                'report': '\n'.join(messages)
            }
            terminalreporter.write(
                msg % ctx,
                **{'green': True},
            )


def pytest_addoption(parser):
    """Add options to control coverage."""

    group = parser.getgroup(
        'cov-threshold', 'coverage reporting with threshold per file support',
    )
    group.addoption(
        '--threshold-config', action='store',
        default='.threshold.json', metavar='path',
        help='config file for threshold, default: .threshold.json',
    )


def pytest_configure(config):
    if config.pluginmanager.hasplugin('_cov'):
        config_file = Path(config.getoption('threshold_config'))

        if config_file.exists():
            with config_file.open() as threshold_config:
                threshold_data = json.load(threshold_config)

            config.pluginmanager.register(
                ThresholdPlugin(config, threshold_data),
                '_cov_threshold',
            )
