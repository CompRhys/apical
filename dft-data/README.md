## Data for paper "Predicting lithium iron oxysulphides for battery cathodes"

Content of the repository

- `lco-apical.aiida` is an AiiDA export file containing all calculation performed and reported in paper with their full provenance. This file can be imported into an AiiDA instance (`aiida-core >= 1.6.3`). Raw data may also be access by simply unzipping the file.


## Importing data into a new AiiDA Database

The provenance data stored in the `lco-apical.aiida` can be imported into a AiiDA database and allow the analysis in the `notebooks` folder to be reproduced.
A few dependencies needs to be installed:

- `aiida-core>=1.6.3` is the mean package of the AiiDA framework. 
- `aiida-castep` - the interface to CASTEP.
- `ase` is needed analysis. `ase==3.21` was used this project, but other compatible version should work as well.
- additional requires in the `requirements.txt`.

A few more steps are needed to step up a new AiiDA profile before importing the archive. Please follow the installation instructions on the [offical documentation](https://aiida.readthedocs.io/).

The magic "%aiida" can be enabled by a file `aiida_magic_register.py` in `<home_folder>/.ipython/profile_default/startup`:


```python
if __name__ == '__main__':

    try:
        import aiida
        del aiida
    except ImportError:
        # AiiDA is not installed in this Python environment
        pass
    else:
        from aiida.tools.ipython.ipython_magics import register_ipython_extension
        register_ipython_extension()
```

Note that you may want to run `ipython` once so the profile folers are created. If not, just create them manually.

Once everything is in place, the following commands will import all data:

```base
verdi archive import -G lco-apical -- lco-apical.aiida
```

As each calculation/workflow is identified based on a unique ID (uuid), the analysis code in the notebook can be reused. 
