<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

Copyright (C) 2019-2024 Intel, Inc.
SPDX-License-Identifier: BSD-3-Clause

Author: Adam Hawley <adam.james.hawley@intel.com>
-->
# @intc/stats-collect

## Packaging
This Javascript package is configured to use the 'npm' package manager.
For security reasons, this project uses an Intel package registry `pixi.intel.com`.

> Note: this JavaScript package in NOT distributed to any public 'npm' registry. This package is private to
the 'stats-collect' project and is not intended to be installed by any other person or project.
The only intended usage for the source code in this project is that it is bundled and distributed
by the 'stats-collect' Python package which can be found in the same repository.

## Bundling
Files within the 'src' directory are bundled with [webpack](https://webpack.js.org/) into the 'dist'
directory. This means that rather than having to include all of the separate JavaScript modules
written in 'src' in the HTML report, we can include one 'main.js'.

Webpack also generates a 'main.js.LICENSE.txt' file which is an aggregation of all of the licenses
from the different packages that have been bundled together. For example, this project uses the
['lit' npm module](https://www.npmjs.com/package/lit). At the time of writing, 'lit' uses the 'BSD
3-Clause' license and this is reflected in the 'main.js.LICENSE.txt'.

## How-To
### Contribute
1. Install the `npm` tool.
2. Install local dependencies with the `npm install` command while in the `js` directory.
3. Make your changes to the relevant file.
4. Compile the JavaScript into `dist/` with `npm run build`.
5. (Optional) if you are using the package to generate a 'stats-collect' HTML report, re-generate your 'stats-collect' HTML report and it should use your modified JavaScript.

### Install Additional Dependencies / Bump Dependency Versions
1. If you have not configured npm to use the Intel package registry `pixi.intel.com`, do so with the `npm set registry https://pixi.intel.com/` command.
2. Use the `npm install <package_name>` command to install the latest version of a package. If you would like to specify a version use the `npm install <package_name>@<version>` command.

### Create a New Web Component
1. Create a new JavaScript file in `src/` containing your web component. This project currently
   uses the 'lit' library for creating web components and it is recommended to view their
   documentation [here](https://lit.dev/) before defining your first web component.
2. Webpack looks at the `src/index.js` as the entry file of the JavaScript files. This means that
   it first looks at this file to see which module imports need to be resolved and then added to the
   bundle. Therefore if you have created a new web component you will need to import the
   newly-defined component in `src/index.js` so that webpack knows to include it in the bundle.
3. Use the `npm run build` command to re-bundle the JavaScript modules and include your new
   component in the `dist/` directory.
