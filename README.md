# Proof Wiki

This is a simple Wiki written with Python that converts categorized Markdown files into 
static HTML files using Pandoc.

# Purpose

Proof Wiki is supposed to provide a simple program that will convert
notes via Pandoc to a static website format. The purpose is to limit the amount
of pointless fluff as well as support for scaling. Scaling is accomodated by having
new pages added to the generated wiki incrementally and not re-building old entries that
are not necssary. Hence adding new entries will not take forever to build.

# Usage

## Requirements

- Python 3
    + PyPandoc
    + GitPython
- Pandoc
- Git

## Sample usage

### Initialising
In order to start using a directory as a source for markdown files and how the
page is to be structured, we run 
```shell
python3 proofwiki.py init DIR_NAME
```
This initialises a git repository in that directory

### Adding new entries

To add new entries (new webpages), all one needs to do is add a markdown file (or any supported by Pandoc)
under the initialised directory. Then running the following command will update the webpage:
``` shell
python3 proofwiki.py build --entries-dir DIR_NAME
```
