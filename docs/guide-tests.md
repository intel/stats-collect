<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
-->

# Stats-collect Tests Guide

- Author: Artem Bityutskiy <dedekind1@gmail.com>

## Table of Contents

- [Overview](#overview)
- [The pepc Read Token](#the-pepc-read-token)
  - [Background](#background)
  - [Renewing the Token](#renewing-the-token)

## Overview

This guide covers topics related to the stats-collect test suite. More content will be added here
over time.

## The pepc Read Token

### Background

CI here refers to GitHub Actions — the automated workflows in `.github/workflows/`. The main test
workflow is `.github/workflows/pytest.yml`, triggered on every push by two orchestrating workflows:

- `.github/workflows/ci-public.yml`: runs on the public GitHub repository (`intel/stats-collect`).
- `.github/workflows/ci-innersource.yml`: runs on the innersource (Intel-internal) repository
  (`intel-innersource/applications.validation.server-powerlab.stats-collect`).

`pepc` is a required dependency but is not on PyPI, so CI checks it out from source. On the public
repository, `pepc` is fetched from `intel/pepc`, which is public and requires no token. On the
innersource repository, `pepc` must be fetched from its innersource location, which is private.
GitHub Actions' automatic `GITHUB_TOKEN` is scoped to the current repository only and cannot read
other repositories, so a fine-grained Personal Access Token (PAT) named `PEPC_READ_TOKEN` is
stored as a repository secret in the innersource `stats-collect` repository and passed to
`actions/checkout` for that step.

PATs expire. This one was created with a one-year lifetime and will need renewing roughly annually.

### Renewing the Token

1. **Create a new fine-grained PAT** on GitHub.
   - Go to your GitHub account → Settings → Developer settings → Personal access tokens →
     Fine-grained tokens → Generate new token.
   - Set an expiration of one year (or whatever the maximum allowed is).
   - Under "Repository access", select "Only select repositories" and pick
     `intel-innersource/applications.validation.server-powerlab.pepc`.
   - Under "Repository permissions", grant **Contents: Read-only**.
   - Generate the token and copy it immediately (it is shown only once).

2. **Update the repository secret** in the innersource `stats-collect` repository.
   - Go to the innersource `stats-collect` repository on GitHub.
   - Navigate to Settings → Secrets and variables → Actions.
   - Find the secret named `PEPC_READ_TOKEN` and click "Update".
   - Paste the new token value and save.

That is all. The workflows pick up the new secret automatically on the next run. No code changes
are needed.
