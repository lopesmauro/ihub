from django.db import migrations


def copy_connector_config_to_rules(apps, schema_editor):
    Rule = apps.get_model("integration", "Rule")

    for rule in Rule.objects.select_related("connector").iterator():
        connector_config = rule.connector.config or {}
        rule_config = rule.config or {}
        rule.config = {**connector_config, **rule_config}
        rule.save(update_fields=["config"])


class Migration(migrations.Migration):
    dependencies = [("integration", "0001_initial")]

    operations = [
        migrations.RunPython(copy_connector_config_to_rules, migrations.RunPython.noop),
        migrations.RemoveField(model_name="delivery", name="connector"),
        migrations.RemoveField(model_name="rule", name="connector"),
        migrations.DeleteModel(name="Connector"),
    ]
