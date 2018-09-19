"""
A script to automate creation of user account
into an instance of Galaxy.

Galaxy instance details and the users list can be provided in one of three
ways:
1. In the YAML format via dedicated files (see ``users_list.yaml.sample`` for a
   sample of such a file)
2. On the command line as dedicated script options (see the usage help).
3. As a single composite parameter to the script. The parameter must be a
   single, YAML-formatted string with the keys corresponding to the keys
   available for use in the YAML formatted file (for example:
    `--yaml_user "{'username': 'user1', 'user_email':'user1@eXample.com',
    'password': 'private', 'group': 'group1'}"`).

Only one of the methods can be used with each invocation of the script but if
more than one are provided are provided, precedence will correspond to order
of the items in the list above.

NB. The Galaxy instance must have the allow_user_creation option set to True
    in the config/galaxy.ini configuration file.

Usage:
    python create_galaxy_users.py [-h]

Required libraries:
    bioblend, pyyaml
"""
import datetime as dt
import logging
import time
import yaml
from argparse import ArgumentParser

from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.users import UserClient
from bioblend.galaxy.groups import GroupsClient
from bioblend.galaxy.client import ConnectionError

# Omit (most of the) logging by external libraries
logging.getLogger('bioblend').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
try:
    logging.captureWarnings(True)  # Capture HTTPS warngings from urllib3
except AttributeError:
    pass


class ProgressConsoleHandler(logging.StreamHandler):
    """
    A handler class which allows the cursor to stay on
    one line for selected messages
    """
    on_same_line = False

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            same_line = hasattr(record, 'same_line')
            if self.on_same_line and not same_line:
                stream.write('\r\n')
            stream.write(msg)
            if same_line:
                stream.write('.')
                self.on_same_line = True
            else:
                stream.write('\r\n')
                self.on_same_line = False
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def _setup_global_logger():
    formatter = logging.Formatter('%(asctime)s %(levelname)-5s - %(message)s')
    progress = ProgressConsoleHandler()
    file_handler = logging.FileHandler('/tmp/user_creation.log')
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(progress)
    logger.addHandler(file_handler)
    return logger


def log_user_success(user, start, end, created_users):
    """
    Log successfull user creation.

    """
    created_users.append(user)
    log.debug("\tUser {} [{}] created successfully (in {})"
              .format(user['username'], user['user_email'],
                      str(end - start)))


def log_user_error(user, start, end, e, errored_users):
    """
    Log failed user creation.

    """
    user['error'] = e.body
    errored_users.append(user)
    log.error("\t* Error creating user {} [{}] after {}\nError: {}"
              .format(user['username'], user['user_email'],
                      str(end - start), user['error']))


def load_input_file(user_list_file='user_list.yaml'):
    """
    Load YAML from the `user_list_file` and return a dict with the content.
    """
    with open(user_list_file, 'r') as f:
        ul = yaml.load(f)
    return ul


def dump_to_yaml_file(content, file_name):
    """
    Dump YAML-compatible `content` to `file_name`.
    """
    with open(file_name, 'w') as f:
        yaml.dump(content, f, default_flow_style=False)


def galaxy_instance(url=None, api_key=None):
    """
    Get an instance of the `GalaxyInstance` object. If the arguments are not
    provided, load the default values using `load_input_file` method.
    """
    if not (url and api_key):
        tl = load_input_file()
        url = tl['galaxy_instance']
        api_key = tl['api_key']
    return GalaxyInstance(url, api_key)


def user_client(gi=None):
    """
    Get an instance of the `UserClient` on a given Galaxy instance. If no
    value is provided for the `galaxy_instance`, use the default provided via
    `load_input_file`.
    """
    if not gi:
        gi = galaxy_instance()
    return UserClient(gi)


def group_client(gi=None):
    """
    Get an instance of the `GroupClient` on a given Galaxy instance. If no
    value is provided for the `galaxy_instance`, use the default provided via
    `load_input_file`.
    """
    if not gi:
        gi = galaxy_instance()
    return GroupsClient(gi)


def existing_user_list(gi):
    """
    Get a list of users on a Galaxy instance.

    :type gi: GalaxyInstance object
    :param gi: A GalaxyInstance object as retured by `galaxy_instance` method.
    :rtype: list
    :return: A list of dicts with user details. For example:

            [{u'email': u'a_user@example.com', u'id': u'dda47097d9189f15', u'url': u'/api/users/dda47097d9189f15'}]
    """
    uc = user_client(gi)
    return uc.get_users()


def existing_group_list(gi):
    """
    Get a list of groups on a Galaxy instance.

    :type gi: GalaxyInstance object
    :param gi: A GalaxyInstance object as retured by `galaxy_instance` method.
    :rtype: list
    :return: A list of dicts with details on individual groups. For example:

            [{'id': '33abac023ff186c2',
              'model_class': 'Group',
              'name': 'Listeria',
              'url': '/api/groups/33abac023ff186c2'},
             {'id': '73187219cd372cf8',
              'model_class': 'Group',
              'name': 'LPN',
              'url': '/api/groups/73187219cd372cf8'}]
    """
    gc = group_client(gi)
    return gc.get_groups()


def user_exists(user, eul):
    if eul:
        return next((u for u in eul if u["username"] == user['username']), False)
    return False


def group_exists(user, egl):
    if egl:
        return next((g for g in egl if g["name"] == user['group']), False)
    return False


def create_user(user, uc, gc, egl):
    """
    Creates single user
    """
    response = uc.create_local_user(username=user['username'],
                                    user_email=user['user_email'],
                                    password=user['password'])
    user_id = response.get('id')
    if user_id and user['group']:
        group_info = group_exists(user, egl)
        if not group_info:
            response = gc.create_group(group_name= user['group'],
                                       user_ids=[user_id])
        else:
            group_id = group_info['id']
            response = gc.add_group_user(group_id=group_id,
                                         user_id=user_id)
    return response


def _parse_cli_options():
    """
    Parse command line options, returning `parse_args` from `ArgumentParser`.
    """
    parser = ArgumentParser(usage="usage: python %(prog)s <options>")

    parser.add_argument("-g", "--galaxy",
                        dest="galaxy_url",
                        help="Target Galaxy instance URL/IP address (required "
                             "if not defined in the tools list file)",)

    parser.add_argument("-a", "--apikey",
                        dest="api_key",
                        help="Galaxy admin user API key (required if not "
                             "defined in the tools list file)",)

    parser.add_argument("-f", "--usersfile",
                        dest="user_list_file",
                        help="Users file to create (see user_list.yaml.sample)",)

    parser.add_argument("-y", "--yaml_user",
                        dest="user_yaml",
                        help="Create user represented by yaml string",)

    parser.add_argument("--username",
                        help="The alias of the user to create (only applicable "
                             "if the users file is not provided).")

    parser.add_argument("--email",
                        dest="user_email",
                        help="The email address of the user to create (only applicable "
                             "if the users file is not provided).")

    parser.add_argument("--password",
                        help="The password of the user to create (only applicable "
                             "if the users file is not provided).")

    parser.add_argument("--group",
                        help="The group of the user to create (only applicable "
                             "if the users file is not provided).")

    return parser.parse_args()


def create_users(options):
    """
    Parse the default input file and proceed to create listed users.

    :type options: OptionParser object
    :param options: command line arguments parsed by OptionParser
    """
    istart = dt.datetime.now()
    user_list_file = options.user_list_file
    if user_list_file:
        ul = load_input_file(user_list_file)  # Input file contents
        users_info = ul['users']  # The list of users to create
    elif options.tool_yaml:
        users_info = [yaml.load(options.user_yaml)]
    else:
        # An individual tool was specified on the command line
        users_info = [{"username": options.username,
                       "user_email": options.user_email,
                       "password": options.password,
                       "group": options.group}]

    galaxy_url = options.galaxy_url or ul.get('galaxy_instance')
    api_key = options.api_key or ul.get('api_key')
    gi = galaxy_instance(galaxy_url, api_key)
    uc = user_client(gi)
    gc = group_client(gi)


    responses = []
    errored_users = []
    skipped_users = []
    existing_users = []
    created_users = []
    counter = 0

    total_num_users = len(users_info)
    default_err_msg = ('All users that you are attempting to create '
                       'have been previously created.')

    # Process each users: check if it's already in or install it

    for user_info in users_info:
        counter += 1
        user = dict()  # Payload for the user we are creating

        eul = existing_user_list(gi)  # existing user list
        egl = existing_group_list(gi)  # existing group list

        # Copy required `user_info` keys into the `user` dict
        user['username'] = user_info.get('username')
        user['user_email'] = user_info.get('user_email')
        user['password'] = user_info.get('password')
        user['group'] = user_info.get('group')

        # Check if all required user sections have been provided; if not, skip
        # the creation of this user.

        if not user['username'] or not user['user_email'] or not user['password']:
            log.error("Missing required user info field; skipping [username: '{}'; "
                      "user_email: '{}'; password: '{}']; group: '{}'"
                      .format(user['username'], user['user_email'],
                              user['password'], user['group']))
            continue

        # Check if the tool@revision is already installed

        if user_exists(user, eul):
            log.debug("({}/{}) User {} [{}] already exists. Skipping."
                        .format(counter, total_num_users, user['username'], user['user_email']))
            skipped_users.append(user)
            continue
        else:
            # Initate user creation
            start = dt.datetime.now()
            log.debug("({}/{}) Creating user {} [{}] (TRT: {})"
                      .format(counter, total_num_users, user['username'], user['user_email'],
                              dt.datetime.now() - istart))

        try:
            response = create_user(user, uc, gc, egl)

            end = dt.datetime.now()
            log_user_success(user=user, start=start, end=end,
                             created_users=created_users)
        except ConnectionError, e:
            response = None
            end = dt.datetime.now()
            log_user_error(user=user, start=start, end=end,
                           e=e, errored_users=errored_users)
        outcome = dict(user=user,
                       response=response,
                       duration=str(end - start))
        responses.append(outcome)

    log.info("Created users ({}): {}".format(
        len(created_users), [(t['username'], t['user_email']) for t in created_users]))
    log.info("Skipped tools ({}): {}".format(
        len(skipped_users), [(t['username'], t['user_email']) for t in skipped_users]))
    log.info("Errored users ({}): {}".format(
        len(errored_users), [(t['username'], t['user_email']) for t in errored_users]))

    log.info("All users listed in '{}' have been processed.".format(user_list_file))
    log.info("Total run time: {}".format(dt.datetime.now() - istart))


if __name__ == "__main__":
    global log
    log = _setup_global_logger()
    options = _parse_cli_options()
    if options.user_list_file or (options.username and options.email and options.password):
        create_users(options)
    else:
        log.error("Must provide the user list file or individual users info; "
                  "look at usage.")