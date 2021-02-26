#!/bin/python3

# Proof Wiki source code
# Written by: Jyry Hjelt

import os
import argparse
import pypandoc as pp
import git

# Add some arguments to the program


def proofwiki_main(args):
    if args.action == "init":
        # Initialise the git repository in the specified entries directory
        if args.verbosity == 1:
            print("Initialising a Git repository in the specified directory")
        repo = git.Repo.init(args.entries_dir)

    elif args.action == "build":
        # Check for changes in the entries directory
        if args.verbosity == 1:
            print("Checking for changes")
        repo = git.Repo(args.entries_dir)
        if not repo.is_dirty() and not args.refresh:
            print("No file changes to build. Run wih '--refresh' if you still want to build all the files.")
            exit(2)

        if args.refresh:
            # Build all the entries
            print("Refresh not implemented")
            pass
        else:
            # Regular building of new and modified files
            changed = [entry.a_path for entry in repo.index.diff(None)]
            new_entries = repo.untracked_files
            for entry in changed:
                print(entry)

            # Fill in the wiki with the new and changed files


            # Finally, commit these files into the git repository

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="A mathematical proof wiki creator for personal memorisation")
    parser.add_argument('action', help='build or init', nargs='?', choices=('build', 'init'))

    parser.add_argument('-v', "--verbosity", action='count', default=0, help="Verbose output")
    parser.add_argument('--entries-dir', default="./entries", help="Directory of the Wiki entries")
    parser.add_argument('--refresh', action='store_true', help="Force a build even if no entries have changed")
    iargs = parser.parse_args()
    proofwiki_main(iargs)
