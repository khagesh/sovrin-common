from plenum.common.constants import TRUSTEE, STEWARD, NODE
from plenum.common.log import getlogger
from sovrin_common.constants import OWNER, POOL_UPGRADE, TGB, TRUST_ANCHOR, NYM
from sovrin_common.roles import Roles

logger = getlogger()


class Authoriser:
    ValidRoles = (TRUSTEE, TGB, STEWARD, TRUST_ANCHOR, None)

    AuthMap = {
        '{}_role__{}'.format(NYM, TRUSTEE):
            {TRUSTEE: []},
        '{}_role__{}'.format(NYM, TGB):
            {TRUSTEE: []},
        '{}_role__{}'.format(NYM, STEWARD):
            {TRUSTEE: []},
        '{}_role__{}'.format(NYM, TRUST_ANCHOR):
            {TRUSTEE: [], STEWARD: []},
        '{}_role__'.format(NYM):
            {TRUSTEE: [], TGB: [], STEWARD: [], TRUST_ANCHOR: []},
        '{}_role_{}_'.format(NYM, TRUSTEE):
            {TRUSTEE: []},
        '{}_role_{}_'.format(NYM, TGB):
            {TRUSTEE: []},
        '{}_role_{}_'.format(NYM, STEWARD):
            {TRUSTEE: []},
        '{}_role_{}_'.format(NYM, TRUST_ANCHOR):
            {TRUSTEE: []},
        '{}_verkey_<any>_<any>'.format(NYM):
            {r: [OWNER] for r in ValidRoles},
        '{}_services__[VALIDATOR]'.format(NODE):
            {STEWARD: [OWNER, ]},
        # TODO: should a steward be allowed to suspend its validator?
        '{}_services_[VALIDATOR]_[]'.format(NODE):
            {TRUSTEE: [], STEWARD: [OWNER, ]},
        '{}_services_[]_[VALIDATOR]'.format(NODE):
            {TRUSTEE: []},
        '{}_node_ip_<any>_<any>'.format(NODE):
            {STEWARD: [OWNER, ]},
        '{}_node_port_<any>_<any>'.format(NODE):
            {STEWARD: [OWNER, ]},
        '{}_client_ip_<any>_<any>'.format(NODE):
            {STEWARD: [OWNER, ]},
        '{}_client_port_<any>_<any>'.format(NODE):
            {STEWARD: [OWNER, ]},
        '{}_action__start'.format(POOL_UPGRADE):
            {TRUSTEE: [], TGB: []},
        '{}_action_start_cancel'.format(POOL_UPGRADE):
            {TRUSTEE: [], TGB: []}
    }

    @staticmethod
    def isValidRole(role) -> bool:
        return role in Authoriser.ValidRoles

    @staticmethod
    def getRoleFromName(roleName) -> bool:
        if not roleName:
            return None
        return Roles[roleName].value

    @staticmethod
    def isValidRoleName(roleName) -> bool:
        if not roleName:
            return True

        try:
            Authoriser.getRoleFromName(roleName)
        except KeyError:
            return False

        return True

    @staticmethod
    def authorised(typ, field, actorRole, oldVal=None, newVal=None,
                   isActorOwnerOfSubject=None) -> (bool, str):
        oldVal = '' if oldVal is None else \
            str(oldVal).replace('"', '').replace("'", '')
        newVal = '' if newVal is None else \
            str(newVal).replace('"', '').replace("'", '')
        key = '_'.join([typ, field, oldVal, newVal])
        if key not in Authoriser.AuthMap:
            key = '_'.join([typ, field, '<any>', '<any>'])
            if key not in Authoriser.AuthMap:
                msg = "key '{}' not found in authorized map". \
                    format(key)
                logger.error(msg)
                return False, msg
        roles = Authoriser.AuthMap[key]
        if actorRole not in roles:
            return False, '{} not in allowed roles {}'.format(actorRole, roles)
        roleDetails = roles[actorRole]
        if len(roleDetails) == 0:
            return True, ''
        else:
            r = OWNER in roleDetails and isActorOwnerOfSubject
            msg = '' if r else 'Only owner is allowed'
            return r, msg
