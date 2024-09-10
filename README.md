# py-cube

## About

`py-cube` is a package to build and publish cubes as defined by [cube.link](https://cube.link), describing a schema to describe structured data from tables in [RDF](https://www.w3.org/RDF/). It allows for an alternative to the [Cube-Creator](https://cube-creator.lindas.admin.ch). Currently this project is heavily linked to the [LINDAS](lindas.admin.ch) the Swiss Federal Linked Data Service.

For further information, please refer to our [Wiki](https://github.com/Kronmar-Bafu/cubelink/wiki)

## Installation

There are two ways to install this package, locally or through the [Python Package Index (PyPI)](https://pypi.org). 

### Locally
Clone this repository and `cd` into the directory. You can now install this package locally on your machine - we advise to use a virtual environment to avoid conflicts with other projects. Additionally, install all dependencies as described in `requirements.txt`

```
pip install -e .
pip install -r requirements.txt
```

### Published Version
**NOT yet implemented** Once Published, you'll be able to intall this package through pip without cloning the repository.

```
pip install py-cube
```
## Contributing and Suggestions
If you wish to contribute to this project, feel free to clone this repository and open a pull request to be reviewed and merged.

Alternatively feel free to open an issue with a suggestion on what we could implement. We laid out a rough road map for the features ahead on our [Timetable](https://github.com/Kronmar-Bafu/cubelink/wiki/Timetable)


<<<<<<< HEAD
Version | Features
------|---------------
0.1.0 | Build cubes
0.1.1 | Read me + "Wiki"
0.1.2 | Fix Getter
0.2.0 | Validierung mit pyShacl, Upload 
0.2.1 | Fix der Issues die von der Validierung kommen werden (units?)
0.3.0 | Smart Validierung (gibt es die Cubes schon? Sonstige URIs)
0.4.0 | Lindas -> yaml?
1.0.0 | SharedDimension Mapping: Pre-Processing, mini API (Look-Up, gibt es eine solche URI, die ich benötige?), Replaces Mapping in Dimension-yaml
1.1.0 | SharedDimension in Python?
2.0.0 | Smart Upload (Diff-Upload?)
=======
>>>>>>> 3fcc0149b5bab0ae3af17ad6c0b4bcd470ca5c0d
