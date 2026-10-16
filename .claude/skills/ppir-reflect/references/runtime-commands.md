# PPIR Runtime Command Patterns

Prefer repository runtime scripts when they exist. If the script does not exist yet, produce the specified artifact text and explicitly mark the command as pending implementation.

Common command patterns:

```bash
python runtime/audit.py --scope all
python runtime/audit.py --scope app:shop-admin
python runtime/graph_query.py deps SHOP.SCREEN.orders.list
python runtime/graph_query.py reverse SHOP.API.orders.list
python runtime/adopt.py --mode propose --scope app:shop-admin --source-type verbal --text "..."
python runtime/merge.py PROP.example --staging
python runtime/reflect.py SHOP.API.orders.list
python runtime/publish.py --target SHOP.SCREEN.orders.list --role fe
python runtime/context.py --target SHOP.SCREEN.orders.list --task screen_update
python runtime/explain.py "why is warehouse available read only?"
python runtime/observe_impl.py --source openapi --file sources/openapi/example.yaml --scope app:shop-admin
```

Never invent a successful script execution. If runtime scripts are unavailable, state that this is a design-time artifact and output the exact files or YAML blocks the runtime should create.
