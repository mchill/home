from extras.scripts import Script
from dcim.models import DeviceType, ModuleType, RackType
from netbox_custom_objects.models import CustomObjectType


class SyncDatasheetsToObjects(Script):
    class Meta:
        name = "Sync Datasheets → Object Types"
        description = "Sets the Datasheet custom field on RackTypes, Device Types, and Module Types from the Datasheet"

    def run(self, data, commit):
        Datasheet = CustomObjectType.objects.get(name="datasheet").get_model()

        models = [
            (DeviceType, "device_type"),
            (ModuleType, "module_type"),
            (RackType, "rack_type"),
        ]

        total = 0
        for model_class, datasheet_field in models:
            for obj in model_class.objects.all():
                datasheet = Datasheet.objects.filter(**{datasheet_field: obj}).first()
                desired_pk = datasheet.pk if datasheet else None
                current_pk = obj.custom_field_data.get("datasheet")

                if current_pk == desired_pk:
                    continue

                obj.custom_field_data["datasheet"] = desired_pk
                obj.save()

                if desired_pk:
                    self.log_success(
                        f"Linked {model_class.__name__} '{obj}' → Datasheet '{datasheet}'"
                    )
                else:
                    self.log_warning(
                        f"Cleared Datasheet on {model_class.__name__} '{obj}' (no matching Datasheet found)"
                    )
                total += 1

        self.log_info(f"Updated {total} object(s) total.")
