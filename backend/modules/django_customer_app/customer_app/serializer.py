from rest_framework import serializers


class CustomerSerializer(serializers.Serializer):
    """
    Serializer for individual customer objects.
    """

    distributor = serializers.CharField()
    customer_name = serializers.CharField(source="customerName")
    billing_country = serializers.CharField(source="billingCountry")
    billing_state = serializers.CharField(source="billingState")
    status = serializers.BooleanField()
    shipping_country = serializers.CharField(source="shippingCountry")
    billing_city = serializers.CharField(source="billingCity")
    shipping_same_as_billing = serializers.CharField(source="shippingSameAsBilling")
    shipping_state = serializers.CharField(source="shippingState")
    industry = serializers.CharField()
    parent = serializers.CharField()
    shipping_city = serializers.CharField(source="shippingCity")
    soft_delete_flag = serializers.CharField(source="softDeleteFlag")
    billing_address1 = serializers.CharField(source="billingAddress1")
    billing_address2 = serializers.CharField(source="billingAddress2")
    permission1 = serializers.CharField(source="canAccessShopManuals")
    primary_branch = serializers.CharField(source="primaryBranch")
    billing_zip = serializers.CharField(source="billingZip")
    shipping_zip = serializers.CharField(source="shippingZip")
    shipping_address1 = serializers.CharField(source="shippingAddress1")
    customer_account_code = serializers.CharField(source="customerAccountCode")
    shipping_address2 = serializers.CharField(source="shippingAddress2")
    display_name = serializers.CharField(source="displayName")
    permission2 = serializers.CharField(source="canOrderParts")
    db_code = serializers.CharField(source="dbCode")
    secondary_phone_number = serializers.CharField(
        source="secondaryPhoneNumber", default="+1 (555) 555-1212"
    )
    primary_phone_number = serializers.CharField(
        source="primaryPhoneNumber", default="+1 (555) 555-1212"
    )
    location_count = serializers.IntegerField(source="locationCount")
    user_count = serializers.IntegerField(source="userCount")
    machine_count = serializers.IntegerField(source="machineCount")


class CustomerListSerializer(serializers.Serializer):
    """
    Serializer for customer objects used in lists.
    """

    customer_name = serializers.CharField(source="customerName")
    customer_account_code = serializers.CharField(source="customerAccountCode")
    industry = serializers.CharField()
    parent = serializers.CharField()
    distributor = serializers.CharField()
    db_code = serializers.CharField(source="dbCode")
    status = serializers.BooleanField()
    location_count = serializers.IntegerField(source="locationCount")
    user_count = serializers.IntegerField(source="userCount")
    machine_count = serializers.IntegerField(source="machineCount")
    display_name = serializers.CharField(source="displayName")
    shipping_address = serializers.SerializerMethodField()
    perm_deactivate = serializers.BooleanField(default=True)
    perm_edit = serializers.BooleanField(default=True)
    perm_delete = serializers.BooleanField(default=True)
    perm_activate = serializers.BooleanField(default=True)
    billing_address = serializers.SerializerMethodField()

    def get_billing_address(self, obj):
        """
        Get formatted billing address.
        """
        address_parts = [
            obj.get("billingAddress1", ""),
            obj.get("billingAddress2", ""),
            obj.get("billingCity", ""),
            obj.get("billingState", ""),
            obj.get("billingCountry", ""),
            obj.get("billingZip", ""),
        ]
        result = ", ".join(filter(None, address_parts))
        return result

    def get_shipping_address(self, obj):
        """
        Get formatted shipping address.
        """
        address_parts = [
            obj.get("shippingAddress1", ""),
            obj.get("shippingAddress2", ""),
            obj.get("shippingCity", ""),
            obj.get("shippingState", ""),
            obj.get("shippingCountry", ""),
            obj.get("shippingZip", ""),
        ]
        result = ", ".join(filter(None, address_parts))
        return result


class ParentCustomerListSerializer(serializers.Serializer):
    """
    Serializer for parent customer objects.
    """

    customer_name = serializers.CharField(source="customerName")
    customer_account_code = serializers.CharField(source="customerAccountCode")
    distributor = serializers.CharField()
    db_code = serializers.CharField(source="dbCode")
    perm_deactivate = serializers.BooleanField(default=True)
    perm_edit = serializers.BooleanField(default=True)
    perm_delete = serializers.BooleanField(default=True)
    perm_activate = serializers.BooleanField(default=True)
