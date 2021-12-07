# Personal JupyterHub

A Docker image providing a [JupyterHub](https://jupyter.org/hub) / [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) configuration for one-person use and small team collaboration.

[Pull it from Docker Hub](https://hub.docker.com/repository/docker/joedeandev/personal-jupyterhub): `docker pull joedeandev/personal-jupyterhub:latest`

![](./logo.png)

## Purpose

Jupyter is an excellent but unwieldy tool. Setting it up, even on ones own computer, requires a significant time investment, and most JupyterHub solutions are designed for large organizations. This image aims to provide an easily-deployable, accessible, and feature-complete JupyterHub configuration.

This image can be a private data science notebook, a personal scripting server, a pair-programming environment, or a group project host.

## Performance and Security

The image weighs just under 3Gb, due to the dependencies needed for Jupyter, the kernels, and the document renderers. When running, the server uses around 100Mb of memory, and very little CPU. Individual kernels are run in the same container as the server, and thus notebook performance can be limited by the resources available to the container. With Jupyter's LocalProcessSpawner, there is no way to throttle single user servers, so don't give a login to any crypto-mining friends. Permissions are managed by Linux, and thus the container is fairly secure, but it's probably not the best place to store important SSH keys.

## Quickstart

1. *(Optional, only for enabling GitHub OAuth login)* Register a new GitHub OAuth app ([here](https://github.com/settings/applications/new)).
   1. Set "Application name" to something like "JupyterHub OAuth"
   2. Set "Homepage URL" to the server's host URL
   3. Set "Authorization callback URL" to "http://`<host>`/hub/oauth_callback"
   4. *(Optional)* The [logo](./logo.png) from this repository makes a nice icon for the application.
   5. Register the application
   6. Save the secret key, client ID, and callback URL
   7. Pass the `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `GITHUB_CALLBACK_URL` environment variables to the container, either via Docker Compose or the command line.
2. Prepare the deployment server to direct traffic to port 8000 of the container. This image is made to work smoothly with [SideProjectDeployment](https://github.com/joedeandev/SideProjectDeployment/). If using a reverse proxy, make sure that the cross-origin policy is valid, and that the WebSocket connections are handled properly. Refer to [the docs](https://jupyterhub.readthedocs.io/en/stable/reference/config-proxy.html) or the [example nginx.conf](./nginx.conf) for details.
3. Mount the `/home` and `/etc` directory as a volume. These directories are managed as volumes by default, so that the data can likely be retrieved even if improperly configured.
4. Spin up the container.
5. Access the server from a web browser.
6. Copy the provided administrator password, and use it to log in as `jupyterhub`.
7. *(Optional)* Open up a terminal session (it can take a second to warm up), and run `passwd` to change the administrator password. Don't lose it!
8. *(Optional)* Confirm that the server is running by running `print("Hello World")` in an IPython notebook.
9. Open the user management settings (File -> Hub Control Panel -> Admin) and create a new, non-admin user. If this username matches a GitHub account, then that user will be able to log in via GitHub's OAuth, assuming it is configured. Otherwise, a password must be configured for them (`sudo passwd <username>` in the terminal).

Log in as the newly created user, and get started!

## Administration

There is by default only one admin user, with the username `jupyterhub`. It is a good idea to use this user for administration only, and not have any other admin users. The password for this user is given once when the hub is first accessed, and should be changed immediately after. Creating an empty file at `/home/jupyterhub/.flag` will reset the password.

Users must be whitelisted before they can log in - this is managed at `/hub/admin` (File -> Hub Control Panel -> Admin). Users can be added or removed from the whitelist here. Users created through this interface have no password - if there is a corresponding GitHub user, then the GitHub OAuth login can be used, but otherwise a password must be configured. This can be done via the terminal interface (`sudo passwd <username>` as `jupyterhub`), or via `admin.py`.

The administration script at `/home/jupyterhub/admin.py` provides a simple interface for administration tasks. It can be run as `jupyterhub` with the command `sudo python admin.py <command>`. The following commands can be used:

* `setuser <username> <password>`: Creates the user if they do not exist. If the user does exist, then the password is changed. This does not add them to the whitelist - that must be done manually.
* `allowread <owner> <target>`: Grant a user read permissions to another's home directory. This also symlinks the target's home directory to a subdirectory of the owner's.
* `allowwrite <owner> <target>`: Same as `allowread`, but with write permissions as well.
* `disallow <owner> <target>`: Clear the permissions added by `allowread` and `allowread`, and unlink the home directory.

## Collaboration

### Asynchronous Collaboration

Any user can edit any file for which they have permissions. Symlinking a project (or running `admin.py allowwrite <owner> <target>`) is a good way to share files between users.

There may be save conflicts if the same file is modified by two users.

### Real-Time Collaboration

For [real-time collaboration](https://jupyterlab.readthedocs.io/en/stable/user/rtc.html), the same URL must be opened by the same user. User access can temporarily shared with `jupyter-link-share` (Share -> Share Jupyter Server Link), alongside a temporary token (``)

**Important security consideration:** Sharing a token gives full account access, until the token is revoked and the user server is restarted. Do not share a token owned by an admin account, and be sure to restart the user server after collaborating.

For this reason, it is recommended to create standalone users for collaborative projects.

### Recommended Approach

For collaborative projects, create a locally-authenticated user specifically for the project, and share the login details with any collaborators. The user can be removed from the whitelist afterwards, or even deleted. This can be done easily as the admin `jupyterhub` user:

* Create a user with a descriptive username: `sudo python admin.py setuser statisticsproject2021 superrsecurrepassword`
* *(Optional)* Grant a normal user write access: `sudo python admin.py allowwrite joedeandev statisticsproject2021`
* Share login details with collaborators, or even better, create tokens.

Log in as the new user, and collaborate.

## Features

* Combined PAM and GitHub OAuth login, with secure multi-user management
* Real-time collaborative editing
* Automatic culling of idle kernels
* Python 3.8 kernel, with popular packages (`numpy`, `scipy`, `pandas`, `flask`, etc.)
* Julia kernel (requires workaround: run `julia -e "using Pkg; Pkg.add(\"IJulia\"); Pkg.build(\"IJulia\");"` and restart user server)
* R kernel
* PDF, LaTeX, Markdown exports
* `jupyterlab-git` extension

## Potential Improvements

* Configure IJulia kernel to be built by default
* Upgrade Python to 3.10
* Read-only guest user
* Access logging
* Improve admin interface
