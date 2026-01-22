#!/usr/bin/env python3.9

""" The CLI entry for TOBi"""

import argparse
import os
import sys

from makei import __version__
from makei import init_project
from makei.build import BuildEnv
from makei.cvtsrcpf import CvtSrcPf
from makei.utils import Colors, colored, decompose_filename
from pathlib import Path


def cli():
    """
    makei program entry
    """
    parser = argparse.ArgumentParser(prog='makei')
    subparsers = parser.add_subparsers(
        title='These are common makei commands',
        metavar='command')

    add_init_parser(subparsers)
    add_info_parser(subparsers)
    add_compile_parser(subparsers)
    add_build_parser(subparsers)
    add_cvtsrcpf_parser(subparsers)
    parser.add_argument(
        '-l', '--log',
        help="log build files and output the make command without executing it; "
             "trace data is stored in ./.makei-trace.",
        action='store_true'
    )
    parser.add_argument(
        '-v', '--version',
        help="print version information and exit",
        action='store_true'
    )

    args = parser.parse_args()
    if args.version:
        print(f"TOBi version {__version__}")
    elif hasattr(args, 'handle'):
        args.handle(args)
    else:
        parser.print_help()


def add_build_parser(subparsers: argparse.ArgumentParser):
    """Add subparsers for build commands"""
    build_parser = subparsers.add_parser(
        'build',
        aliases=['b'],
        help='build the whole project',
    )
    build_target_group = build_parser.add_mutually_exclusive_group()
    build_target_group.add_argument(
        '-t',
        '--target',
        help='target to be built',
        metavar='<target>'
    )
    build_target_group.add_argument(
        '-d',
        '--subdir',
        help='subdirectory to be built',
        metavar='<subdir>'
    )
    build_parser.add_argument(
        '-o',
        '--make-options',
        help='options to pass to make',
        metavar='<options>',
    )
    build_parser.add_argument(
        '--tobi-path',
        help='path to the TOBi directory',
        metavar='<path>',
    )
    build_parser.add_argument(
        '-e',
        '--env',
        help='override environment variables',
        metavar='<var>=<value>',
        action='append'
    )
    build_parser.set_defaults(handle=handle_build)


def add_compile_parser(subparsers: argparse.ArgumentParser):
    """Add subparsers for compile commands"""
    compile_parser = subparsers.add_parser(
        'compile',
        aliases=['c'],
        help='compile a single file')
    compile_target_group = compile_parser.add_mutually_exclusive_group(
        required=True)
    compile_target_group.add_argument(
        '-f',
        '--file',
        help='file to compile',
        metavar='<filename>')
    compile_target_group.add_argument(
        '--files',
        help='files to compile, separated by colon (:)',
        metavar='<filepaths>')
    compile_parser.add_argument(
        '-o',
        '--make-options',
        help='options to pass to make',
        metavar='<options>',
    )
    compile_parser.add_argument(
        '-e',
        '--env',
        help='override environment variables',
        metavar='<var>=<value>',
        action='append'
    )
    compile_parser.add_argument(
        '--tobi-path',
        help='path to the TOBi directory',
        metavar='<path>',
    )
    compile_parser.set_defaults(handle=handle_compile)


def add_init_parser(subparsers: argparse.ArgumentParser):
    """Add subparsers for init commands"""
    init_parser = subparsers.add_parser(
        'init',
        help='set up a new or existing project')

    init_parser.add_argument('-f', '--force',
                             help='force overwrite any existing files',
                             action='store_true')
    init_parser.add_argument('-o', '--objlib',
                             help='update object library')
    init_parser.add_argument('-c', '--ccsid',
                             help='update target ccsid')
    init_parser.set_defaults(handle=handle_init)


def add_cvtsrcpf_parser(subparsers: argparse.ArgumentParser):
    cvtsrcpf_parser = subparsers.add_parser(
        'cvtsrcpf',
        help='convert source physical file members to UTF8 IFS files',
        description='Converts all members in a source physical file to properly-named \
                        (Better Object Builder-compatible), UTF8-encoded, LF-terminated source files \
                        in the current directory in the IFS. An .ibmi.json will also be created at the same directory.'
    )

    cvtsrcpf_parser.add_argument(
        "file",
        help='the name of the source file',
        metavar='<file>',
    )

    cvtsrcpf_parser.add_argument(
        "library",
        help='the name of the library',
        metavar='<library>',
    )

    cvtsrcpf_parser.add_argument(
        "-c",
        "--ccsid",
        help='The target EBCDIC CCSID that the source in this directory should be compiled with. If not specified, '
             'then the CCSID of the SRC-PF being converted will be used. '
             'If that CCSID is 65535 or an invalid CCSID is encountered than the CCSID of the JOB running '
             'the build will be used.',
        metavar='<ccsid>',
        type=str
    )

    cvtsrcpf_parser.add_argument(
        "-l",
        "--tolower",
        help='The generated source file name will be in lowercase.',
        action='store_true'
    )

    cvtsrcpf_parser.add_argument(
        "-t",
        "--text",
        help='The generated source file will include the member text as a comment.',
        action='store_true'
    )

    cvtsrcpf_parser.set_defaults(tolower=False)
    cvtsrcpf_parser.set_defaults(handle=handle_cvtsrcpf)


def add_info_parser(subparsers: argparse.ArgumentParser):
    """Add subparsers for info commands"""
    info_parser = subparsers.add_parser(
        'info',
        help='get information about the current project')

    info_parser.set_defaults(handle=handle_info)


def handle_init(args):
    """
    Handling the init command
    """
    if args.log:
        print(colored("Warning: --log has no effect on 'init' command.", Colors.WARNING))
    init_project.init_project(force=args.force, objlib=args.objlib, tgtCcsid=args.ccsid)


def handle_info(args):
    """
    Handling the info command
    """
    if args.log:
        print(colored("Warning: --log has no effect on 'info' command.", Colors.WARNING))
    print("Not implemented!")


def read_and_filter_rules_mk(source_names):
    """
    Read the Rules.mk file and return targets that match allowed extensions.
    """
    build_targets = []
    source_path = Path(source_names[0])
    name, _, ext, _ = decompose_filename(source_names[0])
    rules_mk_path = Path(source_names[0]).parent / "Rules.mk"
    if not rules_mk_path.exists():
        raise FileNotFoundError(f"No Rules.mk found at {rules_mk_path}")
    with rules_mk_path.open("r") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue  # skip blank lines, comments, or malformed lines
            target, deps = map(str.strip, line.split(":", 1))
            dep_list = [dep.upper() for dep in deps.split()]
            if source_path.name.upper() in dep_list:
                build_targets.append(target)
    if not build_targets:
        raise ValueError(f"No target found in Rules.mk for source file '{source_path.name}'")
    return build_targets


def handle_compile(args):
    """
    Processing the compile command
    """
    filenames = []
    set_environment_vars(args)
    if args.file:
        filenames = [args.file]
    elif args.files:
        # Ensures all paths are relative to the project root
        filenames = map(lambda f: (str(Path(f).resolve().relative_to(Path.cwd()))), args.files.split(':'))
    else:
        filenames = []
    targets = []
    source_names = []
    for name in filenames:
        if os.path.isdir(name):
            targets.append(make_dir_target(name))
        else:
            source_names.append(name)
            targets_from_rule = read_and_filter_rules_mk(source_names)
            targets.extend([t.upper() for t in targets_from_rule])
    print(colored("targets: " + ', '.join(targets), Colors.OKBLUE))
    build_env = BuildEnv(targets, args.make_options, get_override_vars(args), trace=args.log)
    if args.log:
        build_env.dump_resolved_makefile()
    else:
        if build_env.make():
            sys.exit(0)
        else:
            sys.exit(1)


def handle_build(args):
    """
    Processing the build command
    """
    set_environment_vars(args)
    if args.target:
        target = args.target
    elif args.subdir:
        name = os.path.basename(args.subdir)
        filenames = [args.subdir] if os.path.isdir(name) else []
        if filenames:
            for i in filenames:
                target = make_dir_target(i)

    else:
        target = "all"
    build_env = BuildEnv([target], args.make_options, get_override_vars(args), trace=args.log)
    if args.log:
        build_env.dump_resolved_makefile()
    else:
        if build_env.make():
            sys.exit(0)
        else:
            sys.exit(1)


def make_dir_target(filename):
    return f"dir_{filename.replace('/', '_')}"


def handle_cvtsrcpf(args):
    """
    Processing the cvtsrcpf command
    """
    if args.log:
        print(colored("Warning: --trace has no effect on 'cvtsrcpf' command.", Colors.WARNING))
    CvtSrcPf(args.file, args.library, args.tolower, args.ccsid, args.text).run()


def get_override_vars(args):
    """ Get the override variables from the arguments"""
    if args.tobi_path:
        return {"tobi_path": args.tobi_path}
    return {}


def set_environment_vars(args):
    """ Set the environment variables defined in the arguments"""
    if "env" in args and args.env:
        for env in args.env:
            kv_pair = env.split("=")
            if len(kv_pair) != 2:
                print(colored(f"invalid format: {env}", Colors.FAIL))
                sys.exit(1)
            key, value = kv_pair[0], kv_pair[1]
            os.environ[key] = value
            print(colored(f"Set variable <{key}> to '{value}'", Colors.OKBLUE))


if __name__ == '__main__':
    cli()
