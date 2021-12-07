from subprocess import check_output
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser(description="Admin utilities for JupyterHub")
    subparsers = parser.add_subparsers()

    set_user = subparsers.add_parser('setuser', description='Create a user or change a password')
    set_user.set_defaults(action='setuser')
    set_user.add_argument('username')
    set_user.add_argument('password')

    allow_read = subparsers.add_parser('allowread', description='Give a user read-only permission to another user\'s home directory')
    allow_read.set_defaults(action='allowread')
    allow_read.add_argument('owner_username')
    allow_read.add_argument('target_username')

    allow_write = subparsers.add_parser('allowwrite', description='Give a user read & write permission to another user\'s home directory')
    allow_write.set_defaults(action='allowwrite')
    allow_write.add_argument('owner_username')
    allow_write.add_argument('target_username')

    disallow = subparsers.add_parser('disallow', description='Remove a user\'s permissions for another user\'s home directory')
    disallow.set_defaults(action='disallow')
    disallow.add_argument('retired_username')
    disallow.add_argument('target_username')

    args = parser.parse_args()

    if args.action == 'setuser':
        try:
            check_output(['adduser', args.username,  '--disabled-password', '--gecos', '', '--shell', '/bin/bash'])
            print('Created user ', args.username)
        except Exception as e:
            print('ERROR: Failed to create user:', str(e))
        try:
            hashed = check_output(['/usr/bin/openssl', 'passwd', args.password]).decode()[:-1]
            check_output(['/usr/sbin/usermod', '-p', hashed, args.username])
            print('Set password for user ', args.username)
        except Exception as e:
            print('ERROR: Failed to set password:', str(e))
    elif args.action.startswith('allow'):
        perms = 'r-x'
        if args.action.endswith('write'):
            perms = 'rwx'
        source_dir = f'/home/{args.target_username}'
        target_dir = f'/home/{args.owner_username}/{args.target_username}'
        try:
            check_output(['/usr/bin/ln', '-s', source_dir, target_dir])
            check_output(['/usr/bin/setfacl', '-LR', '-m', f'u:{args.owner_username}:{perms}', source_dir])
            print(f'Created permissions ({perms}) for {source_dir}')
        except Exception as e:
            print(f'ERROR: Failed to grant permissions ({perms}) for {target_dir}', str(e))
    elif args.action == 'disallow':
        user_dir = f'/home/{args.target_username}'
        linked_dir = f'/home/{args.retired_username}/{args.target_username}'
        try:
            check_output(['/usr/bin/setfacl', '-LR', '-x', f'u:{args.retired_username}', user_dir])
            check_output(['/usr/bin/unlink', linked_dir])
            print(f'Removed permissions for {user_dir}')
        except Exception as e:
            print(f'ERROR: Failed to remove permissions for {user_dir}', str(e))
