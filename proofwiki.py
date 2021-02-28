#!/bin/python3

# Proof Wiki source code
# Written by: Jyry Hjelt

import os
import argparse
import sys
import logging
import git
from jinja2 import Environment, PackageLoader, select_autoescape
import pypandoc as pp


def proofwiki_main(args):
    '''
        This is the main entry-function of Proof Wiki. Handles instructions conveyed via CLI.
    '''
    if args.verbosity > 1:
        logging.basicConfig(level=logging.DEBUG)
    if args.verbosity > 0:
        logging.basicConfig(level=logging.INFO)

    if args.action == "init":
        # Initialise the git repository in the specified entries directory
        logging.info("Initialising a Git repository in the specified directory")
        repo = git.Repo.init(args.entries_dir)

    elif args.action == "build":
        # Check for changes in the entries directory
        logging.info("Checking for changes")
        repo = git.Repo(args.entries_dir)
        changed = [args.entries_dir + "/" + entry.a_path for entry in repo.index.diff(None) if entry.change_type == 'M']
        deleted_entries = [args.entries_dir + "/" + entry.a_path for entry in repo.index.diff(None) if entry.change_type == 'D']
        new_entries = set([args.entries_dir + "/" + x for x in repo.untracked_files]) | set(changed)

        if len(new_entries) < 1 and len(deleted_entries) < 1 and not args.refresh:
            print("No file changes to build. Run wih '--refresh' if you want to build all the files.")
            sys.exit(2)

        # Check for any directories that are new and also add all the files if --refresh
        all_directories = []
        for root, dirs, files in os.walk(args.entries_dir):
            dirs[:] = [d for d in dirs if d != ".git"]
            all_directories += [root + "/" + x for x in dirs]
            if args.refresh:
                # Add all the files to the new_entries set
                new_entries |= set([f"{root}/{x}" for x in files])

        # Go through the directories and create them in the wiki directory if not there
        for d in all_directories:
            df = args.wiki_dir + d[len(args.entries_dir):]
            if not os.path.isdir(df):
                logging.info("Creating missing directory in " + df)
                os.mkdir(df)

        # Fill in the wiki with the new and changed files
        logging.info("Generating new entries...")
        prettynames = {}
        for entry in new_entries:
            outfile = args.wiki_dir + os.path.splitext(entry)[0][len(args.entries_dir):] + ".html"
            logging.info(f"Converting {entry} -> {outfile}")
            output = pp.convert_file(entry, 'html', outputfile=outfile, extra_args=['--mathjax',
                                                                                    '--template', args.template_file])
            if args.disable_prettylisting:
                prettynames[outfile] = entry
            else:
                prettynames[outfile] = pp.convert_file(entry, 'html', extra_args=["--template", "./assets/title_extractor.pandoc"])

        # Delete any deleted entries
        if len(deleted_entries) > 0:
            logging.info("Deleting removed entries...")
        for entry in deleted_entries:
            dfile = args.wiki_dir + os.path.splitext(entry)[0][len(args.entries_dir):] + ".html"
            logging.info(f"Deleting {dfile}")
            os.remove(dfile)

        # Create the index page for the wiki
        env = Environment(
                loader=PackageLoader('proofwiki', 'assets'),
                autoescape=select_autoescape(['html'])
        )
        indextemplate = env.get_template('index.html.template')
        logging.debug(f"Prettynames: {prettynames}")
        for root, dirs, files in os.walk(args.wiki_dir):
            # Create a index.html page for this directory
            logging.info(f"Generating index for {root}")
            files = [f for f in  os.listdir(root) if f != "index.html"]
            for d in dirs:
                if args.disable_prettylisting:
                    prettynames[f"{root}/{d}"] = d
                else:
                    prettynames[f"{root}/{d}"] = d.replace("_", " ")

            files = [[f, prettynames[f"{root}/{f}" ], os.path.isdir(f"{root}/{f}")] for f in files]
            files.sort(key=lambda x : not x[2]) # Sort directories first!
            logging.debug(files)
            outfile = open(f"{root}/index.html", "w+")
            outfile.write(indextemplate.render(files=files))
            outfile.close()

        # Finally, commit these files into the git repository
        logging.info("Implementing changes to the Git repository...")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="A mathematical proof wiki creator for personal memorisation")
    parser.add_argument('action', help='build or init', nargs='?', choices=('build', 'init'))
    parser.add_argument('-v', "--verbosity", action='count', default=0, help="Verbose output")
    parser.add_argument('-i', '--entries-dir', default="./entries", help="Directory of the entries to be converted")
    parser.add_argument('-o', '--wiki-dir', default="./build", help="Set which directory the built wiki is to be placed")
    parser.add_argument('--refresh', action='store_true', help="Force a build even if no entries have changed")
    parser.add_argument('--disable-prettylisting', action='store_true', help="Make index listing discard naming conventions")
    parser.add_argument('--template-file', default="./assets/entry.html.template", help="File that is going to be the template for the produced HTML for each entry")


   # Run the whole thing
    proofwiki_main(parser.parse_args())
