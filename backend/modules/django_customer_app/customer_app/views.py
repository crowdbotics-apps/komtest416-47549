import time

from customer_app.models import CustomerOrganizationModel
from customer_app.serializer import (
    CustomerListSerializer,
    CustomerSerializer,
    ParentCustomerListSerializer,
)
from dev_mykomatsu_sdk.ontology.objects import MyKomatsuCustomerOrganization
from dev_mykomatsu_sdk.types import ActionConfig, ActionMode
from django.conf import settings
from helpers import perf_diff_time, value_exists
from modules.django_komatsu_idm.komatsu_idm.main import sdk_client as client
from modules.django_komatsu_permissions.permissions.common import *
from response_codes import custom_res_codes
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class CustomerViewset(viewsets.ViewSet):
    """
    GET:
        param:
            page_num (default=1)
            page_size (default=20)
    POST:
        create single obj (NOT IMPLEMENTED YET)

    /cust_account_code
    GET: Retrieve single object
    PUT: Update single object
    DELETE: Delete single object

    """

    # permission_classes = [IsCustomer|IsDistributor]

    def list(self, request, *args, **kwargs):
        # GET
        try:
            page_no = int(
                self.request.query_params.get("page_num", settings.PAGE_NUM)
            )  # TODO: Will add this in serializer later
            page_size = int(
                self.request.query_params.get("page_size", settings.PAGE_SIZE)
            )
            parent = self.request.query_params.get("parent", None)
            sort_by_field = self.request.query_params.get("sort_by", None)
            search_query = self.request.query_params.get("search", None)

            filter_dict = {}
            for key in CustomerOrganizationModel.FILTER_KEYS:
                if self.request.query_params.get(key, None):
                    filter_dict[key] = self.request.query_params.getlist(key, None)

            performance_data = {}
            view_start_time = time.time()
            if value_exists(parent):
                start_time = time.time()

                customer_count = (
                    CustomerOrganizationModel.objects()
                    .where(MyKomatsuCustomerOrganization.parent.__eq__(parent))
                    .count()
                    .compute()
                )

                customer_obj = (
                    CustomerOrganizationModel.objects()
                    .where(MyKomatsuCustomerOrganization.parent.__eq__(parent))
                    .page(page_size=page_size)
                )

                performance_data["customer_count_fetch"] = perf_diff_time(
                    start_time, time.time()
                )

                start_time = time.time()

                customer_count = (
                    CustomerOrganizationModel.objects()
                    .where(MyKomatsuCustomerOrganization.parent.__eq__(parent))
                    .count()
                    .compute()
                )
                customer_obj = (
                    CustomerOrganizationModel.objects()
                    .where(MyKomatsuCustomerOrganization.parent.__eq__(parent))
                    .page(page_size=page_size)
                )
                for _ in range(page_no):
                    customer = next(customer_obj)

                performance_data["customer_iterate"] = perf_diff_time(
                    start_time, time.time()
                )

                response = []
                for obj in customer:
                    response.append(obj._asdict())

                start_time = time.time()

                customer_serialized = ParentCustomerListSerializer(response, many=True)
                customer_serialized_data = customer_serialized.data

                performance_data["customer_serializer"] = perf_diff_time(
                    start_time, time.time()
                )

                performance_data = {
                    **{"full_view": perf_diff_time(view_start_time, time.time())},
                    **performance_data,
                }

                result_dict = {
                    "performance": performance_data,
                    "customer_count": customer_count,
                    "customer_obj": customer_serialized_data,
                }
                return Response(result_dict, status=200)
            else:
                if request.palantir_user.distributor_id:
                    cust_obj = CustomerOrganizationModel.objects().where(
                        CustomerOrganizationModel.db_code.__eq__(
                            request.palantir_user.distributor_id
                        )
                    )
                else:
                    cust_obj = CustomerOrganizationModel.filter_and_sort(
                        **filter_dict, sort_by=sort_by_field, search=search_query
                    )

                customer_count = cust_obj.count().compute()
                customer_obj = cust_obj.page(page_size=page_size)

                for _ in range(page_no):
                    customer = next(customer_obj)

                response = []
                for obj in customer:
                    obj = obj._asdict()
                    obj.update(
                        {
                            "perm_deactivate": True,
                            "perm_edit": True,
                            "perm_delete": True,
                            "perm_activate": True,
                        }
                    )
                    response.append(obj)

                customer_serialized = CustomerListSerializer(response, many=True)
                customer_serialized_data = customer_serialized.data

                result_dict = {
                    "customer_count": customer_count,
                    "customer_obj": customer_serialized_data,
                }
                return Response(result_dict, status=200)

        except Exception as e:
            # Handle and log the exception appropriately
            result_dict = {
                "customer_count": 0,
                "customer_obj": [],
            }
            result_dict.update({"error": str(e)})
            return Response(result_dict, status=500)

    def create(self, request):
        # POST
        return Response(custom_res_codes["E102"], status=405)

    def retrieve(self, request, pk=None, *args, **kwargs):
        # GET/id/
        try:
            customer_account_code = pk

            if value_exists(customer_account_code):
                customer_obj = CustomerOrganizationModel.get_object(
                    customer_account_code
                )
                customer_serialized = CustomerSerializer(customer_obj._asdict())
                customer_serialized_data = customer_serialized.data
                response = custom_res_codes["S100"]
                response.update({"data": customer_serialized_data})
                return Response(response, status=200)
            return Response({}, status=200)

        except Exception as e:
            # Handle and log the exception appropriately
            return Response({"error": str(e)}, status=500)

    def update(self, request, pk=None, *args, **kwargs):
        # PUT/id/
        try:
            sdk_client = client()
            customer_account_code = pk
            customer_data = request.data
            # TODO: remove code once renaming done at palantir's end
            customer_data["billing_address_1"] = customer_data.pop("billing_address1")
            customer_data["billing_address_2"] = customer_data.pop("billing_address2")
            customer_data["can_access_shop_manuals"] = customer_data.pop("permission1")
            customer_data["shipping_address_1"] = customer_data.pop("shipping_address1")
            customer_data["shipping_address_2"] = customer_data.pop("shipping_address2")
            customer_data["can_order_parts"] = customer_data.pop("permission2")
            customer_data["secondary_phone_number"] = customer_data.pop(
                "secondary_phone_number", "+1 (555) 555-1212"
            )
            customer_data["primary_phone_number"] = customer_data.pop(
                "primary_phone_number", "+1 (555) 555-1212"
            )

            customer_obj = CustomerOrganizationModel.get_object(
                pk=customer_account_code
            )

            customer_data["location_count"] = customer_data.pop(
                "location_count", customer_obj.location_count
            )
            customer_data["user_count"] = customer_data.pop(
                "user_count", customer_obj.user_count
            )
            customer_data["machine_count"] = customer_data.pop(
                "machine_count", customer_obj.machine_count
            )

            # TODO: update this after rework by frontend team
            customer_data.update(
                {
                    "can_order_parts": True
                    if customer_data["can_order_parts"] == "True"
                    else False
                }
            )
            customer_data.update(
                {
                    "can_access_shop_manuals": True
                    if customer_data["can_access_shop_manuals"] == "True"
                    else False
                }
            )

            # customer_data.pop('customer_account_code')
            sdk_client.ontology.actions.my_komatsu_customer_organization_edit(
                my_komatsu_customer_organization=customer_account_code,
                action_config=ActionConfig(mode=ActionMode.APPLY),
                **customer_data
            )
            return Response(customer_data, status=200)

        except Exception as e:
            # Handle and log the exception appropriately
            return Response({"error": str(e)}, status=500)

    def destroy(self, request, pk=None, *args, **kwargs):
        # DELETE/id/
        try:
            sdk_client = client()
            customer_account_code = pk
            customer_data = CustomerOrganizationModel.get_object(customer_account_code)
            customer_serialized = CustomerSerializer(customer_data._asdict())
            customer_data = customer_serialized.data
            # TODO: remove code once renaming done at palantir's end
            customer_data["billing_address_1"] = customer_data.pop("billing_address1")
            customer_data["billing_address_2"] = customer_data.pop("billing_address2")
            customer_data["can_access_shop_manuals"] = customer_data.pop("permission1")
            customer_data["shipping_address_1"] = customer_data.pop("shipping_address1")
            customer_data["shipping_address_2"] = customer_data.pop("shipping_address2")
            customer_data["can_order_parts"] = customer_data.pop("permission2")
            customer_data["secondary_phone_number"] = customer_data.pop(
                "secondary_phone_number", "+1 (555) 555-1212"
            )
            customer_data["primary_phone_number"] = customer_data.pop(
                "primary_phone_number", "+1 (555) 555-1212"
            )
            customer_obj = CustomerOrganizationModel.get_object(
                pk=customer_account_code
            )

            customer_data["location_count"] = customer_data.pop(
                "location_count", customer_obj.location_count
            )
            customer_data["user_count"] = customer_data.pop(
                "user_count", customer_obj.user_count
            )
            customer_data["machine_count"] = customer_data.pop(
                "machine_count", customer_obj.machine_count
            )

            customer_data.update(
                {
                    "can_order_parts": True
                    if customer_data["can_order_parts"] == "True"
                    else False
                }
            )
            customer_data.update(
                {
                    "can_access_shop_manuals": True
                    if customer_data["can_access_shop_manuals"] == "True"
                    else False
                }
            )

            # customer_data.pop('customer_account_code')
            customer_data.update({"soft_delete_flag": settings.DELETE_FLAG})
            sdk_client.ontology.actions.my_komatsu_customer_organization_edit(
                my_komatsu_customer_organization=customer_account_code,
                action_config=ActionConfig(mode=ActionMode.APPLY),
                **customer_data
            )
            return Response(customer_data, status=200)

        except Exception as e:
            # Handle and log the exception appropriately
            return Response({"error": str(e)}, status=500)

    @action(
        methods=["patch"],
        detail=False,
        url_path="update-parent",
        url_name="update_parent",
    )
    def update_parent(self, request, *args, **kwargs):
        try:
            pk_list = request.data.pop("pk_list", None)
            pk_parent = request.data.pop("pk_parent", None)
            sdk_client = client()
            for pk in pk_list:
                cust_obj = CustomerOrganizationModel.get_object(pk)
                customer_data = CustomerSerializer(cust_obj._asdict()).data
                # TODO: remove code once renaming done at palantir's end
                customer_data["billing_address_1"] = customer_data.pop(
                    "billing_address1"
                )
                customer_data["billing_address_2"] = customer_data.pop(
                    "billing_address2"
                )
                customer_data["can_access_shop_manuals"] = customer_data.pop(
                    "permission1"
                )
                customer_data["shipping_address_1"] = customer_data.pop(
                    "shipping_address1"
                )
                customer_data["shipping_address_2"] = customer_data.pop(
                    "shipping_address2"
                )
                customer_data["can_order_parts"] = customer_data.pop("permission2")
                customer_obj = CustomerOrganizationModel.get_object(pk=pk)

                customer_data["location_count"] = customer_data.pop(
                    "location_count", customer_obj.location_count
                )
                customer_data["user_count"] = customer_data.pop(
                    "user_count", customer_obj.user_count
                )
                customer_data["machine_count"] = customer_data.pop(
                    "machine_count", customer_obj.machine_count
                )

                customer_data["secondary_phone_number"] = customer_data.pop(
                    "secondary_phone_number", "+1 (555) 555-1212"
                )
                customer_data["primary_phone_number"] = customer_data.pop(
                    "primary_phone_number", "+1 (555) 555-1212"
                )

                # TODO: update this after rework by frontend team
                customer_data.update(
                    {
                        "can_order_parts": True
                        if customer_data["can_order_parts"] == "True"
                        else False
                    }
                )
                customer_data.update(
                    {
                        "can_access_shop_manuals": True
                        if customer_data["can_access_shop_manuals"] == "True"
                        else False
                    }
                )
                customer_data.update({"parent": pk_parent})
                # TODO: need to update response
                sdk_client.ontology.actions.my_komatsu_customer_organization_edit(
                    my_komatsu_customer_organization=pk,
                    action_config=ActionConfig(mode=ActionMode.APPLY),
                    **customer_data
                )

            response = custom_res_codes["S101"]
            return Response(response, status=200)

        except Exception as e:
            # Handle and log the exception appropriately
            return Response({"error": str(e)}, status=500)

    @action(
        methods=["get"],
        detail=False,
        url_path="orphan-customers",
        url_name="orphan_customers",
    )
    def orphan_customers(self, request, *args, **kwargs):
        try:
            page_no = int(
                self.request.query_params.get("page_num", settings.PAGE_NUM)
            )  # TODO: Will add this in serializer later
            page_size = int(
                self.request.query_params.get("page_size", settings.PAGE_SIZE)
            )
            customer_count = (
                CustomerOrganizationModel.objects()
                .where(
                    MyKomatsuCustomerOrganization.parent.__eq__("")
                    | MyKomatsuCustomerOrganization.parent.is_null()
                )
                .count()
                .compute()
            )
            customer_obj = (
                CustomerOrganizationModel.objects()
                .where(
                    MyKomatsuCustomerOrganization.parent.__eq__("")
                    | MyKomatsuCustomerOrganization.parent.is_null()
                )
                .page(page_size=page_size)
            )

            for _ in range(page_no):
                customer = next(customer_obj)

            response = []
            for obj in customer:
                response.append(obj._asdict())

            customer_serialized = ParentCustomerListSerializer(response, many=True)
            customer_serialized_data = customer_serialized.data

            result_dict = {
                "customer_count": customer_count,
                "customer_obj": customer_serialized_data,
            }
            return Response(result_dict, status=200)

        except Exception as e:
            # Handle and log the exception appropriately
            return Response({"error": str(e)}, status=500)

    # TODO: Temp code to get the deleted entries
    @action(methods=["get"], detail=False, url_path="deleted", url_name="deleted")
    def get_deleted_entries(self, request, *args, **kwargs):
        try:
            deleted_objs = CustomerOrganizationModel.deleted_objects()
            response = []
            for obj in deleted_objs.iterate():
                obj = obj._asdict()
                response.append(obj)
            deleted_serialized = CustomerSerializer(response, many=True)
            response = custom_res_codes["S100"]
            response.update({"data": deleted_serialized.data})
            return Response(response, status=200)

        except Exception as e:
            # Handle and log the exception appropriately
            return Response({"error": str(e)}, status=500)
