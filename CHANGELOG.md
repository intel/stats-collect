# Changelog

Changelog practices: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning practices: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [ADD NEW VERSION HERE] - ADD DATE HERE
### Fixed
 - Adapt to pepc API changes.
### Added
### Removed
### Changed

## [1.0.60] - 2025-09-16
### Fixed
 - Fix crashes related to typing changes in pepc.
### Changed
 - Display all turbostat metrics in CPU statistics. For example, display
   CPU%c6, even though it has core scope, not CPU scope.

## [1.0.59] - 2025-06-06
### Changed
  - Workaround for newest pandas not working in CentOS9.
  - Adjust to turbostat command line options changes.

## [1.0.58] - 2025-05-27
### Changed
 - Adjust to API changes in pepc project. No functional changes.

## [1.0.57] - 2025-05-06
### Fixed
 - Fix failures when running via 'sudo'.

## [1.0.56] - 2025-04-14
### Changed
 - Avoid adding constant metrics to diagram hover text to optimize HTML size.

## [1.0.55] - 2025-04-07
### Fixed
 - Fix a crash introduced in version 1.0.53.

## [1.0.54] - 2025-04-07
### Fixed
 - Fix pepc version requirement: pepc 1.0.53 is requred.

## [1.0.53] - 2025-04-07
### Added
 - Check for 'rsync' before starting to collect statistics.
 - Add support for workloads that provide custom lables. Use the '--pipe' option
   for that. The 'stc-wl-cpu-wake-walk' is an example of such a workload.
 - Add hover text to turbostat scatter plots.

## [1.0.52] - 2025-03-26
### Fixed
 - Fix labels support that was broken in version 1.0.51.

## [1.0.51] - 2025-03-25
### Removed
 - Remove 'stats-collect start --cpus' option.

## [1.0.50] - 2025-03-14
### Fixed
 - Fix python 3.9 compatibility breakage.

## [1.0.49] - 2025-03-11
### Fixed
 - Fix crash with plotly version >= 6.0.0.
 - Fix crash when parsing turbostat files with "(neg)" values.
### Added
 - Add placeholders support in 'stats-collect start'. For example, one can run
   the "stats-collect start my_workload --reportid {REPORTID}", and
   "{REPORTID}" will be substituted with the report ID of the result.

## [1.0.48] - 2025-03-05
### Added
 - Add 'stats-collect report --cpus' option to specify CPU numbers to include
   in the report.
### Changed
 - Rename 'stats-collect start --cpunum' option to '--cpus' and allow for
   providing multiple CPU numbers, not just one CPU number.

## [1.0.47] - 2025-02-27
### Fixed
 - Fix crash introduced in release 1.0.46.

## [1.0.46] - 2025-02-27
### Fixed
 - Fix alignment in SPECjbb2015 diagrams.
### Added
 - Add 'stats-collect start --cmd-local' option.

## [1.0.45] - 2025-01-27
### Fixed
  - Fix a regression since 1.0.44: pbe reports generation crashes.

## [1.0.44] - 2025-01-25
### Added
 - Add interrupt statistics visualization.
### Changed
 - Do not add histograms to HTML reports to save disk space.

## [1.0.43] - 2025-01-23
### Fixed
 - Fix python < 3.10 breakage.
### Changed
 - Improve '/proc/interrupts' collector to save disk space by making the
   collected data more compact (remove extra white-spaces).

## [1.0.42] - 2025-01-23
### Fixed
 - Fix failure to generate 'pepc' tab in 'SysInfo'. Regression since v 1.0.39.

## [1.0.41] - 2025-01-21
### Fixed
 - Fix failure to generate 'pepc' tab in 'SysInfo'. Regression since v 1.0.39.

## [1.0.40] - 2025-01-17
### Added
 - Support collecting interrupts statistics. No visualisation support yet, just
   collection.

## [1.0.39] - 2025-01-15
### Fixed
 - Do not delete logs on error.
### Added
 - Collect 'pepc pmqos' output.

## [1.0.38] - 2025-01-08
### Changed
 - Improve SEPCjbb2015 results cropping.

## [1.0.37] - 2025-01-05
### Fixed
 - Fix failure to visualize IPMI statistics  (regression since v1.0.35).

## [1.0.36] - 2025-01-05
### Fixed
 - Fix incorrect pepc requriement.

## [1.0.35] - 2025-01-05
### Fixed
 - Fix mis-placing of ACPI C-states like C1_ACPI in HTML reports.
### Added
 - Add workload data direcrtory reference from the intro table.
 - Add basic SPECjbb2015 workload support.
 - Add 'stats-collect report --copy-raw' option support.
### Changed
 - Speed up Turbostat data parsing.

## [1.0.34] - 2024-11-29
### Fixed
 - Fix turbostat "PkgWatt%TDP" statistics for results collected with
   multisocket systems.

## [1.0.33] - 2024-10-21
### Added
 - Add turbostat 'SYS%LPI' metric.

## [1.0.32] - 2024-10-15
### Changed
 - Minor cleanups, no real functional changes.

## [1.0.31] - 2024-10-15
 - Fix a regression introduced in v1.0.30 - the turbostat HTML tab for the
   measured CPU was removed - bring it back.

## [1.0.30] - 2024-09-16
### Fixed
 - Fix a regression introduced in v1.0.29 which meant HTML reports could not be
   generated for results which were collected without the '--cpunum' option.
### Changed
 - By default, disable 'IRQ' turbostat data. This can be re-enabled by
   disabling the 'hide-irq' turbostat property in a stats-collect configuration
   file.

## [1.0.29] - 2024-08-16
### Fixed
 - Fix a regression introduced in v1.0.28 which meant that package C-state
   residency tabs with shorter names (e.g. PC1) are excluded from the turbostat
   tab in HTML reports.
 - Fix an issue where metric descriptions in "Turbostat Totals" tabs contained
   duplicate sentences.

## [1.0.28] - 2024-08-07
### Fixed
 - Fix support for package C-state residencies with longer names in HTML report
   turbostat hardware C-state tabs. For example, the package C-state residency
   for 'PC10' will now be included in the hardware C-state tabs.
 - Fix HTML report generation crashing when turbostat files contain one or more
   "(neg)" values.

## [1.0.27] - 2024-07-23
### Fixed
 - Fix an issue which caused HTML report generation to crash when hover-text
   contained values with no unit.
### Added
 - Add relative package power data to the turbostat totals tab in HTML reports.
   The new tab contains package power data relative to TDP.

## [1.0.26] - 2024-07-12
### Fixed
 - Fix some turbostat package C-state residency tabs being missed in HTML
   reports.

## [1.0.25] - 2024-06-05
### Fixed
 - Fix an issue where 'stats-collect report' would not generate diffs for files
   with minor differences.
 - Fix a 'FutureWarning' from a dependency being printed during HTML report
   generation.
 - Fix 'stats-collect report' crashing when 'ipmi' statistics contain 'nan'
   values.
### Added
 - Add support for new turbostat uncore frequency columns in HTML reports.
 - Add 'Diff' tabs with messages clarifying when diff generation has been
   skipped because files are identical in HTML report Sysinfo tabs.
### Changed
 - Change the order of hardware C-state residency turbostat tabs in the HTML
   report tab tree so that module C-state residency tabs appear above package
   C-state residency tabs.
 - Change redundant log message about deleted directories (when no statistics
   are collected) so that it only appears as a debug message.

## [1.0.24] - 2024-04-25
### Changed
 - Fix debianiaztion/rpm-ization to include new split man pages.

## [1.0.23] - 2024-04-25
### Fixed
 - Fix 'stats-collect report' populating totals turbostat tabs with measured
   CPU data since v1.0.4.

## [1.0.22] - 2024-03-08
### Removed
 - Remove 'scaling_cur_freq' from 'SysInfo' 'cpufreq' files to reduce filesize
   and diff generation times.
 - Remove 'usage', 'time', 'above' and 'below' from 'SysInfo' 'cpuidle' files
   to reduce filesize and diff generation times.
### Changed
 - Fix 'pandas' dependency version to '>2.1.0' to avoid 'FutureWarning'
   appearing during HTML report generation.

## [1.0.21] - 2024-02-09
### Changed
 - Replaced time-zone sensitive timestamps in 'ipmi' raw statistic files with
   epoch timestamps to allow labels to be applied to 'ipmi' data.

## [1.0.20] - 2023-12-22
### Added
 - Add summarised turbostat data for CPU 0, as a part of SysInfo statistics (in
   addition to existing turbostat data collection).
### Removed
 - Removed time-stamps from 'dmesg' SysInfo files.
### Changed
 - Show summarised turbostat data for CPU 0 in the turbostat SysInfo tab in
   HTML reports instead of longer data which was collected without specifying a
   CPU.

## [1.0.19] - 2023-11-24
### Fixed
 - Fix the order of turbostat hardware C-state tabs in HTML reports.
### Added
 - Add a link to the report generation log in the report info panel of HTML
   reports.

## [1.0.18] - 2023-10-04
### Fixed
 - Make data points in HTML report plots more human-readable by scaling values
   with SI-unit prefixes. For example, a value of '1200 MHz' will now be shown
   as '1.20 GHz'.

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
