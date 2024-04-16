from modules.django_komatsu_idm.komatsu_idm.main import sdk_client as client
from dev_mykomatsu_sdk.ontology.objects import MyKomatsuCustomerOrganization
from django.conf import settings


class FilterTypes:
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    IS_ANY_OF = "is_any_of"
    EQUALS = "equals"


class InvalidSortByAttribute(Exception):
    """
    Custom exception class for invalid sort_by attribute.
    """

    def __init__(self):
        self.message = "Invalid sort_by value"
        super().__init__(self.message)


class CustomerOrganizationModel(MyKomatsuCustomerOrganization):
    FILTER_KEYS = [
        "customer_name",
        "customer_account_code",
        "industry",
        "parent",
        "distributor",
        "primary_branch",
        "location_count",
        "user_count",
        "machine_count",
        "status",
    ]

    @classmethod
    def objects(cls):
        try:
            sdk_client = client()
            return sdk_client.ontology.objects.MyKomatsuCustomerOrganization.where(
                ~MyKomatsuCustomerOrganization.soft_delete_flag.__eq__(
                    settings.DELETE_FLAG
                )
                # & MyKomatsuCustomerOrganization.industry.contains_any_term(['Mining'])
            )
        except Exception as e:
            # Handle and log the exception appropriately
            raise e

    @classmethod
    def deleted_objects(cls):
        try:
            sdk_client = client()
            return sdk_client.ontology.objects.MyKomatsuCustomerOrganization.where(
                MyKomatsuCustomerOrganization.soft_delete_flag.__eq__(
                    settings.DELETE_FLAG
                )
            )
        except Exception as e:
            # Handle and log the exception appropriately
            raise e

    @classmethod
    def get_object(cls, pk):
        try:
            return (
                cls.objects()
                .where(MyKomatsuCustomerOrganization.customer_account_code.__eq__(pk))
                .take(1)[0]
            )
        except IndexError:
            # Handle if the object with the specified primary key is not found
            raise ValueError(f"No object found with primary key: {pk}")
        except Exception as e:
            # Handle and log the exception appropriately
            raise e

    @classmethod
    def filter_and_sort(cls, **kwargs):
        """
        Filters and sorts MyKomatsuCustomerOrganization objects based on provided criteria.
        """
        try:
            sort_by = kwargs.pop("sort_by", None)
            search_query = kwargs.pop("search", None)

            data = cls.objects()

            for k, v in kwargs.items():
                filter_type, value = v
                if filter_type == FilterTypes.CONTAINS:
                    filtered_data = data.where(
                        MyKomatsuCustomerOrganization.customer_name.contains_any_terms(
                            [value]
                        )
                    )
                elif filter_type == FilterTypes.STARTS_WITH:
                    filtered_data = data.where(getattr(cls, k).starts_with([value]))
                # TODO: implement once provided by Palantir
                # elif filter_type == FilterTypes.ENDS_WITH:
                #     filtered_data = data.where(getattr(cls, k).__eq__(v))
                elif filter_type == FilterTypes.IS_EMPTY:
                    filtered_data = data.where(getattr(cls, k).is_null())
                elif filter_type == FilterTypes.IS_NOT_EMPTY:
                    filtered_data = data.where(~getattr(cls, k).is_null())
                elif filter_type == FilterTypes.IS_ANY_OF:
                    filtered_data = data.where(
                        getattr(cls, k).contains_any_term(eval(value))
                    )
                elif filter_type == FilterTypes.EQUALS:
                    filtered_data = data.where(getattr(cls, k).__eq__(value))

                if filtered_data.count().compute() > 0:
                    data = filtered_data
                else:
                    return filtered_data

            filtered_res = data

            skip_search = True if filtered_res.count().compute() == 0 else False
            if search_query and not skip_search:
                for field in cls.SEARCH_FIELDS:
                    data = filtered_res.where(
                        getattr(cls, field).starts_with([search_query])
                    )
                    if data.count().compute() > 0:
                        filtered_res = data

            skip_sort_by = True if filtered_res.count().compute() == 0 else False
            if sort_by and not skip_sort_by:
                is_asc, sort_by = (
                    (False, sort_by[1:]) if sort_by[0] == "-" else (True, sort_by)
                )
                valid_attributes = [
                    attr
                    for attr in dir(cls)
                    if not callable(getattr(cls, attr)) and not attr.startswith("__")
                ]

                if sort_by in valid_attributes:
                    filtered_res = filtered_res.order_by(
                        getattr(cls, sort_by).asc()
                        if is_asc
                        else getattr(cls, sort_by).desc()
                    )
                else:
                    raise InvalidSortByAttribute

            return filtered_res

        except Exception as e:
            # Handle exceptions
            raise e
