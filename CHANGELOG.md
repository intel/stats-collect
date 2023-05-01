# Changelog

Changelog practices: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning practices: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [ADD NEW VERSION HERE] - ADD DATE HERE
### Fixed
 - Fix statistics collectors.
 - Fix 'stats-collect report' generating broken diffs when given results with
   duplicate report IDs.
### Added
### Removed
### Changed

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
