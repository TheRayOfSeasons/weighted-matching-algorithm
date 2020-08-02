class Vertex:
    """
    This represents an item.

    - Constructor Parameters

        :param item: :type any:
            This is the data which the vertex will represent.
    """

    def __init__(self, item, *args, **kwargs):
        self.neigbors = []
        self.edges = []
        self.item = item

    def __eq__(self, other):
        try:
            other.item
        except AttributeError:
            return False
        return self.item == other.item

    def __lt__(self, other):
        try:
            other.item
        except AttributeError:
            return False
        return self.item < other.item

    def __repr__(self):
        return '<Vertex ({})>'.format(self.item)

    @property
    def heaviest_edge(self):
        """
        Returns the edge connected to the vertex
        with the largest weight.
        """
        try:
            edge = max(self.edges)
        except ValueError:
            edge = None
        return edge

    def add_neighbor(self, other_vertex, edge):
        """
        This sets another vertex as a neighbor of this vertex.

        - Parameters

            :param other_vertex: :type Vertex:
                The other vertex to connect.
            :param edge: :type edge:
                The reference to the edge that connects the two vertices.
        """
        self.neigbors.append(other_vertex)
        self.edges.append(edge)


class Edge:
    """
    Represents a connection between edges.

    - Constructor Parameters

        :param vertex_1: :type Vertex:
            The first vertex of the edge.
        :param vertex_2: :type Vertex:
            The second vertex of the edge.
        :param weight: :type int:
            The initial weight of the edge. Defaults as 1.
    """

    def __init__(self, vertex_1, vertex_2, weight=1, *args, **kwargs):
        self.vertex_1 = vertex_1
        self.vertex_2 = vertex_2
        self.weight = 1
        vertex_1.add_neighbor(vertex_2, self)
        vertex_2.add_neighbor(vertex_1, self)

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        parallel, reverse = _get_parallels(other)
        return self.weight == other.weight and (parallel or reverse)

    def __lt__(self, other):
        if not isinstance(other, Edge):
            return False
        parallel, reverse = _get_parallels(other)
        return self.weight < other.weight and (parallel or reverse)

    def __repr__(self):
        return '<Edge ({}) | ({})>'.format(
            self.vertex_1.item, self.vertex_2.item)

    def get_vertices(self, reverse=False):
        """
        Returns the vertices in the edge as a tuple.

        - Parameters

            :param reverse: :type boolean:
                Defaults as False. If True, returns the 2nd vertex
                before the first.
        """
        return [(vertex_1, vertex_2), (vertex_2, vertex_1)][reverse]

    def _get_parallels(self, other):
        """
        A private helper function for getting reversed
        and non reversed comparisons of vertices.
        """
        parallel = (
            self.vertex_1 == other.vertex_1
            and self.vertex_2 == other.vertex_2
        )
        reverse = (
            self.vertex_1 == other.vertex_2
            and self.vertex_2 == other.vertex_1
        )
        return parallel, reverse

    def add_weight(self, weight=1):
        """
        Add weight to the edge.

        - Parameters

            :param weight: :type int:
                The value to add to the weight.
        """
        self.weight += weight


class MatchingGraph:
    """
    The graph proper. This holds the core methods for the matching.

    - Constructor Parameters

        :param x_set: :type list:
            The values received by this parameter are used as the items
            for the first set.
        :param y_set: :type list:
            The values received by this parameter are used as the items
            for the second set.
        :param x_vertex_class: :type type:
            The type of vertex that will be used to initialize the items
            from the first set as vertices. Defaults as Vertex.
        :param y_vertex_class: :type type:
            The type of vertex that will be used to initialize the items
            from the second set as vertices. Defaults as Vertex.
        :param edge_class: :type type:
            The type of edge that will be used to initialize the edge
            instances for the matching. Defaults as Edge.
        :param x_extra_vertex_initalization_values: :type dict:
            Defaults as an empty dictionary. Should the vertex
            class that will be used for the initialization of the
            first set need to accept additional constructor
            arguments, then they may be placed here. Preferably,
            the item of the vertex must be able to identify
            the key of the value.
        :param y_extra_vertex_initalization_values: :type dict:
            Defaults as an empty dictionary. Should the vertex
            class that will be used for the initialization of the
            second set need to accept additional constructor
            arguments, then they may be placed here. Preferably,
            the item of the vertex must be able to identify
            the key of the value.
        :param x_kwarg_extractor: :type method:
            Defaults as None. This is responsible for extracting
            kwargs from the x_extra_vertex_initalization_values.
            The method accepted here must be able to accept
            at least 2 values, which are a vertex's item, and the
            values from the intialization values for the X set.
        :param y_kwarg_extractor: :type method:
            Defaults as None. This is responsible for extracting
            kwargs from the y_extra_vertex_initalization_values.
            The method accepted here must be able to accept
            at least 2 values, which are a vertex's item, and the
            values from the intialization values for the Y set.
        according_to_x_set:
            Defaults as True. This only determines from which set
            should the matching comparison base from. Regardless
            of this setting, the same value will be returned because
            this only provides a minor change in the algorithm flow
            when it comes to optimally matching the data sets.
    """

    def __init__(
            self, x_set, y_set,
            x_set_vertex_class=Vertex,
            y_set_vertex_class=Vertex,
            edge_class=Edge,
            x_extra_vertex_initalization_values={},
            y_extra_vertex_initalization_values={},
            x_kwarg_extractor=None,
            y_kwarg_extractor=None,
            according_to_x_set=True,
            *args, **kwargs):
        self.x_set = x_set
        self.y_set = y_set
        self.x_set_vertex_class = x_set_vertex_class
        self.y_set_vertex_class = y_set_vertex_class
        self.edge_class = edge_class
        self.edges = []
        self.matches = []
        self.according_to_x_set = according_to_x_set
        self.vertex_attr_a = ['vertex_1', 'vertex_2'][according_to_x_set]
        self.vertex_attr_b = ['vertex_2', 'vertex_1'][according_to_x_set]
        intialization_args = (
            x_extra_vertex_initalization_values,
            y_extra_vertex_initalization_values,
            x_kwarg_extractor,
            y_kwarg_extractor
        )

        # The initialization lifecycle.
        self._initialize_vertices(*intialization_args)
        self._build_edges(*args, **kwargs)
        self.match(*args, **kwargs)

    @property
    def unique_weights(self):
        """
        Returns all the unique weights of all edges as a set.
        """
        return set([edge.weight for edge in self.edges])

    @property
    def matched_x_vertices(self):
        """
        Returns all the vertices from the x set that have been matched.
        """
        return [edge.vertex_1 for edge in self.matches]

    @property
    def matched_x_vertices(self):
        """
        Returns all the vertices from the y set that have been matched.
        """
        return [edge.vertex_2 for edge in self.matches]

    @property
    def unmatched_x_vertices(self):
        """
        Returns all the vertices from the x set that were not matched.
        """
        return [
            vertex for vertex in self.x_vertices
            if vertex not in self.matched_x_vertices
        ]

    @property
    def unmatched_y_vertices(self):
        """
        Returns all the vertices from the y set that were not matched.
        """
        return [
            vertex for vertex in self.y_vertices
            if vertex not in self.matched_y_vertices
        ]

    def _initialize_vertices(
            self,
            x_extra_vertex_initalization_values={},
            y_extra_vertex_initalization_values={},
            x_kwarg_extractor=None,
            y_kwarg_extractor=None):
        """
        Initialize vertices based on values received from constructor.
        """
        vertex_sets = ([],[])
        vertex_data = [
            (
                self.x_set,
                self.x_set_vertex_class,
                x_extra_vertex_initalization_values,
                x_kwarg_extractor
            ),
            (
                self.y_set,
                self.y_set_vertex_class,
                y_extra_vertex_initalization_values,
                y_kwarg_extractor
            )
        ]
        for index, data in enumerate(vertex_data):
            item_set, vertex_class, extra_values, extract = data
            for item in item_set:
                if extract:
                    extras = extract(item, extra_values)
                else:
                    extras = {}
                vertex_sets[index].append(vertex_class(item, **extras))
        self.x_vertices, self.y_vertices = vertex_sets

    def get_x_set_condition_values(self, x_vertex, *args, **kwargs):
        """
        An abstract method for setting up the values from the x_vertex
        that is necessary to evaluate a match.

        - Parameters

            :param x_vertex: :type Vertex:
                A vertex from the x_set.

        - Returns

            By default, this returns a dictionary in this structure:
                {'value': <the vertex>}

            This is always expected to return a dictionary.
        """
        return {'value': x_vertex}

    def get_y_set_condition_values(self, y_vertex, *args, **kwargs):
        """
        An abstract method for setting up the values from the y_vertex
        that is necessary to evaluate a match.

        - Parameters

            :param y_vertex: :type Vertex:
                A vertex from the y_set.

        - Returns

            By default, this returns a dictionary in this structure:
                {'value': <the vertex>}

            This is always expected to return a dictionary.
        """
        return {'value': y_vertex}

    def get_matching_arguments(self, x_vertex, y_vertex, *args, **kwargs):
        """
        An abstract method that collects all the values necessary
        to evaluate two vertices as a match.

        - Parameters

            :param x_vertex: :type Vertex:
                A vertex from the x_set.
            :param y_vertex: :type Vertex:
                A vertex from the y_set.

        - Returns

            This returns the results from get_x_set_condition_values and
            get_y_set_condition_values as a tupled pair.
        """
        x_conditions = (
            self.get_x_set_condition_values(x_vertex, *args, **kwargs))
        y_conditions = (
            self.get_y_set_condition_values(y_vertex, *args, **kwargs))
        return x_conditions, y_conditions

    def _check_match(self, x_vertex, y_vertex, *args, **kwargs):
        """
        A private method for checking if two vertices are a match.

        - Parameters:

            :param x_vertex: :type Vertex:
                A vertex from the x_set.
            :param y_vertex: :type Vertex:
                A vertex from the y_set.

        - Returns

            This returns
        """
        x_conditions, y_conditions = (
            self.get_matching_arguments(x_vertex, y_vertex, *args, **kwargs))
        conditions = self.get_conditions(x_conditions, y_conditions)
        is_match = self.assess_match(conditions, *args, **kwargs)
        compatibility = self.assess_compatibility(conditions, *args, **kwargs)
        return is_match, compatibility

    def get_conditions(self, x_conditions, y_conditions, *args, **kwargs):
        """
        An abstract method for setting up all the conditions
        needed to prove if a pair of vertices are a match.

        - Parameters

            :param x_conditions: :type dict:
                A dictionary of values from a vertex from the x_set
                that is necessary to compare it with a vertex from the
                y_set.
            :param y_conditions: :type dict:
                A dictionary of values from a vertex from the y_set
                that is necessary to compare it with a vertex from the
                x_set.

        - Returns

            This returns the evaluation of all conditions as
            a tuple of boolean values.
        """
        return (x_conditions['value'] == y_conditions['value'],)

    def assess_match(self, conditions, *args, **kwargs):
        """
        An abstract method for assessing a pair of vertices as
        a valid match.

        - Parameters

            :param condition: :type tuple:
                A tuple of boolean values.
        """
        return any(conditions)

    def assess_compatibility(self, conditions, *args, **kwargs):
        """
        An abstract method for counting the
        compatibility of a possible match.

        - Parameters

            :param condition: :type tuple:
                A tuple of boolean values.
        """
        return len([condition for condition in conditions if condition])

    def _build_edges(self, *args, **kwargs):
        """
        This edges all possible matches between the x_set and the y_set.
        """
        adherence = self.according_to_x_set
        x_vertices, y_vertices = self.x_vertices, self.y_vertices
        a_vertices, b_vertices = [
            (y_vertices, x_vertices), (x_vertices, y_vertices)][adherence]
        for vertex_a in a_vertices:
            for vertex_b in b_vertices:
                vertices = [
                    (vertex_b, vertex_a), (vertex_a, vertex_b)][adherence]
                is_match, compatibility = (
                    self._check_match(*vertices, *args, **kwargs))
                if is_match:
                    edge_args = vertices + (compatibility,)
                    self.edges.append(self.edge_class(*edge_args))

    def evaluate_match(self, vertex, *args, **kwargs):
        """
        An abstract method for assesing an edge as an optimal match.
        """
        optimal_match = vertex.heaviest_edge
        if optimal_match:
            self.matches.append(optimal_match)

    def match(self, *args, **kwargs):
        """
        An abstract method to assess the optimal matchings.
        """
        adherence = self.according_to_x_set
        vertices = [self.x_vertices, self.y_vertices][adherence]
        import pdb; pdb.set_trace()
        for vertex in vertices:
            self.evaluate_match(vertex, *args, **kwargs)
        return self.matches
