# Changelog

Changelog practices: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning practices: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [ADD NEW VERSION HERE] - ADD DATE HERE
### Fixed
### Added
### Removed
### Changed

## [1.0.17] - 2023-09-08
### Fixed
 - Fix units in HTML report plot hover texts sometimes containing two
   SI-prefixes (e.g. kMHz).
 - Fix HTML reports being generated missing the last data point of 'ipmi' data.
 - Fix 'ipmi' plots in HTML reports being generated with timestamps which are
   inconsistent with raw 'ipmi' statistics files.
 - Fix 'stats-collect start' collecting both 'ipmi-inband' and 'ipmi-oob' data
   when it has already stated that it will disable the former in favour of the
   latter.
 - Fix 'stats-collect report' crashing on plot density reduction if any data
   points were marked with the 'skip' label.
### Changed
 - Change the 'ipmi-oob' 'bmcpwd' property to 'pwdfile' property.
 - Rename the 'bmcuser' and 'bmchost' 'ipmi-oob' properties to 'user' and 'host'
   respectively.
 - Maximum report ID length changed from 64 characters to 128.

## [1.0.16] - 2023-08-23
### Fixed
 - Fix units on plot axes in HTML reports sometimes containing two SI-prefixes
   (e.g. kMHz).
 - Fix diagrams with hover text being generated with huge file sizes.
### Changed
 - Change HTML reports to show "Time Elapsed" in the "hh:mm:ss" format in plots
   (rather than using the integer count of seconds passed, which previously
   resulted in values shown in "ks").

## [1.0.15] - 2023-08-11
### Fixed
 - Fix duplicate report IDs appearing in the trimmed file alert in the 'Captured
   Output' tab.
 - Fix 'stats-collect report' marking all captured output log files as 'trimmed'
   even if they are not trimmed.
 - Fix 'stats-collect start 'cmd'' not killing the process running 'cmd' upon
   keyboard-interrupt.
 - Fix regression introduced in v1.0.14 which caused
   'stats-collect start --stats=none' to crash.
### Changed
 - Increase the line limits of files in the 'Captured Output' tab of HTML
   reports.
 - Change 'stats-collect report' to generate 'turbostat' and 'ipmi' tabs for
   metrics present in any result rather than all results.
 - Change 'Captured Output' tab in HTML reports to generate if any results have
   captured output files rather than only generating if all results have
   captured output files.
 - Change 'stats-collect report' to store 'Captured Output' tab files in a
   dedicated directory.

## [1.0.14] - 2023-07-28
### Added
 - Add 'Report info' section to HTML reports with the name and version of the
   tool used to generate the report.
### Changed
 - Simplify the HTML report directory structure.
 - Generate 'SysInfo' tabs in HTML diffs when one or more results have 'SysInfo'
   data rather than only when all results have 'SysInfo' data.
 - Change 'stats-collect start' to fail if 'cmd' finishes before any significant
   data has been collected.

## [1.0.13] - 2023-07-20
### Added
 - Add logs generated with 'stats-collect start' to HTML reports.

## [1.0.12] - 2023-07-14
### Fixed
 - Fix debian installation.

## [1.0.11] - 2023-07-12
### Fixed
 - Fix 'stats-collect start --time-limt' option.

## [1.0.10] - 2023-06-28
### Fixed
 - Fix 'stats-collect start' to accept command without quotes.
 - Fix 'stats-collect report' crashing on unsupported turbostat metrics.

## [1.0.9] - 2023-06-23
### Changed
 - Change 'stats-collect report' to work for results with no statistics data.
 - Change 'stats-collect report' to not print messages about tabs skipped
   because there is no data for them.

## [1.0.8] - 2023-06-15
### Added
 - Add turbostat requested C-state count visualization.

## [1.0.7] - 2023-06-15
### Added
 - Add report generation logs to report directories.
### Changed
 - Change 'stats-collect start' to raise an error if the user's command fails
   during statistics collection.
 - Change 'stats-collect start' to remove the output directory if no statistics
   were collected.

## [1.0.6] - 2023-06-12

## [1.0.5] - 2023-06-12
### Changed
 - Separate from the 'wult' project.

## [1.0.4] - 2023-06-08
### Fixed
 - Fix statistics collectors.
 - Fix 'stats-collect report' generating broken diffs when given results with
   duplicate report IDs.
 - Fix a bug where 'sysinfo' tabs in HTML reports do not generate diffs.
 - Fix 'Measured CPU' tab generation crashing when the measured CPU of a result
   is not 0.
 - Fix '--stats=ipmi' not resolving to 'ipmi-inband' and 'ipmi-oob' properly.
 - Fix '--stats=ipmi-inband' or '--stats=ipmi-oob' sometimes resulting in the
   other 'ipmi' collection method being used.
 - Fix 'stats-collect start --stats=none' crashing.
 - Fix turbostat tabs failing to generate because of two or more results do not
   have enough turbostat metrics in common.
### Added
 - Add 'stats-collect report --reportids' option.
 - Add 'pepc power info' output to 'pepc SysInfo' tabs in HTML reports.
### Changed
 - Install man page when using 'pip install'.
 - Minor design improvements to HTML report tabs with alerts and file-previews.
 - Change 'stats-collect' to skip generating SysInfo diffs if the files are
   identical to speed up report generation.
 - Changed the default value of 'stats-collect start --cpunum' to 'None'.

## [1.0.3] - 2023-04-21
### Fixed
 - Fix HTML reports not being able to be viewed locally since v1.0.2.
### Added
 - Add 'tool information' and 'collection date' to HTML report intro tables.

## [1.0.2] - 2023-03-24
### Fixed
 - Fix 'stats-collect report' crashing on 'inf' acpower values.
 - Fix 'stats-collect report' crashing on on raw acpower statistic files with
   bad headers.
 - Fix several metrics missing 'min/max' summary functions in HTML reports.
### Added
 - Add module C-state support to turbostat collection and reporting.
 - Add fullscreen view to diagrams to 'stats-collect' reports.
 - Add a button to hide report headers in 'stats-collect' reports.
 - Add command used in 'stats-collect start' to 'stats-collect' reports.
### Changed
 - Change 'stats-collect' to collect 'turbostat' and 'sysinfo' statistics by
   default.

## [1.0.1] - 2023-02-13
### Fixed
 - Fix 'stats-collect report' crashing because HTML assets are not properly
   installed.
### Added
 - Add 'pepc topology info' output to 'sysinfo' statistics collection.
 - Add 'pepc topology info' output to 'sysinfo pepc' tab in HTML reports.
### Changed
 - Renamed the 'stats-collect-components' JavaScript package to
    '@intc/stats-collect'.
 - Moved the 'Busy%' turbostat tab from 'Misc' to 'C-states,Hardware' in
   reports generated with 'stats-collect report'.

## [1.0.0] - 2023-01-24
### Changed
 - First release.