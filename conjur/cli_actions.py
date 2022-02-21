"""
CLI Actions module

This module holds the run logic of each command.

"""

# Builtin
import sys

# SDK
from conjur_api.interface import CredentialsProviderInterface
from conjur_api.models import CreateHostData, CreateTokenData, ListMembersOfData, ListPermittedRolesData, \
    CredentialsData

# Internal
# pylint: disable=too-many-arguments
from conjur.controller.hostfactory_controller import HostFactoryController

from conjur.errors import ConflictingParametersException, FileNotFoundException, InvalidFilePermissionsException
from conjur.logic.hostfactory_logic import HostFactoryLogic
from conjur.controller import InitController, LoginController, \
    LogoutController, ListController, VariableController, \
    PolicyController, HostController
from conjur.logic import InitLogic, LoginLogic, LogoutLogic, ListLogic, VariableLogic, \
    PolicyLogic
from conjur.data_object import ConjurrcData, HostResourceData, ListData, VariableData, \
    PolicyData
from conjur.util.ssl_utils import SSLClient
from conjur.util import init_utils, util_functions


# pylint: disable=raise-missing-from
def handle_init_logic(
        url: str = None, account: str = None,
        cert: str = None, force: bool = None,
        ssl_verify=None, is_self_signed: bool = False):
    """
    Method that wraps the init call logic
    Initializes the client, creating the .conjurrc file
    """
    try:
        init_utils.validate_init_action_ssl_verification_input(cert, is_self_signed, ssl_verify)
    except ConflictingParametersException:
        raise ConflictingParametersException("Can't accept more than one of the following "
                                             "arguments:"
                                             "\n1. --ca-cert"
                                             "\n2. --self-signed"
                                             "\n3. --insecure (skip certificate validation)")
    except FileNotFoundException:
        raise FileNotFoundException(f"Couldn't find '{cert}'. Make sure correct path is provided")
    except InvalidFilePermissionsException:
        raise InvalidFilePermissionsException(f"No read access for: {cert}")

    ssl_verification_data = init_utils.get_ssl_verification_meta_data_from_cli_params(cert, is_self_signed, ssl_verify)
    ssl_service = SSLClient()
    # TODO conjurrcData creation should move to controller
    conjurrc_data = ConjurrcData(conjur_url=url,
                                 account=account,
                                 cert_file=cert)

    init_logic = InitLogic(ssl_service)
    input_controller = InitController(conjurrc_data=conjurrc_data,
                                      init_logic=init_logic,
                                      force=force,
                                      ssl_verification_data=ssl_verification_data)
    input_controller.load()


# pylint: disable=line-too-long
def handle_login_logic(
        credential_provider: CredentialsProviderInterface, identifier: str = None,
        password: str = None, ssl_verify: bool = True):
    """
    Method wraps the login call logic
    """
    credential_data = CredentialsData(username=identifier)
    login_logic = LoginLogic(credential_provider)
    ssl_verification_metadata = util_functions.get_ssl_verification_meta_data_from_conjurrc(ssl_verify)
    login_controller = LoginController(ssl_verification_metadata=ssl_verification_metadata,
                                       user_password=password,
                                       credential_data=credential_data,
                                       login_logic=login_logic)
    login_controller.load()

    sys.stdout.write("Successfully logged in to Conjur\n")


def handle_logout_logic(credential_provider: CredentialsProviderInterface):
    """
    Method wraps the logout call logic
    """
    logout_logic = LogoutLogic(credential_provider)
    logout_controller = LogoutController(logout_logic=logout_logic,
                                         credentials_provider=credential_provider)
    logout_controller.remove_credentials()


def handle_list_logic(args: list = None, client=None):
    """
    Method wraps the list call logic
    """
    list_logic = ListLogic(client)
    list_controller = ListController(list_logic=list_logic)

    if args.permitted_roles_identifier:
        list_permitted_roles_data = ListPermittedRolesData(
            identifier=args.permitted_roles_identifier,
            privilege=args.privilege)
        list_controller.get_permitted_roles(list_permitted_roles_data)
    elif args.members_of:
        list_role_members_data = ListMembersOfData(kind=args.kind,
                                                   identifier=args.members_of,
                                                   inspect=args.inspect,
                                                   search=args.search,
                                                   limit=args.limit,
                                                   offset=args.offset)
        list_controller.get_role_members(list_role_members_data)
    else:
        list_data = ListData(kind=args.kind, inspect=args.inspect,
                             search=args.search, limit=args.limit,
                             offset=args.offset, role=args.role)
        list_controller.load(list_data)


def handle_hostfactory_logic(args: list = None, client=None):
    """
        Method wraps the hostfactory call logic
    """
    if args.action_type == 'create_token':
        hostfactory_logic = HostFactoryLogic(client)

        create_token_data = CreateTokenData(host_factory=args.hostfactoryid,
                                            cidr=args.cidr,
                                            days=args.duration_days,
                                            hours=args.duration_hours,
                                            minutes=args.duration_minutes)
        hostfactory_controller = HostFactoryController(hostfactory_logic=hostfactory_logic)
        hostfactory_controller.create_token(create_token_data)
    elif args.action_type == 'create_host':
        hostfactory_logic = HostFactoryLogic(client)

        create_host_data = CreateHostData(host_id=args.id,
                                          token=args.token)
        hostfactory_controller = HostFactoryController(hostfactory_logic=hostfactory_logic)
        hostfactory_controller.create_host(create_host_data)
    elif args.action_type == 'revoke_token':
        hostfactory_logic = HostFactoryLogic(client)
        hostfactory_controller = HostFactoryController(hostfactory_logic=hostfactory_logic)
        hostfactory_controller.revoke_token(args.token)


def handle_variable_logic(args: list = None, client=None):
    """
    Method wraps the variable call logic
    """
    variable_logic = VariableLogic(client)
    if args.action == 'get':
        variable_data = VariableData(action=args.action, id=args.identifier, value=None,
                                     variable_version=args.version)
        variable_controller = VariableController(variable_logic=variable_logic,
                                                 variable_data=variable_data)
        variable_controller.get_variable()
    elif args.action == 'set':
        variable_data = VariableData(action=args.action, id=args.identifier, value=args.value,
                                     variable_version=None)
        variable_controller = VariableController(variable_logic=variable_logic,
                                                 variable_data=variable_data)
        variable_controller.set_variable()


def handle_policy_logic(policy_data: PolicyData = None, client=None):
    """
    Method wraps the variable call logic
    """
    policy_logic = PolicyLogic(client)
    policy_controller = PolicyController(policy_logic=policy_logic,
                                         policy_data=policy_data)
    policy_controller.load()


def handle_host_logic(args, client):
    """
    Method wraps the host call logic
    """
    host_resource_data = HostResourceData(action=args.action, host_to_update=args.id)
    host_controller = HostController(client=client, host_resource_data=host_resource_data)
    host_controller.rotate_api_key()
