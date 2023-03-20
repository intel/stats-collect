# Changelog

Changelog practices: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning practices: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [ADD NEW VERSION HERE] - ADD DATE HERE
### Fixed
 - Fix 'stats-collect report' crashing on 'inf' acpower values.
 - Fix 'stats-collect report' crashing on on raw acpower statistic files with
   bad headers.
### Added
 - Add module C-state support to turbostat collection and reporting.
 - Add fullscreen view to diagrams in wult HTML reports.
 - Add a button to hide report headers in wult HTML reports.
 - Add command used in 'stats-collect start' to 'stats-collect' reports.
### Removed
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
