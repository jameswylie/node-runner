import json
import subprocess
from datetime import datetime
import requests
import sys, os


def printCommand(cmd):
    print('-----------------------------')
    if type(cmd) is list:
        print('Running command :' + ' '.join(cmd))
        print('-----------------------------')
    else:
        print('Running command ' + cmd)
        print('-----------------------------')


def run_shell_command(cmd, env=None, shell=False, fail_on_error=True, quite=False):
    printCommand(cmd)
    if env:
        result = subprocess.run(cmd, env=env, shell=shell)
    else:
        result = subprocess.run(cmd, shell=shell)
    if fail_on_error and result.returncode != 0:
        print("""
            Command failed. Exiting...
        """)
        sys.exit()
    return result


class Helpers:
    @staticmethod
    def is_json(myjson):
        try:
            json_object = json.loads(myjson)
        except ValueError as e:
            return False
        return True

    @staticmethod
    def pretty_print_request(req):
        print('{}\n{}\r\n{}\r\n\r\n{}\n{}'.format(
            '-----------Request-----------',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
            '-------------------------------'
        ))

    @staticmethod
    def send_request(prepared, print_request=False, print_response=True):
        if print_request:
            Helpers.pretty_print_request(prepared)
        s = requests.Session()
        resp = s.send(prepared, verify=False)
        if Helpers.is_json(resp.content):
            response_content = json.dumps(resp.json())
        else:
            response_content = resp.content

        if print_response:
            print(response_content)
        return resp

    @staticmethod
    def get_nginx_user():
        nginx_admin_password = 'NGINX_ADMIN_PASSWORD'
        if os.environ.get('%s' % nginx_admin_password) is None:
            print("""
            ------
            NGINX_ADMIN_PASSWORD is missing !
            Setup NGINX_ADMIN_PASSWORD environment variable using below command . Replace the string 'nginx_password_of_your_choice' with your password

            echo 'export NGINX_ADMIN_PASSWORD="nginx_password_of_your_choice"' >> ~/.bashrc
            """)
            sys.exit()
        else:
            return dict({
                "name": "admin",
                "password": os.environ.get("%s" % nginx_admin_password)
            })

    @staticmethod
    def docker_compose_down(composefile, remove_volumes):
        command = ['docker-compose', '-f', composefile, 'down']
        if remove_volumes:
            command.append('-v')
        run_shell_command(command)

    @staticmethod
    def get_public_ip():
        return requests.get('https://api.ipify.org').text

    @staticmethod
    def get_current_date_time():
        now = datetime.now()
        return now.strftime("%Y_%m_%d_%H_%M")

    @staticmethod
    def get_application_path():
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            print(f"Getting application for executable {sys._MEIPASS}")
            application_path = sys._MEIPASS
        else:
            print("Getting application for file")
            application_path = os.path.dirname(os.path.abspath(__file__))

        return application_path
