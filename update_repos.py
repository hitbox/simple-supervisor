import argparse
import configparser
import datetime
import logging.config
import os
import subprocess

APPNAME = 'simple_supervisor'

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

def git_fetch_and_hard_reset_origin_branch(top, exclude):
    options = dict(
        capture_output = True,
        check = True,
        text = True,
    )
    # XXX: WIP
    # - the git commands are changing the state of the filesystem
    # - so we capture in a list
    # - would rather generate
    roots = list(dir_with_git(top))
    for root in roots:
        if root in exclude:
            print(f'excluding: {root}')
            continue
        else:
            print(root)

        # XXX: WIP
        if not os.path.exists(root):
            continue

        options.update(cwd=root)
        command = ['git', 'fetch']
        result = subprocess.run(command, **options)
        if result.stdout or result.stderr:
            # guessing that if there was standard output, then we proceed
            print_result(result)
            branch = get_branch_name(root)
            command = ['git', 'reset', '--hard', f'origin/{branch}']
            result = subprocess.run(command, **options)
            if result.stdout:
                print_result(result)

def main(argv=None):
    """
    Run commands from configuration.
    """
    parser = argparse.ArgumentParser(
        description = main.__doc__,
        prog = APPNAME,
    )
    parser.add_argument('config', nargs='+')
    parser.add_argument(
        '--top',
        help = 'Ignore `top` from config and start at this path.',
    )
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    if set(['loggers', 'handlers', 'formatters']).issubset(cp):
        logging.config.fileConfig(cp)

    app_section = cp[APPNAME]

    exclude = app_section.get('exclude', '')
    exclude = set(exclude_paths(exclude.splitlines()))

    if args.top:
        top = args.top
    else:
        top = app_section['top']

    start_time = datetime.datetime.now()
    git_fetch_and_hard_reset_origin_branch(top, exclude)
    end_time = datetime.datetime.now()
    elapsed = end_time - start_time
    print(f'{start_time=}')
    print(f'{elapsed=}')
    print(f'{end_time=}')

if __name__ == '__main__':
    main()
