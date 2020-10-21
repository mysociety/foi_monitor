# FOI Monitoring Framework

Static site generator to process FOI compliance statistics. 

This contains files to process UK Cabinet Office related statistics, or those released by the Office of the Scottish Information Commissioner - but is intended as a example of a generalisable framework. 

Live version: https://research.mysociety.org/sites/foi-monitor/

## Setup

Set the `BUILD_PATH` (where the completed site will be rendered to, not necessary for local work) in `config.py`

Run the following to set up a local instance:

```
pipenv install
pipenv shell
invoke migrate
invoke populate
```

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

To render to the specified location use `python manage.py bake`. If not running in a vagrant, this will require a path to a CHROME_DRIVER in `config.py`.

Upload involves creating a zip and uploading via scp. Look at `tasks.py` for more details, but after setting up ssh details in `conf.ssh_creds.py` (usually reference to location of key). 

`invoke bakezip`
`invoke uploadzip`