from extras.scripts import Script
from dcim.models import Device, Module, Rack, Cable
from netbox_custom_objects.models import CustomObjectType


class SyncReceiptsToObjects(Script):
    class Meta:
        name = "Sync Receipts → Object Types"
        description = "Sets the Receipt custom field on Racks, Devices, Modules, and Cables from the Receipt"

    def run(self, data, commit):
        Receipt = CustomObjectType.objects.get(name="receipt").get_model()

        models = [
            (Device, "devices"),
            (Module, "modules"),
            (Rack, "racks"),
            (Cable, "cables"),
        ]

        total = 0
        for model_class, receipt_field in models:
            obj_to_receipt = {}
            for receipt in Receipt.objects.all():
                for obj in getattr(receipt, receipt_field).all():
                    obj_to_receipt[obj.pk] = receipt.pk

            for obj in model_class.objects.all():
                desired_pk = obj_to_receipt.get(obj.pk)
                current_pk = obj.custom_field_data.get("receipt")

                if current_pk == desired_pk:
                    continue

                obj.custom_field_data["receipt"] = desired_pk
                obj.save()

                if desired_pk:
                    self.log_success(
                        f"Linked {model_class.__name__} '{obj}' → Receipt '{obj_to_receipt[obj.pk]}'"
                    )
                else:
                    self.log_warning(
                        f"Cleared Receipt on {model_class.__name__} '{obj}' (no matching Receipt found)"
                    )
                total += 1

        self.log_info(f"Updated {total} object(s) total.")
