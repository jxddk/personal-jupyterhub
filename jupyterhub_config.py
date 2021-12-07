from os import environ, remove
from os.path import isfile
from jupyterhub.spawner import LocalProcessSpawner
from oauthenticator.github import LocalGitHubOAuthenticator
import pamela
from subprocess import check_output
from string import ascii_letters, digits
from random import choice
from sys import executable


class PAMLocalGitHubOAuthenticator(LocalGitHubOAuthenticator):
    def authenticate(self, handler, data=None):
        username = None
        try:
            control = data["control"]
            username = data["username"]
            password = data["password"]
            if control != "local":
                raise KeyError()
            pamela.authenticate(username, password)
            return username
        except pamela.PAMError as e:
            if handler is not None:
                self.log.warning(
                    "PAM Authentication failed (%s@%s): %s",
                    username,
                    handler.request.remote_ip,
                    e,
                )
            else:
                self.log.warning("PAM Authentication failed: %s", e)
        except (KeyError, TypeError):
            return super().authenticate(handler, data)

    def get_custom_html(self, base_url):
        if isfile(".flag"):
            remove(".flag")
            new_password = "".join([choice(ascii_letters + digits) for _ in range(24)])
            hashed = check_output(
                ["/usr/bin/openssl", "passwd", new_password]
            ).decode()[:-1]
            check_output(["/usr/sbin/usermod", "-p", hashed, "jupyterhub"])
            return f"""
                <form style="width: 100%" action="/" method="GET" role="form">
                  <div class="auth-form-header">Admin Password Generated</div>
                  <div class="auth-form-body">
                    <p><label>Password:</label> {new_password}</p>
                    <hr>
                    <p>This password allows you to log in as an admin. Save it, because you will not be able to see it again!</p>
                    <a role="button" class="btn btn-jupyter" style="width: 100%" href="/">Continue</a>
                  </div>
                </form>
            """

        return f"""
            <form style="width: 100%" action="/hub/login?next=%2Fhub%2F" method="post" role="form">
              <div class="auth-form-header">Sign in</div>
              <div class="auth-form-body">
                <label for="username">Username:</label>
                <input id="username" type="text" autocapitalize="none" autocorrect="off" class="form-control" name="username" val="" tabindex="1" autofocus="autofocus">
                <label for="password">Password:</label>
                <input type="password" class="form-control" name="password" id="password" tabindex="2">
                <input type="hidden" name="control" id="control" value="local">
                <div class="feedback-container">
                  <input id="login_submit" type="submit" class="btn btn-jupyter" style="width: 100%" value="Sign in" tabindex="3">
                  <div class="feedback-widget hidden"><i class="fa fa-spinner"></i></div>
                </div>
                <hr>
                {
                    '''<label style="display: block">Log in using third-party OAuth:</label>
                    <a role="button" class="btn btn-jupyter" style="width: 100%" href="/hub/oauth_login?next=%2Fhub%2F">Log in via GitHub</a>
                    <hr>'''
                    if environ.get('GITHUB_CLIENT_SECRET', 'GITHUB_CLIENT_SECRET') != 'GITHUB_CLIENT_SECRET' else ''
                }
                <a style="width: 100%" href="https://github.com/joedeandev/personal-jupyterhub">Read the docs for Personal JupyterHub on GitHub</a>
              </div>
            </form>
        """


c.JupyterHub.db_url = "jupyterhub.sqlite"
c.JupyterHub.admin_access = False
c.NotebookApp.allow_origin = "*"
origin = "*"
c.JupyterHub.tornado_settings = {
    "headers": {
        "Access-Control-Allow-Origin": origin,
    },
}
c.Spawner.cmd = ["jupyter-labhub"]
c.Spawner.args = ["--collaborative", "--NotebookApp.allow_origin={0}".format(origin)]
c.LocalGitHubOAuthenticator.client_id = environ.get(
    "GITHUB_CLIENT_ID", "GITHUB_CLIENT_ID"
)
c.LocalGitHubOAuthenticator.client_secret = environ.get(
    "GITHUB_CLIENT_SECRET", "GITHUB_CLIENT_SECRET"
)
c.LocalGitHubOAuthenticator.oauth_callback_url = environ.get(
    "GITHUB_CALLBACK_URL", "GITHUB_CALLBACK_URL"
)
c.JupyterHub.services = [
    {
        "name": "jupyterhub-idle-culler-service",
        "command": [
            executable,
            "-m",
            "jupyterhub_idle_culler",
            "--timeout=1800",
        ],
        "admin": True,
    }
]
c.JupyterHub.authenticator_class = PAMLocalGitHubOAuthenticator
c.JupyterHub.spawner_class = LocalProcessSpawner
c.PAMLocalGitHubOAuthenticator.create_system_users = True
c.PAMLocalGitHubOAuthenticator.admin_users = {"jupyterhub"}
c.PAMLocalGitHubOAuthenticator.allowed_users = {"jupyterhub"}
