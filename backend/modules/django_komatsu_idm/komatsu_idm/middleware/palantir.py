"""
Custom Palantir middleware to retrieve user data from Palantir and put
in request object so it's available anywhere in views or templates.
"""
import time
from django.conf import settings
from dev_mykomatsu_sdk.ontology.objects import MyKomatsuUser, MyKomatsuRole
from komatsu_idm.main import sdk_client as client


class PalantirUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Try and get Palantir user from JWT 'oid' param and add PalantirUser to request object.
        """
        request.palantir_user = get_palantir_user(request)
        return self.get_response(request)


class PalantirUser:
    """
    There are a few properties in user_json that are promised, set by default to make
    downstream user properites checking easier.
    This is the default props every user is created with that you can guarantee will exist:
    user_data = {
            'userId': '',
            'type': '',
            'role_data': {
                    'primary_user_role': {
                            'customerId': '',
                            'distributorId': '',
                    },
                    'user_roles': []
            }
    }
    """

    def __init__(self):
        # Default props
        self.__start_time = time.time()
        self.__performance = {"fetch_and_set": 0}
        self.__user_json = {}
        self.is_valid_user = False
        self.is_distributor = False
        self.is_customer = False
        self.is_komatsu = False
        self.is_admin = False
        self.is_super_admin = False
        self.distributor_id = None
        self.customer_id = None
        self.location_ids = []
        self.branch_ids = []

    def set_properties(self, data):
        """
        Check and set props based on init data.
        """
        self.__user_json = data
        self.__sanitize_user_json()
        self.__set_valid_user()

        if self.is_valid_user:
            self.__set_ids()
            self.__set_role()
            self.__set_admin()  # From 'type'
            self.__set_super_admin()

        # TEMP until Azure monitor gets setup.
        self.__performance[
            "fetch_and_set"
        ] = f"{round(time.time()-self.__start_time, 2)}s"

    def __sanitize_user_json(self):
        """
        Clean up some data before we process it.
        """
        if self.__user_json["role_data"]["primary_user_role"]["customerId"] in [
            None,
            "",
            "None",
        ]:
            self.__user_json["role_data"]["primary_user_role"]["customerId"] = None
        if self.__user_json["role_data"]["primary_user_role"]["distributorId"] in [
            None,
            "",
            "None",
        ]:
            self.__user_json["role_data"]["primary_user_role"]["distributorId"] = None

    def __set_valid_user(self):
        if self.__user_json.get("userId", None) or self.__user_json.get(
            "user_id", None
        ):
            self.is_valid_user = True

    def __set_ids(self):
        # By default/promise, these will always exist via "get_palantir_user" (creates users)
        # They are set to None by default and cleaned up in "__sanitize_user_json" before this is called.
        self.customer_id = self.__user_json["role_data"]["primary_user_role"][
            "customerId"
        ]
        self.distributor_id = self.__user_json["role_data"]["primary_user_role"][
            "distributorId"
        ]

        # Branch and location can be defined in each role,
        # so we extract from each role in "roles" and add one from primary role.
        branch_ids = [
            x.get("branchId", "")
            for x in self.__user_json["role_data"].get("user_roles", [])
        ]
        branch_ids.append(
            self.__user_json["role_data"]["primary_user_role"].get("branchId", "")
        )
        self.branch_ids = [v.strip() for v in branch_ids if v]

        location_ids = [
            x.get("locationId", "")
            for x in self.__user_json["role_data"].get("user_roles", [])
        ]
        location_ids.append(
            self.__user_json["role_data"]["primary_user_role"].get("locationId", "")
        )
        self.location_ids = [v.strip() for v in location_ids if v]

    def __set_admin(self):
        """
        Admin determination comes from 'type'. Not guaranteed to exist, not sanitized.
        """
        user_type = self.__user_json.get("type", None)

        if user_type:
            user_type = user_type.strip().lower()

        self.is_admin = user_type == "admin"

    def __set_role(self):
        """
        Roles are: distributor|customer|komatsu.
        """
        # This is the proper way to do this, but use ID existence for now until we get 2 new fields added to Palantir role obj.
        # try:
        # 	user_role = self.__user_json['role_data']['primary_user_role'].get('role').strip().lower()
        # except:
        # 	user_role = None
        #
        # if user_role == 'distributor':
        # 	self.is_distributor = True
        # elif user_role == 'customer':
        # 	self.is_customer = True
        # elif user_role == 'komatsu':
        # 	self.is_komatsu = True

        # TEMP solution until we get two new fields added to role object in Palantir
        if self.distributor_id:
            self.is_distributor = True
        elif self.customer_id:
            self.is_customer = True
        else:
            self.is_komatsu = True

    def __set_super_admin(self):
        """
        Superusers can access everything.
        """
        self.is_super_admin = self.is_komatsu and self.is_admin

    def get_json_data(self):
        json_data = {
            "palantir_middleware_data": {
                "performance": self.__performance,
                "is_valid_user": self.is_valid_user,
                "is_distributor": self.is_distributor,
                "is_customer": self.is_customer,
                "is_komatsu": self.is_komatsu,
                "is_admin": self.is_admin,
                "is_super_admin": self.is_super_admin,
                "distributor_id": self.distributor_id,
                "customer_id": self.customer_id,
                "branch_ids": self.branch_ids,
                "location_ids": self.location_ids,
            }
        }

        # Merge user_json and middleware data together,
        json_data.update(self.__user_json)

        return json_data


def get_palantir_user(request):
    palantir_user = PalantirUser()

    # Get oid (Entra "object id") from decoded JWT data. It's used for the Palantir user id.
    jwt_user_id = request.jwt_data.get("oid", None)

    # For DEV/TESTING:
    # Allow entraID to come in thru GET or POST to override/set
    # a specific user making the request.
    if settings.DEBUG:
        jwt_user_id = request.GET.get("entra_id", jwt_user_id)
        jwt_user_id = request.POST.get("entra_id", jwt_user_id)

    if jwt_user_id:
        try:
            sdk_client = client()

            # Try and get "active" user with specified user ID from JWT (oid).
            palantir_user_data = sdk_client.ontology.objects.MyKomatsuUser.where(
                MyKomatsuUser.entra_id.__eq__(jwt_user_id)
                & ~MyKomatsuUser.soft_delete_flag.__eq__(settings.DELETE_FLAG)
            ).take(1)[0]

            # Get user's roles.
            palantir_role_data = sdk_client.ontology.objects.MyKomatsuRole.where(
                MyKomatsuRole.user_id.__eq__(palantir_user_data.user_id)
            )

            primary_role = {
                "customerId": None,
                "distributorId": None,
            }

            # Loop thru all user roles. If they have a primary, put it into it's own object.
            # Put ALL OTHER roles into "roles" array.
            user_roles = []
            for role in palantir_role_data.iterate():
                if role._asdict()["id"] == palantir_user_data.home_role_id:
                    primary_role = role._asdict()
                else:
                    user_roles.append(role._asdict())

            # Set user object with returned data and update Palantir user with it.
            # Then we return Palantir user to be added to request.
            user_data = palantir_user_data._asdict()
            user_data["role_data"] = {
                "primary_user_role": primary_role,
                "user_roles": user_roles,
            }

            # Update our default palantir user object with data from palantir,
            # Then return it.
            palantir_user.set_properties(user_data)

        except Exception as ex:
            # TEMP until we get Azure Monitor setup.
            print(f">> Error getting Palantir user, error: {ex}")
            pass

    return palantir_user
