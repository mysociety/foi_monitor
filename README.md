# FOI Monitoring Framework

Static site generator to process FOI compliance statistics. 

This contains files to process UK Cabinet Office related statistics, or those released by the Office of the Scottish Information Commissioner - but is intended as a example of a generalisable framework. 

Live version: https://research.mysociety.org/sites/foi-monitor/

## Setup

There are script-to-rule-them-all scripts that trigger actions in the dockerfile.
Run the following to set up a local instance:

* `script/bootstrap` - Prepare config files from defaults.
* `script/setup` - Bootstrap and remove any existing database.
* `script/build` - Build container and database (will use existing database in `databases\db.sqlite3` if present)
* `script/server` - Load container and run interactive django server.
* `script/bake` - Load container and render site to `bake_dir`. Accepts command line arguments from `[django-sourdough](https://jinhory.xyz/ajparsons/django-sourdough)` e.g. `--only-absent` to only render missing files.

The site can then be viewed at http://127.0.0.1:8000/sites/foi-monitor/

## Updating

This is designed to be simple to update with future releases, or new datasets. 

For each 'jurisdiction', the process expects:

- A file with a list of properties, and parent child relationships.
- A file with a list of authorities, with sector mappings. Sectors themselves should be included as 'Authorities' but without parents.
- A file (or files) that contain the statistics. Roughly expected as a csv with authorities as rows and the properties as columns. 

Examples of these can be seen in the `resources` folder. 

The location of the files, additional processing steps are defined in an adapter. These are stored in `pi_monitor/adapters`. This also includes the current year bounds, which will need to be updated with new information. 

To add a new adapter, add it to the `PI_ADAPTERS` list in `settings.py`.


## Uploading

[No automated process, once baked on server, manually zip and move to correct server.]