#!/bin/sh -euf
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

PROG="make_a_release.sh"
BASEDIR="$(readlink -ev -- ${0%/*}/..)"

# Regular expression matching stats-collect version.
VERSION_REGEX='\([0-9]\+\)\.\([0-9]\+\)\.\([0-9]\+\)'

# File paths containing the version number that we'll have to adjust.
STCOLL_FILE="$BASEDIR/statscollecttools/_StatsCollect.py"
STCOLL_VER_FILE="$BASEDIR/statscollecttools/ToolInfo.py"
SPEC_FILE="$BASEDIR/rpm/stats-collect.spec"

# The CHANGELOG.md file path.
CHANGELOG_FILE="$BASEDIR/CHANGELOG.md"

# Documentation file paths.
STCOLL_MAN_FILE="$BASEDIR/docs/man1/stats-collect.1"
STCOLL_RST_FILE="$BASEDIR/docs/stats-collect-man.rst"

# Path to 'pepc' project sources.
PEPC_SRC_PATH="$BASEDIR/../pepc"
# Path to the script converting CHANGELOG.md into debian changelog.
CHANGELOG_MD_TO_DEBIAN="$PEPC_SRC_PATH/misc/changelog_md_to_debian"
# Path to the script that prepares CHANGELOG.md for the release.
PREPARE_CHENGELOG_MD="$PEPC_SRC_PATH/misc/prepare_changelog_md"

fatal() {
        printf "$PROG: error: %s\n" "$1" >&2
        exit 1
}

usage() {
        cat <<EOF
Usage: ${0##*/} <new_ver>

<new_ver> - new tool version to make in X.Y.Z format. The X.Y.(Z+1) version
            will be used by default.
EOF
        exit 0
}

ask_question() {
	local question=$1

	while true; do
		printf "%s\n" "$question (yes/no)?"
		IFS= read answer
		if [ "$answer" == "yes" ]; then
			printf "%s\n" "Very good!"
			return
		elif [ "$answer" == "no" ]; then
			printf "%s\n" "Please, do that!"
			exit 1
		else
			printf "%s\n" "Please, answer \"yes\" or \"no\""
		fi
	done
}

if [ $# -eq 1 ]; then
    new_ver="$1"; shift
    # Validate the new version.
    printf "%s" "$new_ver" | grep -q -x "$VERSION_REGEX" ||
           fatal "please, provide new version in X.Y.Z format"
elif [ $# -eq 0 ]; then
    # The new version was not provided, increment the current version number.
    sed_regex="^VERSION = \"$VERSION_REGEX\"$"
    ver_start="$(sed -n -e "s/$sed_regex/\1.\2./p" "$STCOLL_VER_FILE")"
    ver_end="$(sed -n -e "s/$sed_regex/\3/p" "$STCOLL_VER_FILE")"
    ver_end="$(($ver_end+1))"
    new_ver="$ver_start$ver_end"
else
    usage
fi

echo "New stats-collect version: $new_ver"

# Validate the new version.
printf "%s" "$new_ver" | grep -q -x "$VERSION_REGEX" ||
         fatal "please, provide new version in X.Y.Z format"

pepc_ver="$(sed -n -e "s/.*pepc\s*>=\s*\($VERSION_REGEX\).*/\1/p" "$BASEDIR/setup.py")"

echo "Dependency: pepc version >= $pepc_ver"

# Validate 'pepc' version.
printf "%s" "$pepc_ver" | grep -q -x "$VERSION_REGEX" ||
         fatal "bad 'pepc' version '$pepc_ver' in '$BASEDIR/setup.py'"

# Make sure that the current branch is 'main' or 'release'.
current_branch="$(git -C "$BASEDIR" branch | sed -n -e '/^*/ s/^* //p')"
if [ "$current_branch" != "main" -a "$current_branch" != "release" ]; then
	fatal "current branch is '$current_branch' but must be 'main' or 'release'"
fi

# Remind the maintainer about various important things.
ask_question "Did you run tests"
ask_question "Did you update 'CHANGELOG.md'"

# Update 'pepc' version.
sed -i -e "s/\(pepc\s*>=\s*\)$VERSION_REGEX/\1$pepc_ver/g" "$BASEDIR/rpm/wult.spec"
sed -i -e "s/^\(\s\+pepc\s*(>=\s*\)$VERSION_REGEX)/\1$pepc_ver)/g" "$BASEDIR/debian/control"

# Update CHANGELOG.md.
"$PREPARE_CHENGELOG_MD" "$new_ver" "$CHANGELOG_FILE"
# Update debian changelog.
"$CHANGELOG_MD_TO_DEBIAN" -o "$BASEDIR/debian/changelog" -p "stats-collect" -n "Artem Bityutskiy" \
                          -e "artem.bityutskiy@intel.com" "$CHANGELOG_FILE"

# Change the tool version.
sed -i -e "s/^VERSION = \"$VERSION_REGEX\"$/VERSION = \"$new_ver\"/" "$STCOLL_VER_FILE"
# Change RPM package version.
sed -i -e "s/^Version:\(\s\+\)$VERSION_REGEX$/Version:\1$new_ver/" "$SPEC_FILE"

# Update the man page.
argparse-manpage --pyfile "$STCOLL_FILE" --function build_arguments_parser \
                 --project-name 'stats-collect' --author 'Artem Bityutskiy' \
                 --author-email 'dedekind1@gmail.com' --output "$STCOLL_MAN_FILE" \
                 --url 'https://github.com/intel/stats-collect'
pandoc --toc -t man -s "$STCOLL_MAN_FILE" -t rst -o "$STCOLL_RST_FILE"

# Commit the changes.
git -C "$BASEDIR" commit -a -s -m "Release version $new_ver"

outdir="."
tag_name="v$new_ver"
release_name="Version $new_ver"

# Create new signed tag.
printf "%s\n" "Signing tag $tag_name"
git -C "$BASEDIR" tag -m "$release_name" -s "$tag_name"

if [ "$current_branch" = "main" ]; then
    branchnames="main and release brances"
else
    branchnames="release branch"
fi

cat <<EOF
To finish the release:
  1. push the $tag_name tag out
  2. push $branchnames branches out

The commands would be:
EOF

for remote in "origin" "upstream" "public"; do
    echo "git push $remote $tag_name"
    if [ "$current_branch" = "main" ]; then
        echo "git push $remote main:main"
        echo "git push $remote main:release"
    else
        echo "git push $remote release:release"
    fi
done

if [ "$current_branch" != "main" ]; then
    echo
    echo "Then merge the release branch back to main, and run the following commands:"

    for remote in "origin" "upstream" "public"; do
        echo "git push $remote main:main"
    done
fi
