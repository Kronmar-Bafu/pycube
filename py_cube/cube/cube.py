import re
from urllib.parse import quote
from rdflib import BNode, Graph, Literal, RDF, URIRef, XSD
from rdflib.collection import Collection
from datetime import datetime, timezone
import pandas as pd
import numbers
import sys
from py_cube.lindas.namespaces import *
from py_cube.lindas.query import query_lindas


class Cube:
    _base_uri: URIRef
    _cube_uri: URIRef
    _cube_dict: dict
    _graph: Graph
    _dataframe: pd.DataFrame
    _shape_dict: dict
    _shape_URI: URIRef

    
    def __init__(self, dataframe: pd.DataFrame, cube_yaml: dict, environment: str, local=False):
        """
        Initialize a Cube object.

        Args:
            dataframe (pd.DataFrame): The Pandas DataFrame representing the cube data.
            cube_yaml (dict): A dictionary containing cube information.
            environment (str): The environment of the cube.
            local (bool): A flag indicating whether the cube is local.

        Returns:
            None
        """
        self._dataframe = dataframe
        self._setup_cube_dict(cube_yaml=cube_yaml)
        self._cube_uri = self._setup_cube_uri(local=local, environment=environment)
        assert self._cube_uri is not None
        self._setup_shape_dicts()
        self._graph = self._setup_graph()
        # self._graph.serialize("example/mock-cube.ttl", format="turtle")

    def __str__(self) -> str:
        """
        Return a string representation of the Cube object.

        This method returns a string representation of the Cube object, including its URI and name.

        Returns:
            str: A string representation of the Cube object.
        """
        how_many_triples_query = (
            "SELECT (COUNT(*) as ?Triples)"
            "WHERE {"
            "    ?s ?p ?o."
            "}"
        )
        how_many_triples = self._graph.query(how_many_triples_query).bindings[0].get("Triples").value
        output = (f"Cube Object <{self._cube_uri}> with name '{self._cube_dict.get('Name').get('en')}'.\n\n"
                  f"{self._dataframe.head()}\n"
                  f"Number of triples in Graph: {how_many_triples}")
        return output

    def prepare_data(self):
        """
        Prepare the cube data by constructing observation URIs and applying mappings.

        This method constructs observation URIs for each row in the dataframe and applies mappings to the dataframe.

        Returns:
            None
        """
        self._construct_obs_uri()
        self._apply_mappings()

    def write_cube(self) -> None:
        """
        Write the cube metadata to the graph.

        This method writes the cube metadata to the graph, including its URI, name, description, publisher, creator, contributor, contact point, version, and date information.

        Returns:
            None
        """
        self._graph.add((self._cube_uri, RDF.type, CUBE.Cube))
        self._graph.add((self._cube_uri, RDF.type, SCHEMA.Dataset))
        self._graph.add((self._cube_uri, RDF.type, DCAT.Dataset))
        self._graph.add((self._cube_uri, RDF.type, VOID.Dataset))

        names = self._cube_dict.get("Name")
        for lan, name in names.items():
            self._graph.add((self._cube_uri, SCHEMA.name, Literal(name, lang=lan)))
            self._graph.add((self._cube_uri, DCT.title, Literal(name, lang=lan)))

        descriptions = self._cube_dict.get("Description")
        for lan, desc in descriptions.items():
            self._graph.add((self._cube_uri, SCHEMA.description, Literal(desc, lang=lan)))
            self._graph.add((self._cube_uri, DCT.description, Literal(desc, lang=lan)))

        publisher = self._cube_dict.get("Publisher")
        for pblshr in publisher:
            self._graph.add((self._cube_uri, SCHEMA.publisher, URIRef(pblshr.get("IRI"))))

        creator = self._cube_dict.get("Creator")
        for crtr in creator:
            self._graph.add((self._cube_uri, SCHEMA.creator, URIRef(crtr.get("IRI"))))

        contributor = self._cube_dict.get("Contributor")
        for cntrbtr in contributor:
            self._graph.add((self._cube_uri, SCHEMA.contributor, URIRef(cntrbtr.get("IRI"))))

        contact_node = self._write_contact_point(self._cube_dict.get("Contact Point"))
        self._graph.add((self._cube_uri, DCAT.contactPoint, contact_node))

        for creator in self._cube_dict.get("Creator", []):
            iri = creator.get('IRI')
            self._graph.add((self._cube_uri, DCT.creator, URIRef(iri)))

        for theme in self._cube_dict.get("Themes", []):
            iri = theme.get('IRI')
            if not iri:
                continue
            self._graph.add((self._cube_uri, DCAT.theme, URIRef(theme['IRI'])))

        version = self._cube_dict.get("Version")
        self._graph.add((self._cube_uri, SCHEMA.version, Literal(version)))

        today = datetime.today().strftime("%Y-%m-%d")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        self._graph.add(
            (self._cube_uri, SCHEMA.dateCreated, Literal(self._cube_dict.get("Date Created"), datatype=XSD.date)))
        self._graph.add((self._cube_uri, SCHEMA.datePublished, Literal(today, datatype=XSD.date)))
        # todo: serialization yields improper format for datetime (with timezone as +02:00 instead of proper UTC)
        self._graph.add((self._cube_uri, SCHEMA.dateModified, Literal(now, datatype=XSD.dateTime)))

        self._graph.add((self._cube_uri, CUBE.observationSet, self._cube_uri + "/ObservationSet"))
        self._graph.add((self._cube_uri, CUBE.observationConstraint, self._shape_URI))

        if self._cube_dict.get("Visualize"):
            self._graph.add((self._cube_uri, SCHEMA.workExample, URIRef("https://ld.admin.ch/application/visualize")))

        if self._cube_dict.get("Work Status"):
            status = self._cube_dict.get("Work Status")
            self._graph.add((self._cube_uri, SCHEMA.creativeWorkStatus,
                             URIRef(f"https://ld.admin.ch/vocabulary/CreativeWorkStatus/{status}")))

        if self._cube_dict.get("Accrual Periodicity"):
            accrual_periodicity_uri = self._get_accrual_periodicity(self._cube_dict.get("Accrual Periodicity"))
            self._graph.add((self._cube_uri, DCT.accrualPeriodicity, accrual_periodicity_uri))

    def get_iri(self) -> URIRef:
        return self._cube_uri

    def _setup_cube_dict(self, cube_yaml: dict) -> None:
        """
        Set up the cube dictionary with the provided YAML data.

        Args:
            cube_yaml (dict): A dictionary containing cube information.

        Returns:
            None
        """
        self._base_uri = URIRef(cube_yaml.get("Base-URI"))
        self._cube_dict = cube_yaml

    def _setup_cube_uri(self, local: bool, environment="TEST") -> URIRef:
        """
        Set up the cube URI by concatenating the base URI and the cube identifier with the version.

        Returns:
            URIRef: The constructed cube URI as a URIRef object.
        """
        cube_uri = self._base_uri + "/".join(["cube", str(self._cube_dict.get("Identifier")), str(self._cube_dict.get("Version"))])
        
        return URIRef(cube_uri)

    def _setup_shape_dicts(self) -> None:
        """Set up shape dictionaries by extracting key dimensions from cube dictionary.
        
            This function initializes the shape dictionary, shape URI, and key dimensions list based on the cube dictionary.
        
            Returns:
                None
        """
        self._shape_dict = self._cube_dict.pop("dimensions")
        self._shape_URI = URIRef(self._cube_uri + "/shape") 
        self._key_dimensions = [dim_name for dim_name, dim in self._shape_dict.items() if dim.get("dimension-type") == "Key Dimension"]

    def _setup_graph(self) -> Graph:
        """Set up the graph by binding namespaces and returning the graph object.
        
        Returns:
            Graph: The graph object with namespaces bound.
        """
        graph = Graph()
        for prefix, nmspc in Namespaces.items():
            graph.bind(prefix=prefix, namespace=nmspc)
        try:
            graph.bind(prefix=self._cube_dict.get("Namespace"), namespace=Namespace(self._base_uri))
        except KeyError:
            print("no Namespace")
            pass
        return graph

    def _construct_obs_uri(self) -> None:
        """Construct observation URIs for each row in the dataframe.
        
        This function constructs observation URIs for each row in the dataframe based on the cube URI and key dimensions.
        
        Returns:
            None
        """
        def make_iri(row):
            return self._cube_uri + "/observation/" + "_".join([quote(str(row[key_dim])) for key_dim in self._key_dimensions])
        self._dataframe['obs-uri'] = self._dataframe.apply(
            make_iri, axis=1
        )
        self._dataframe['obs-uri'] = self._dataframe['obs-uri'].map(URIRef)
        self._dataframe = self._dataframe.set_index("obs-uri")

    def _apply_mappings(self) -> None:
        """Apply mappings to the dataframe based on the specified mapping type.
        
        This method iterates through the dimensions in the shape dictionary and applies mappings to the dataframe if a mapping is defined for the dimension. 
        For dimensions with 'additive' mapping type, it adds a baseline URI in front of the value. For example the entry 1999 will be replaced with 
        https://ld.admin.ch/time/year/1999. 
        For dimensions with 'replace' mapping type, it replaces values in the dataframe column based on the specified replacements.
        Finally, it converts the values in the dataframe column to URIRef objects.
        
        Returns:
            None
        """
        for dim_name, dim_dict in self._shape_dict.items():
            if "mapping" in dim_dict:
                mapping = dim_dict.get("mapping")
                match mapping.get("type"):
                    case "additive":
                        base = mapping.get("base") + "{}"
                        self._dataframe[dim_name] = self._dataframe[dim_name].map(lambda x: base.format(quote(str(x))))
                    case "replace":
                        self._dataframe[dim_name] = self._dataframe[dim_name].map(mapping.get("replacements"))
                    case "regex":
                        pat = re.compile(mapping.get("pattern"))
                        repl = mapping.get("replacement")
                        self._dataframe[dim_name] = self._dataframe[dim_name].map(lambda x: re.sub(pat, repl, x))
                value_type = mapping.get("value-type", 'Shared')
                assert value_type in ['Shared', 'Literal']
                self._dataframe[dim_name] = self._dataframe[dim_name].map(lambda v: URIRef(v) if value_type == "Shared" else Literal(v))

    def _write_contact_point(self, contact_dict: dict) -> BNode|URIRef:
        """Writes a contact point to the graph.
        
            Args:
                contact_dict (dict): A dictionary containing information about the contact point.
                
            Returns:
                BNode or URIRef: The created BNode or URIRef representing the contact point.
        """
        if contact_dict.get("IRI"):
            return URIRef(contact_dict.get("IRI"))
        else:
            contact_node = BNode()
            self._graph.add((contact_node, RDF.type, VCARD.Organization))
            self._graph.add((contact_node, VCARD.hasEmail, Literal(contact_dict.get("E-Mail"), datatype=XSD.string)))
            self._graph.add((contact_node, VCARD.fn, Literal(contact_dict.get("Name"), datatype=XSD.string)))
            return contact_node

    @staticmethod
    def _get_accrual_periodicity(periodicity: str) -> URIRef:
        """Get the URIRef for the given accrual periodicity.
        
        Args:
            periodicity (str): The periodicity of the accrual.
        
        Returns:
            URIRef: The URIRef corresponding to the accrual periodicity.
        """
        base_uri = URIRef("http://publications.europe.eu/resource/authority/frequency/")
        match periodicity:
            case "daily":
                return URIRef(base_uri + "DAILY")
            case "weekly":
                return URIRef(base_uri + "WEEKLY")
            case "monthly":
                return URIRef(base_uri + "MONTHLY")
            case "yearly": 
                return URIRef(base_uri + "ANNUAL")
            case "irregular":
                return URIRef(base_uri + "IRREG")

    def write_observations(self) -> None:
        """Write observations to the cube.

        This function iterates over the rows in the dataframe and adds each row as an observation to the cube.
        It also adds the observation URI to the observation set of the cube.

        Returns:
            None
        """
        self._graph.add((self._cube_uri + "/ObservationSet", RDF.type, CUBE.ObservationSet))
        self._dataframe.apply(self._add_observation, axis=1)

    def serialize(self, filename: str) -> None:
        """Serialize the cube to a file.

        This function serializes the cube to the given file name in turtle format.

        Args:
            filename (str): The name of the file to write the cube to.

        Returns:
            None
        """
        self._graph.serialize(destination=filename, format="turtle", encoding="utf-8")

    def _add_observation(self, obs: pd.DataFrame) -> None:
        """Add an observation to the cube.
        
            Args:
                obs (pd.DataFrame): The observation data to be added.
        
            Returns:
                None
        """
        self._graph.add((self._cube_uri + "/ObservationSet", CUBE.observation, obs.name))
        self._graph.add((obs.name, RDF.type, CUBE.Observation))
        self._graph.add((obs.name, CUBE.observedBy, URIRef(self._cube_dict.get("Creator")[0].get("IRI"))))

        for column in obs.keys():
            path = URIRef(self._base_uri + self._get_shape_column(column).get("path"))
            sanitized_value = self._sanitize_value(obs.get(column))
            self._graph.add((obs.name, URIRef(path), sanitized_value))

    def _get_shape_column(self, column: str):
        c = self._shape_dict.get(column)
        if not c:
            print(self._shape_dict)
            raise ValueError(f'Could not find {column}')
        return c

    def write_shape(self) -> None:
        """Write the shape of the cube to the graph.

            This function writes the shape of the cube to the graph, which is used to validate the cube as well as for
            description of dimension metadata

            Returns:
                None
        """
        self._graph.add((self._shape_URI, RDF.type, CUBE.Constraint))
        self._graph.add((self._shape_URI, SH.closed, Literal("true", datatype=XSD.boolean)))
        for dim, dim_dict in self._shape_dict.items():
            shape = self._write_dimension_shape(dim_dict, self._dataframe[dim])
            self._graph.add((self._shape_URI, SH.property, shape))
    
    def _write_dimension_shape(self, dim_dict: dict, values: pd.Series) -> BNode:
        """Write dimension shape based on the provided dictionary and values.
        
        Args:
            dim_dict (dict): A dictionary containing information about the dimension.
            values (pd.Series): A pandas Series containing values related to the dimension.
        
        Returns:
            BNode: The created dimension node in the graph.
        """
        dim_node = BNode()
        
        self._graph.add((dim_node, SH.minCount, Literal(1)))
        self._graph.add((dim_node, SH.maxCount, Literal(1)))

        for lan, name in dim_dict.get("name").items():
            self._graph.add((dim_node, SCHEMA.name, Literal(name, lang=lan)))
        for lan, desc in dim_dict.get("description").items():
            self._graph.add((dim_node, SCHEMA.description, Literal(desc, lang=lan)))
        
        self._graph.add((dim_node, SH.path, URIRef(self._base_uri + dim_dict.get("path"))))

        match dim_dict.get("dimension-type"):
            case "Key Dimension":
                self._graph.add((dim_node, RDF.type, CUBE.KeyDimension))
                self._graph.add((dim_node, SH.nodeKind, SH.IRI))
                self._graph.add((dim_node, SH.nodeKind, SH.IRI))
                
            case "Measure Dimension":
                self._graph.add((dim_node, RDF.type, CUBE.MeasureDimension))
                self._graph.add((dim_node, SH.nodeKind, SH.Literal))
            
            case "Standard Error":
                relation_node = BNode()
                relation_path = dim_dict.get("relates-to")
                self._graph.add((relation_node, RDF.type, RELATION.StandardError))
                self._graph.add((relation_node, META.relatesTo, URIRef(self._base_uri + relation_path)))
                self._graph.add((dim_node, META.dimensionRelation, relation_node))
                self._graph.add((dim_node, SH.nodeKind, SH.Literal))
            case _ as unrecognized:
                print(f"Dimension Type '{unrecognized}' is not recognized")
        
        match dim_dict.get("scale-type"):
            case "nominal":
                self._graph.add((dim_node, QUDT.scaleType, QUDT.NominalScale))
                self._add_sh_list(dim_node, values)
            case "ordinal":
                self._graph.add((dim_node, QUDT.scaleType, QUDT.OrdinalScale))
                self._add_sh_list(dim_node, values)
            case "interval":
                self._graph.add((dim_node, QUDT.scaleType, QUDT.IntervalScale))
                self._add_min_max(dim_node, values)
            case "ratio":
                self._graph.add((dim_node, QUDT.scaleType, QUDT.RatioScale))
                self._add_min_max(dim_node, values)
            case _ as unrecognized:
                print(f"Scale Type '{unrecognized}' is not recognized")
        
        try:
            match dim_dict.get("unit"):
                case "kilogramm":
                   self._graph.add((dim_node, QUDT.hasUnit, UNIT.KiloGM))
                case "percent":
                   self._graph.add((dim_node, QUDT.hasUnit, UNIT.PERCENT))
        except KeyError:
            pass

        try:
            data_kind = dim_dict.get("data-kind")
            try: 
                match data_kind.get("type"):
                    case "temporal":
                        data_kind_node = BNode()
                        self._graph.add((data_kind_node, RDF.type, TIME.GeneralDateTimeDescription))
                        self._graph.add((data_kind_node, TIME.unitType, TIME.unitYear))
                        self._graph.add((dim_node, META.dataKind, data_kind_node))
                    case "spatial-shape":
                        data_kind_node = BNode()
                        self._graph.add((data_kind_node, RDF.type, SCHEMA.GeoShape))
                        self._graph.add((dim_node, META.dataKind, data_kind_node))
                    case "spatial-coordinates":
                        data_kind_node = BNode()
                        self._graph.add((data_kind_node, RDF.type, SCHEMA.GeoCoordinates))
                        self._graph.add((dim_node, META.dataKind, data_kind_node))
            except AttributeError:
                pass
        except KeyError or AttributeError:
            pass



        return dim_node
    
    def _add_sh_list(self, dim_node: BNode, values: pd.Series):
        """Add a SHACL list of all unique values to the given dimension node.
        
            Args:
                dim_node (BNode): The dimension node to which the SHACL list will be added.
                values (pd.Series): The values to be added to the SHACL list.
        
            Returns:
                None
        """
        list_node = BNode()
        unique_values = values.unique()
        Collection(self._graph, list_node, [URIRef(vl) for vl in unique_values])
        self._graph.add((dim_node, URIRef(SH + "in"), list_node))

    def _add_min_max(self, dim_node: BNode, values: pd.Series):
        """Add minimum and maximum values to the given dimension node.
        
            Args:
                dim_node (BNode): The dimension node to which the values will be added.
                values (pd.Series): The series of values from which minimum and maximum will be calculated.
        
            Todo:
                Case of cube.Undefined should be covered.
        """
        # todo: case of cube.Undefined should be covered
        _min = values.min()
        _max = values.max()
        self._graph.add((dim_node, SH.min, Literal(_min)))
        self._graph.add((dim_node, SH.max, Literal(_max)))

    @staticmethod
    def _sanitize_value(value) -> Literal|URIRef:
        """Sanitize the input value to ensure it is in a valid format.
        
            Args:
                value: The value to be sanitized.
        
            Returns:
                Literal or URIRef: The sanitized value in the form of a Literal or URIRef.
        """
        if isinstance(value, numbers.Number):
            if pd.isna(value):
                return Literal("", datatype=CUBE.Undefined)
            else:
                return Literal(value, datatype=XSD.decimal)
        elif isinstance(value, URIRef):
            return value
        else:
            return Literal(str(value))



