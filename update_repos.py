import argparse
import configparser
import datetime
import logging.config
import os
import subprocess

APPNAME = 'update_repos'

def onerror(os_error):
    raise os_error

def dir_with_git(top, gitname='.git', onerror=onerror):
    for root, dirs, files in os.walk(top, onerror=onerror):
        if gitname in dirs:
            yield root

def current_branch(head_path, prefix='ref: '):
    with open(head_path) as head_file:
        for line in head_file:
            if line.startswith(prefix):
                yield line[len(prefix):].strip()

def exclude_paths(lines):
    for line in lines:
        if line and not line.startswith('#'):
            yield line

def print_result(result):
    for output in [result.stdout, result.stderr]:
        for line in output.splitlines():
            print(line)

def get_branch_name(root):
    gitdir = os.path.join(root, '.git')
    head_path = os.path.join(gitdir, 'HEAD')

    refs = list(current_branch(head_path))
    assert len(refs) == 1, gitdir
    ref = refs[0]

    branch = ref.split('/')[-1]
    return branch

def git_fetch_and_hard_reset_origin_branch(root):
    options = dict(
        capture_output = True,
        check = True,
        text = True,
    )
    options.update(cwd=root)
    command = ['git', 'fetch']
    result = subprocess.run(command, **options)
    if result.stdout or result.stderr:
        # guessing that if there was standard output, then we proceed
        yield result
        branch = get_branch_name(root)
        command = ['git', 'reset', '--hard', f'origin/{branch}']
        result = subprocess.run(command, **options)
        if result.stdout or result.stderr:
            yield result

def build_command(args, cp):
    """
    Build a database file of .git repo root paths.
    """
    app_section = cp[APPNAME]

    output = app_section['database']

    exclude = app_section.get('exclude', '')
    exclude = set(exclude_paths(exclude.splitlines()))

    if args.top:
        top = args.top
    else:
        top = app_section['top']

    with open(output, 'w') as database:
        for root in dir_with_git(top):
            # root is a path that contains a .git
            if root in exclude:
                continue
            print(root, file=database)

def update_command(args, cp):
    """
    Fetch and update git repos.
    """
    app_section = cp[APPNAME]
    database_path = app_section['database']

    start_time = datetime.datetime.now()

    logger = logging.getLogger(APPNAME)
    with open(database_path) as database:
        roots = list(map(str.strip, database))
        nroots = len(roots)
        for n, root in enumerate(roots, start=1):
            logger.debug('(%03d/%03d) update: %s', n, nroots, root)
            for result in git_fetch_and_hard_reset_origin_branch(root):
                for attr in ['stdout', 'stderr']:
                    output = getattr(result, attr)
                    for line in output.splitlines():
                        logger.debug('%s: %s', attr, line)

    end_time = datetime.datetime.now()
    elapsed = end_time - start_time
    logger.debug('start_time=%s', start_time)
    logger.debug('elapsed=%s', elapsed)
    logger.debug('end_time=%s', end_time)

def add_common_options(parser):
    parser.add_argument('config', nargs='+')
    parser.add_argument(
        '--top',
        help = 'Ignore `top` from config and start at this path.',
    )

def argument_parser():
    parser = argparse.ArgumentParser(
        description = main.__doc__,
        prog = APPNAME,
    )
    subparsers = parser.add_subparsers()

    sp = subparsers.add_parser('build')
    add_common_options(sp)
    sp.set_defaults(func=build_command)

    sp = subparsers.add_parser('update')
    add_common_options(sp)
    sp.set_defaults(func=update_command)
    return parser

def main(argv=None):
    """
    Run commands from configuration.
    """
    parser = argument_parser()
    args = parser.parse_args(argv)

    func = args.func
    del args.func

    cp = configparser.ConfigParser()
    cp.read(args.config)

    if set(['loggers', 'handlers', 'formatters']).issubset(cp):
        logging.config.fileConfig(cp)

    return func(args, cp)

if __name__ == '__main__':
    main()
