# Changelog

Changelog practices: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning practices: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [ADD NEW VERSION HERE] - ADD DATE HERE
### Fixed
### Added
### Removed
### Changed

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