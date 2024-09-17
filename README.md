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


## Functionality
To avoid the feeling of a black box, our philosophy is to make the construction of cubes modular. The process will take place in multiple steps, outlined below.

1. **Initialization** 
```
cube = pycube.Cube(dataframe: pd.Dataframe, cube_yaml: dict, shape_yaml: dict)
```
This step sets some need background information about the cube up. 

2. **Mapping**
```
cube.apply_mapping()
```
Applies the mappings as described in the shape yaml. 

3. **Write `cube:Cube`**
```
cube.write_cube()
```
Writes the `cube:Cube`.

4. **Write `cube:Observation`**
```
cube.write_observations()
```
Writes the `cube:Observation`s and the `cube:ObservationSet`. The URI for the observations are written as `<cube_URI/observations/[list_of_key_dimensions]>`. This should avoid the possibilities of conflicts in their uniqueness.

5. **Write `cube:ObersvationConstraint`**
```
cube.write_shape()
```
Writes the `cube:ObservationConstraint`. 

### The full work-flow
```
# Write the cube
cube = pycube.Cube(dataframe: pd.DataFrame, cube_yaml: dict, shape_yaml: dict)
cube.apply_mapping()
cube.write_cube()
cube.write_observations()
cube.write_shape()

# Upload the cube
cube.upload(endpoint: str, named_graph: str)
```
