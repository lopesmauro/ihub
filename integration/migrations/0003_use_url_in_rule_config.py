from django.db import migrations


def replace_base_url_and_path(apps, schema_editor):
    Rule = apps.get_model("integration", "Rule")

    for rule in Rule.objects.iterator():
        config = rule.config or {}
        base_url = config.pop("base_url", None)
        path = config.pop("path", None)

        if not config.get("url") and isinstance(base_url, str) and isinstance(path, str):
            config["url"] = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

        rule.config = config
        rule.save(update_fields=["config"])


class Migration(migrations.Migration):
    dependencies = [("integration", "0002_centralize_http_config_in_rule")]

    operations = [
        migrations.RunPython(replace_base_url_and_path, migrations.RunPython.noop),
    ]
