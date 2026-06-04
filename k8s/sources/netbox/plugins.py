PLUGINS = [
    "netbox_attachments",
    "netbox_custom_objects",
    "netbox_interface_synchronization",
    "netbox_topology_views",
]

PLUGINS_CONFIG = {
    "netbox_attachments": {
        "applied_scope": "model",
        "scope_filter": [
            "netbox_custom_objects.datasheet",
            "netbox_custom_objects.receipt",
        ],
        "display_default": "right_page",
    }
}
