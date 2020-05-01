from collections import OrderedDict
import contextlib
import copy
from difflib import SequenceMatcher
import operator
import os
import re
import time

import h5py
import jinja2
import netCDF4
import numpy as np
import pyparsing
import rdflib
import rdflib.collection
import requests
import six

# try:
#     #import terra.datetime
#     from terra import datetime
#     terra_imp = True
# except ImportError:
#     terra_imp = False

from bald import datetime
terra_imp = True
import bald.validation as bv

__version__ = '0.3'


def _graph_html():
    return('''<html>
<head>
<title>agraph</title>
<meta charset="utf-8"/>
<link rel="stylesheet" type="text/css"
href="https://rawgit.com/clientIO/joint/master/dist/joint.min.css" />

</head>
<body>

<div id="paper"></div>
<script
src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/jquery.js"></script>
<script
src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/3.10.1/lodash.js"></script>
<script
src="https://cdnjs.cloudflare.com/ajax/libs/backbone.js/1.3.3/backbone.js"></script>
<script
src="https://rawgit.com/clientIO/joint/master/dist/joint.min.js"></script>
<script src="http://rawgit.com/clientIO/joint/master/dist/joint.layout.DirectedGraph.js"></script>
<script src="https://rawgit.com/cpettitt/graphlib/v2.1.1/dist/graphlib.min.js"></script>
<script src="https://rawgit.com/cpettitt/dagre/v0.7.4/dist/dagre.min.js"></script>

<script type="text/javascript">

{{ script }}

</script>
</body>
</html>
''')

def _network_js():
    return('''
var graph = new joint.dia.Graph;

var paper = new joint.dia.Paper({
     el: $('#paper'),
     width: 2400,
     height: 1350,
     gridSize: 1,
     model: graph
});

var instance_list = [];

LinkedClass = joint.shapes.uml.Class.extend({


    markup: [
        '<g class="rotatable">',
        '<g class="scalable">',
        '<rect class="uml-class-name-rect"/><rect class="uml-class-attrs-rect"/>',
        '</g>',
        '<text class="uml-class-name-text"/><text class="uml-class-attrs-text"/>',
        '</g>'
        ].join(''),

    defaults: _.defaultsDeep({

        type: 'uml.Class',

        attrs: {
            rect: { 'width': 200 },

            '.uml-class-name-rect': { 'stroke': 'black', 'stroke-width': 2, 'fill': '#3498db' },
            '.uml-class-attrs-rect': { 'stroke': 'black', 'stroke-width': 2, 'fill': '#2980b9' },

            '.uml-class-name-text': {
                'ref': '.uml-class-name-rect', 'ref-y': .5, 'ref-x': .5, 'text-anchor': 'middle', 'y-alignment': 'middle', 'font-weight': 'bold',
                'fill': 'black', 'font-size': 12, 'font-family': 'Times New Roman'
            },
            '.uml-class-attrs-text': {
                'ref': '.uml-class-attrs-rect', 'ref-y': 5, 'ref-x': 0.99, 'text-anchor': 'end',
                'fill': 'black', 'font-size': 12, 'font-family': 'Times New Roman'
            }
        },

        name: [],
        attributes: [],

    }, joint.shapes.basic.Generic.prototype.defaults),

    updateRectangles: function() {

        var attrs = this.get('attrs');

        var rects = [
            { type: 'name', text: this.getClassName() },
            { type: 'attrs', text: this.get('attributes') },
        ];

        var offsetY = 0;

        _.each(rects, function(rect) {

            var lines = _.isArray(rect.text) ? rect.text : [rect.text];
            var rectHeight = lines.length * 60 + 60;
            var tspanLines = []
            for (var i = 0; i < lines.length; i++) {
              var line = '<tspan class="v-line" x="0" dy="1em">'
              line += lines[i]
              line += '</tspan> '
              tspanLines.push(line) 
            }
            attrs['.uml-class-' + rect.type + '-text'].html = tspanLines.join('');

            attrs['.uml-class-' + rect.type + '-rect'].height = rectHeight;
            attrs['.uml-class-' + rect.type + '-rect'].transform = 'translate(0,' + offsetY + ')';

            offsetY += rectHeight;
           });
        }

});
 



function instance(label, attrs, bfill) {

     var cell = new LinkedClass({
         name: label,
         attributes: attrs,
         size: { width: label.length * 2, height: 60 },
         attrs: {
            '.uml-class-name-rect': {
                fill: bfill,
                stroke: '#fff',
                'stroke-width': 0.5
            },
            '.uml-class-attrs-rect, .uml-class-methods-rect': {
                fill: bfill,
                stroke: '#fff',
                'stroke-width': 0.5
            },
            '.uml-class-attrs-text': {
                'ref-y': 0.5,
                'y-alignment': 'middle'
            }
         }
     });
     graph.addCell(cell);
     instance_list.push(cell);
     return cell;
};

Aggregation = joint.dia.Link.extend({
    defaults: {
        type: 'uml.Aggregation',
        attrs: { '.marker-source': { d: 'M 40 10 L 20 20 L 0 10 L 20 0 z', fill: 'white' }}
    }
});

Composition = joint.dia.Link.extend({
    defaults: {
        type: 'uml.Composition',
        attrs: { '.marker-source': { d: 'M 40 10 L 20 20 L 0 10 L 20 0 z', fill: 'black' }}
    }
});

    function link(source, target, label, ed, comp) {
     if (comp) {
       var aclass = Composition;
     } else {
       var aclass = Aggregation;
     }
     var cell = new aclass({ 
         source: { id: source.id },
         target: { id: target.id },

         router: { 
                name: 'manhattan', 
                args: {
                    startDirections: ['right'],
                    endDirections: [ed || 'left']
                }
            },
         connector: { name: 'rounded' }
     });
     graph.addCell(cell);
     return cell;
};
''')


def _network_js_close():
    return('''    joint.layout.DirectedGraph.layout(graph, { setLinkVertices: false,
                                               nodeSep: 150, rankSep: 100,
                                               marginX: 100, marginY: 100,
				               rankDir: 'LR' });


for (var i = 0; i < instance_list.length; i++) {
    instance_list[i].toFront();
}
''')


def is_http_uri(item):
    result = True
    if not isinstance(item, six.string_types):
        result = False
    else:
        if not (item.startswith('http://') or item.startswith('https://')):
            result = False
        if ',' in item:
            result = False
        if ' ' in item:
            result = False
    return result


class HttpCache(object):
    """
    Requests cache.
    """
    def __init__(self):
        self.cache = {}

    def is_http_uri(self, item):
        return is_http_uri(item)

    def __getitem__(self, item):

        if not self.is_http_uri(item):
            raise ValueError('{} is not a HTTP URI.'.format(item))
        if item not in self.cache:
            # null response, as a fall back
            self.cache[item] = requests.models.Response()
            # now = time.time()
            try:
                # print('trying: {}'.format(item))

                headers = {'Accept': 'application/rdf+xml'}
                self.cache[item] = requests.get(item, headers=headers, timeout=11)
            except Exception:
                try:
                    # print('retrying: {}'.format(item))
                    headers = {'Accept': 'text/html'}
                    self.cache[item] = requests.get(item, headers=headers, timeout=64)
                except Exception:
                    pass

        # print('in {} seconds'.format(time.time() - then))
        return self.cache[item]

    def check_uri(self, uri):
        result = False
        if self[uri].status_code == 200:
            result = True
        return result


class Resource(object):
    _rdftype = 'bald__Resource'
    def __init__(self, baseuri, relative_id, attrs=None, prefixes=None,
                 aliases=None, alias_graph=None):
        """
        A resource of metadata statements.

        attrs: an dictionary of key value pair attributes
        """
        self.baseuri = baseuri
        self.relative_id = relative_id

        if attrs is None:
            attrs = {}
        if prefixes is None:
            prefixes = {}
        if aliases is None:
            aliases = {}

        self.attrs = attrs
        
        self.rdf__type = self._rdftype

        self.aliases = aliases
        self._prefixes = prefixes
        self._prefix_suffix = re.compile('(^(?:(?!__).)*)__((?!.*__).*$)')
        _http_p = 'http[s]?://.*'
        self._http_uri = re.compile('{}'.format(_http_p))
        self._http_uri_prefix = re.compile('{}/|#'.format(_http_p))
        if alias_graph is None:
            alias_graph = rdflib.Graph()
        self.alias_graph = alias_graph

    @property
    def identity(self):
        if self.relative_id is None:
            result = None
        elif self.relative_id:
            result = self.baseuri + self.relative_id
        else:
            result = self.baseuri
        return result
        # return '/'.join([self.baseuri, self.relative_id])

    def __str__(self):
        return '{}:{}: {}'.format(self.identity, type(self), self.attrs)

    def __repr__(self):
        return str(self)

    def __setattr__(self, attr, value):
        reserved_attrs = ['baseuri', 'relative_id', 'prefixes', '_prefixes',
                          '_prefix_suffix', '_http_uri_prefix', '_http_uri',
                          'aliases', 'alias_graph', 'attrs', '_rdftype']
        if attr in reserved_attrs:
            object.__setattr__(self, attr, value)
        else:
            if attr not in self.attrs:
                self.attrs[attr] = set([value])
            elif value not in self.attrs[attr]:
                if isinstance(self.attrs[attr], list):
                    self.attrs[attr].append(value)
                elif isinstance(self.attrs[attr], set):
                    self.attrs[attr].add(value)
                else:
                    self.attrs[attr] = set((self.attrs[attr], value))
            elif isinstance(self.attrs[attr], six.string_types):
                self.attrs[attr] = set([self.attrs[attr]])


    def __getattr__(self, attr):
        if attr not in self.attrs:
            msg = '{} object has no attribute {}'.format(type(self), attr)
            raise AttributeError(msg)
        return self.attrs[attr]

    #@property
    def prefixes(self):
        prefixes = {}
        for key, value in self._prefixes.items():
            if key.endswith('__') and self._http_uri_prefix.match(value):
                pref = key.rstrip('__')
                if pref in prefixes:
                    raise ValueError('This container has conflicting prefix'
                                     ' definitions.')
                prefixes[pref] = value
        return prefixes

    def unpack_predicate(self, astring):
        result = astring
        if isinstance(astring, six.string_types) and self._prefix_suffix.match(astring):
            prefix, suffix = self._prefix_suffix.match(astring).groups()
            if prefix in self.prefixes():
                if self._http_uri.match(self.prefixes()[prefix]):
                    result = astring.replace('{}__'.format(prefix),
                                             self.prefixes()[prefix])
        elif isinstance(astring, six.string_types):
            qstr = ('prefix dct: <http://purl.org/dc/terms/> \n'
                    'prefix owl: <http://www.w3.org/2002/07/owl#> \n'
                    'select ?uri where \n'
                    '{{?uri dct:identifier "{}" ; \n'
                    '      rdf:type ?type. \n'
                    'FILTER(?type in (rdf:Property, owl:ObjectProperty) ) \n'
                    '}}\n')
            predicate_alias_query = (six.text_type(qstr).format(astring))

            qres = self.alias_graph.query(predicate_alias_query)
            results = list(qres)
            if len(results) > 1:
                raise ValueError('multiple alias options')
            elif len(results) == 1:
                result = str(results[0][0])
        if result == astring:
            result = self.baseuri + result
        return result

    def unpack_rdfobject(self, astring, predicate):
        result = astring
        if isinstance(astring, six.string_types) and self._prefix_suffix.match(astring):
            prefix, suffix = self._prefix_suffix.match(astring).groups()
            if prefix in self.prefixes():
                if self._http_uri.match(self.prefixes()[prefix]):
                    result = astring.replace('{}__'.format(prefix),
                                             self.prefixes()[prefix])
        elif isinstance(astring, six.string_types):
            # if not is_http_uri(predicate):
            #     msg = 'predicate must be a http uri, not {}'.format(predicate)
            #     raise ValueError(msg)
            # can be a file uri too
            qstr = ('prefix dct: <http://purl.org/dc/terms/> \n'
                    'select ?uri where \n'
                    '{{ <{pred}> rdfs:range ?range . \n'
                    '?uri dct:identifier "{id}" ; \n'
                    '     rdf:type ?range .\n'
                    '}}\n')
            rdfobj_alias_query = (six.text_type(qstr).format(pred=predicate, id=astring))
            # qres = self.alias_graph.query(rdfobj_alias_query)
            try:
                qres = self.alias_graph.query(rdfobj_alias_query)
                results = list(qres)
                if len(results) > 1:
                    raise ValueError('multiple alias options')
                elif len(results) == 1:
                    result = str(results[0][0])
            except pyparsing.ParseException:
                pass
        return result

    # def unpack_uri(self, astring):
    #     """
    #     Return a URI for the given input string, or return the astring unchanged if
    #     none is available.

    #     """
    #     result = astring
    #     if isinstance(astring, six.string_types) and self._prefix_suffix.match(astring):
    #         prefix, suffix = self._prefix_suffix.match(astring).groups()
    #         if prefix in self.prefixes():
    #             if self._http_uri.match(self.prefixes()[prefix]):
    #                 result = astring.replace('{}__'.format(prefix),
    #                                          self.prefixes()[prefix])
    #     elif isinstance(astring, six.string_types) and astring in self.aliases:
    #         result = self.aliases[astring]
    #     return result

    @property
    def link_template(self):
        return '<a xlink:href="{url}" xlink:show=new text-decoration="underline">{key}</a>'

    def graph_elems(self):
        instances = []
        links = []
        remaining_attrs = self.attrs.copy()
        structural_attrs = ['rdf__type']
        for att in structural_attrs:
            if att in remaining_attrs:
                _ = remaining_attrs.pop(att)

        instances.append(self._graph_elem_attrs(remaining_attrs))

        return instances, links


    def _graph_elem_attrs(self, remaining_attrs):
        attrs = []
        for attr in remaining_attrs:
            attr_uri = self.unpack_predicate(attr)
            if is_http_uri(attr_uri):
                kstr = self.link_template + ': '
                kstr = kstr.format(url=attr_uri, key=attr)
            else:
                kstr = '{key}: '.format(key=attr)
            vals = remaining_attrs[attr]
            if (isinstance(vals, six.string_types) or
               isinstance(vals, np.ma.core.MaskedConstant)):
                vuri = self.unpack_rdfobject(vals, predicate=attr_uri)
                if is_http_uri(vuri):
                    vstr = self.link_template
                    vstr = vstr.format(url=vuri, key=vals)
                else:
                    vstr = '{key}'.format(key=vals)
            else:
                vstrlist = []
                for val in vals:
                    vuri = self.unpack_rdfobject(val, predicate=attr_uri)
                    if is_http_uri(vuri):
                        vstr = self.link_template
                        vstr = vstr.format(url=vuri, key=val)
                    elif isinstance(val, Resource):
                        vstr = ''
                    else:
                        vstr = '{key}'.format(key=val)
                    if vstr:
                        vstrlist.append(vstr)
                if vstrlist == []:
                    vstrlist = ['|']
                vstrlist.sort()
                vstr = ', '.join(vstrlist)

            attrs.append("'{}'".format(kstr + vstr))
            attrs.sort()

        attrs = ''.join(['[' + ', '.join(attrs) + ']'])
        avar = "var {var} = instance('{var}:{type}', {attrs}, '#878800');"
        atype = self.link_template
        type_links = []
        for rdftype in self.rdf__type:
            type_links.append(atype.format(url=self.unpack_rdfobject(rdftype, 'rdf__type'), key=rdftype))
        type_links.sort()
        avar = avar.format(var=self.identity, type=', '.join(type_links), attrs=attrs)

        return avar


    def viewgraph(self):
        """
        Return html to render the Resource as a graph diagram, using the JointJS engine.

        """

        instances, links = self.graph_elems()
        links.sort()
        instances.sort()
        ascript = '\n'.join([_network_js(), '\n'.join(instances), '\n'.join(links),  _network_js_close()])

        html = jinja2.Environment().from_string(_graph_html()).render(title='agraph', script=ascript)

        return html

    def rdfnode(self, graph):
        """
        Create an RDF Node,
        add it to the supplied graph,
        return the node.

        """
        if self.identity is None:
            selfnode = rdflib.BNode()
        else:
            selfnode = rdflib.URIRef(self.identity)
        for attr in self.attrs:
            list_items = []
            objs = self.attrs[attr]
            if(isinstance(objs, np.ndarray)):
                #try to convert np.ndarray to a list
                objs = objs.tolist()

            if not (isinstance(objs, set) or isinstance(objs, list)):
                objs = set([objs])
            for obj in objs:

                rdfpred = self.unpack_predicate(attr)
                if isinstance(obj, Resource):
                    if obj.identity is None:
                        rdfobj = obj.rdfnode(graph)
                    else:
                        rdfobj = rdflib.URIRef(obj.identity)
                else:
                    rdfobj = self.unpack_rdfobject(obj, rdfpred)
                    if is_http_uri(rdfobj):

                        rdfobj = rdflib.URIRef(rdfobj)
                    elif terra_imp and isinstance(rdfobj, datetime.EpochDateTimes):
                        rdfobj = rdflib.Literal(str(rdfobj), datatype=rdflib.XSD.dateTime)
                    elif isinstance(rdfobj, float):
                        rdfobj = rdflib.Literal(rdfobj, datatype=rdflib.XSD.decimal)
                    else:
                        rdfobj = rdflib.Literal(rdfobj)
                rdfpred = rdflib.URIRef(rdfpred)
                if isinstance(objs, set):
                    try:
                        graph.add((selfnode, rdfpred, rdfobj))

                    except AssertionError:
                        pass
                        #graph.add((selfnode, rdfpred, rdfobj))
                elif isinstance(objs, list):
                    list_items.append(rdfobj)
                # recurse and build the related objects
                if isinstance(obj, Resource) and obj.identity is not None:
                    obj_ref = rdflib.URIRef(obj.identity)
                    if not ((obj_ref, None, None) in graph):
                        node = obj.rdfnode(graph)
            if list_items:
                list_name = rdflib.BNode()
                col = rdflib.collection.Collection(graph, list_name, list_items)
                graph.add((selfnode, rdfpred, list_name))

        return selfnode

    def rdfgraph(self):
        """
        Return an rdflib.Graph representing the Resource.

        """
        graph = rdflib.Graph()
        graph.bind('bald', 'https://www.opengis.net/def/binary-array-ld/')
        # why is a trailing slash added here?
        # should all identities of root groups include the trailing slash??
        ## all include trailing slash
        graph.bind('this', self.baseuri)# + '/')
        for prefix_name in self.prefixes():
            
            #strip the double underscore suffix

            # new_name = prefix_name[:-2]

            graph.bind(prefix_name, self.prefixes()[prefix_name])

        for alias_name in self.aliases:
            # hack :S
            uri = self.aliases[alias_name]
            if '?_format' in uri:
                uri = uri.split('?')[0]
            if not (uri.endswith('#') or uri.endswith('/')):
                uri = uri + '/'
            graph.bind(alias_name, uri)
        
        self.rdfnode(graph)
        
        return graph


class Reference(Resource):
    _rdftype = 'bald__Reference'


class Array(Resource):
    _rdftype = 'bald__Array'

    @property
    def array_references(self):
        return self.attrs.get('bald__references', [])

    def graph_elems(self):
        instances = []
        links = []
        remaining_attrs = self.attrs.copy()
        structural_attrs = ['rdf__type']
        for att in structural_attrs:
            if att in remaining_attrs:
                _ = remaining_attrs.pop(att)
        instances.append(self._graph_elem_attrs(remaining_attrs))

        if hasattr(self, 'bald__references'):
            for aref in self.bald__references:
                alink = "link({var}, {target}, 'bald__references');"
                alink = alink.format(var=self.identity, target=aref.identity)
                links.append(alink)

        # if hasattr(self, 'bald__array'):
        #     for aref in self.bald__array:
        #         if isinstance(aref, str):
        #             raise TypeError('unexpected string: {}'.format(aref))
        #         alink = "link({var}, {target}, 'bald__array', 'bottom');"
        #         alink = alink.format(var=self.identity, target=aref.identity)
        #         links.append(alink)


        return instances, links


class Container(Resource):
    _rdftype = 'bald__Container'

    def graph_elems(self):
        instances = []
        links = []

        remaining_attrs = self.attrs.copy()
        structural_attrs = ['rdf__type',
                            'bald__isAliasedBy', 'bald__isPrefixedBy']
        for att in structural_attrs:
            if att in remaining_attrs:
                _ = remaining_attrs.pop(att)

        instances.append(self._graph_elem_attrs(remaining_attrs))

        for member in self.bald__contains:
            new_inst, new_links = member.graph_elems()
            instances = instances + new_inst
            links = links + new_links
            alink = "link({var}, {target}, 'bald__contains', 'top', true);"
            alink = alink.format(var=self.identity, target=member.identity)
            links.append(alink)

        return instances, links


def _merge_sequences(seq1,seq2):
    sm=SequenceMatcher(a=seq1,b=seq2)
    res = []
    for (op, start1, end1, start2, end2) in sm.get_opcodes():
        if op == 'equal' or op=='delete':
            #This range appears in both sequences, or only in the first one.
            res += seq1[start1:end1]
        elif op == 'insert':
            #This range appears in only the second sequence.
            res += seq2[start2:end2]
        elif op == 'replace':
            #There are different ranges in each sequence - add both.
            res += seq1[start1:end1]
            res += seq2[start2:end2]
    return res

def netcdf_shared_dimensions(source_var, target_var):
    result = OrderedDict((('sourceReshape', OrderedDict()),
                          ('targetReshape', OrderedDict())))
    source_dims = OrderedDict(zip(source_var.dimensions, source_var.shape))
    target_dims = OrderedDict(zip(target_var.dimensions, target_var.shape))
    initial = OrderedDict((('sourceReshape', source_dims),
                           ('targetReshape', target_dims)))
    combined_dims_unordered = OrderedDict(source_dims.items() | target_dims.items())
    myorder = _merge_sequences(source_var.dimensions, target_var.dimensions)
    ordered_dims = OrderedDict((k, combined_dims_unordered[k]) for k in myorder)
    result = OrderedDict((('sourceReshape', OrderedDict((k, combined_dims_unordered[k]) for k in myorder)),
                          ('targetReshape', OrderedDict((k, combined_dims_unordered[k]) for k in myorder))))
    for k in result:
        for rk in result[k]:
            if rk not in initial[k]:
                result[k][rk] = 1
    # check overall nValues is consistent
    # is this validation?
    # or, can this only be a code bug, given nc dims???
    for k in result:
        if six.moves.reduce(operator.mul, [i[1] for i in result[k].items()], 1) != six.moves.reduce(operator.mul, [i[1] for i in initial[k].items()], 1):
            raise ValueError('Reshape lists must have the same count for the multiplication of elements')
    return result


@contextlib.contextmanager
def load(afilepath):
    if afilepath.endswith('.hdf'):
        loader = h5py.File
    elif afilepath.endswith('.nc'):
        loader = netCDF4.Dataset
    else:
        raise ValueError('filepath suffix not supported: {}'.format(afilepath))
    #Disable this check for now to allow URL input
    #TODO: Add feature to check both local files and files on the web, e.g. URLs
    #if not os.path.exists(afilepath):
    #    raise IOError('{} not found'.format(afilepath))
    try:
        f = loader(afilepath, "r")
        yield f
    finally:
        try:
            f.close()
        except NameError:
            pass

def load_netcdf(afilepath, baseuri=None, alias_dict=None, cache=None):
    """
    Load a file with respect to binary-array-linked-data.
    Returns a :class:`bald.Collection`
    """
    if alias_dict == None:
        alias_dict = {}
    if cache is None:
        cache = HttpCache()

    with load(afilepath) as fhandle:
        # ensure that baseuri always terminates in a '/'
        if baseuri is None:
            baseuri = 'file://{}/'.format(afilepath)
        elif type(baseuri) == str and not baseuri.endswith('/'):
            baseuri = '{}/'.format(baseuri)
        identity = baseuri

        # prefixes are defined as group attributes in a dedicated group, and/or
        # by external resources
        prefix_var_name  = None
        if hasattr(fhandle, 'bald__isPrefixedBy'):
           prefix_var_name  = fhandle.bald__isPrefixedBy

        prefix_ids = (fhandle.bald__isPrefixedBy if
                      hasattr(fhandle, 'bald__isPrefixedBy') else '')
        prefix_urls = []
        prefix_groups = []
        for pid in prefix_ids.split(' '):
            if pid in fhandle.groups:
                prefix_groups.append(fhandle.groups[pid])
            elif pid.startswith('http://') or pid.startswith('https://'):
                prefix_urls.append(pid)
        prefixes = {}

        skipped_variables = []
        for prefix_group in prefix_groups:
            if prefix_group != {}:
                prefixes = (dict([(prefix, getattr(prefix_group, prefix)) for
                                  prefix in prefix_group.ncattrs() if prefix.endswith('__')]))
                if isinstance(prefix_group, netCDF4._netCDF4.Variable):
                    skipped_variables.append(prefix_var.name)
            # else:
            #     for k in fhandle.ncattrs():
            #         if k.endswith('__'):
            #             prefixes[k] = getattr(fhandle, k)

        prefix_graph = rdflib.Graph()
        for prefix_url in prefix_urls:
            res = cache[prefix_url]
            try:
                prefix_graph.parse(data=res.text, format='xml')
            except Exception:
                print('Failed to parse: {} for prefixes.'.format(prefix_url))

        qres = prefix_graph.query("select ?prefix ?uri where \n"
                                  "{\n"
                                  "?s <http://purl.org/vocab/vann/preferredNamespacePrefix> ?prefix ;\n"
                                  "<http://purl.org/vocab/vann/preferredNamespaceUri> ?uri . \n"
                                  "}")
        for res in qres:
            key, value = (str(res[0]), str(res[1]))
            if key in prefixes and value !=prefixes[key]:
                prefixes.pop(key)
            else:
                prefixes[key] = value

        # check that default set is handled, i.e. bald__ and rdf__
        if 'bald__' not in prefixes:
            prefixes['bald__'] = "https://www.opengis.net/def/binary-array-ld/" 

        if 'rdf__' not in prefixes:
            prefixes['rdf__'] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

        alias_var_name = None
        if hasattr(fhandle, 'bald__isAliasedBy'):
           alias_var_name  = fhandle.bald__isAliasedBy

        alias_var = (fhandle[fhandle.bald__isAliasedBy]
                       if hasattr(fhandle, 'bald__isAliasedBy') else {})
        aliases = {}
        if alias_var != {}:
            aliases = (dict([(alias, getattr(alias_var, alias))
                             for alias in alias_var.ncattrs()]))
            if isinstance(alias_var, netCDF4._netCDF4.Variable):
                skipped_variables.append(alias_var.name)

        aliases = careful_update(aliases, alias_dict)
        attrs = {}
        for k in fhandle.ncattrs():
            attrs[k] = getattr(fhandle, k)

        aliasgraph = rdflib.Graph()

        for alias in aliases:
            response = cache[aliases[alias]]
            try:
                aliasgraph.parse(data=response.text, format='xml')
            except Exception:
                print('Failed to parse: {}'.format(aliases[alias]))
            # try:
            #     import xml.sax._exceptions
            #     aliasgraph.parse(data=response.text, format='xml')
            # except TypeError:
            #     pass
            # except xml.sax._exceptions.SAXParseException:
            #     import pdb; pdb.set_trace()
            #     pass
        # if hasattr(fhandle, 'Conventions'):
        #     conventions = [c.strip() for c in fhandle.Conventions.split(',')]
        #     for conv in conventions:
        #         if conv.startswith('CF-'):
        #             uri = 'http://def.scitools.org.uk/CFTerms?_format=ttl'
        #             aliasgraph.parse(uri)
        #             uri = 'http://vocab.nerc.ac.uk/standard_name/'
        #             aliasgraph.parse(uri, format='n3')
            # qstr = ('select ?alias ?uri where '
            #         '{?uri dct:identifier ?alias .}')
            # qres = aliasgraph.query(qstr)

            # new_aliases = [(str(q[0]), str(q[1])) for q in list(qres)]
            # na_keys = [n[0] for n in new_aliases]
            # if len(set(na_keys)) != len(na_keys):
            #     raise ValueError('duplicate aliases')
            # aliases = careful_update(aliases, dict(new_aliases))
        root_container = Container(baseuri, '', attrs, prefixes=prefixes,
                                   aliases=aliases, alias_graph=aliasgraph)

        root_container.attrs['bald__contains'] = set()
        file_variables = {}
        for name in fhandle.variables:
            if name ==  prefix_var_name:
                continue

            sattrs = fhandle.variables[name].__dict__.copy()

            identity = name
            if baseuri is not None:
                identity = baseuri + name

            # netCDF coordinate variable special case
            if (len(fhandle.variables[name].dimensions) == 1 and
                fhandle.variables[name].dimensions[0] == name and
                len(fhandle.variables[name]) > 0):

                if not isinstance(fhandle.variables[name][0], np.ma.core.MaskedConstant):
                    sattrs['bald__first_value'] = fhandle.variables[name][0]
                    if np.issubdtype(sattrs['bald__first_value'], np.integer):
                        sattrs['bald__first_value'] = int(sattrs['bald__first_value'])
                    elif np.issubdtype(sattrs['bald__first_value'], np.floating):
                        sattrs['bald__first_value'] = float(sattrs['bald__first_value'])
                    if (len(fhandle.variables[name]) > 1 and
                        not isinstance(fhandle.variables[name][-1], np.ma.core.MaskedConstant)):
                        sattrs['bald__last_value'] = fhandle.variables[name][-1]
                        if np.issubdtype(sattrs['bald__last_value'], np.integer):
                            sattrs['bald__last_value'] = int(sattrs['bald__last_value'])
                        elif np.issubdtype(sattrs['bald__last_value'], np.floating):
                            sattrs['bald__last_value'] = float(sattrs['bald__last_value'])

                # datetime special case
                if 'units' in fhandle.variables[name].ncattrs() and terra_imp:
                    ustr = fhandle.variables[name].getncattr('units')
                    pattern = '^([a-z]+) since ([0-9T:\\. -]+)'

                    amatch = re.match(pattern, ustr)
                    if amatch:
                        quantity = amatch.group(1)
                        origin = amatch.group(2)
                        ig = datetime.ISOGregorian()
                        tog = datetime.parse_datetime(origin,
                                                            calendar=ig)
                        if tog is not None:
                            dtype = '{}{}'.format(fhandle.variables[name].dtype.kind,
                                                  fhandle.variables[name].dtype.itemsize)
                            fv = netCDF4.default_fillvals.get(dtype)
                            first = None
                            if fhandle.variables[name][0] == fv:
                                first = np.ma.MaskedArray(fhandle.variables[name][0],
                                                          mask=True)
                            else:
                                first = fhandle.variables[name][0]
                            if first is not None:
                                try:
                                    first = int(first)
                                except Exception:
                                    pass
                                edate_first = datetime.EpochDateTimes(first,
                                                                      quantity,
                                                                      epoch=tog)
                                if first is not np.ma.masked:
                                    sattrs['bald__first_value'] = edate_first
                            if len(fhandle.variables[name]) > 1:
                                if fhandle.variables[name][0] == fv:
                                    last = np.ma.MaskedArray(fhandle.variables[name][-1],
                                                             mask=True)
                                else:
                                    last = fhandle.variables[name][-1]
                                if last:
                                    try:
                                        last = round(last)
                                    except Exception:
                                        pass
                                    edate_last = datetime.EpochDateTimes(last,
                                                                         quantity,
                                                                         epoch=tog)

                                    sattrs['bald__last_value'] = edate_last




                
            if fhandle.variables[name].shape:
                sattrs['bald__shape'] = list(fhandle.variables[name].shape)
                var = Array(baseuri, name, sattrs, prefixes=prefixes,
                            aliases=aliases, alias_graph=aliasgraph)
            else:
                var = Resource(baseuri, name, sattrs, prefixes=prefixes,
                              aliases=aliases, alias_graph=aliasgraph)
            root_container.attrs['bald__contains'].add(var)

            file_variables[name] = var
                

        reference_prefixes = dict()
        reference_graph = copy.copy(aliasgraph)

        response = cache['https://www.opengis.net/def/binary-array-ld']
        reference_graph.parse(data=response.text, format='n3')

        # # reference_graph.parse('https://www.opengis.net/def/binary-array-ld')
        # qstr = ('prefix bald: <https://www.opengis.net/def/binary-array-ld/> '
        #         'prefix skos: <http://www.w3.org/2004/02/skos/core#> '
        #         'select ?s '
        #         'where { '
        #         '  ?s rdfs:range ?type . '
        #         'filter(?type != rdfs:Literal) '
        #         'filter(?type != skos:Concept) '
        #         '}')
        
        # refs_ = reference_graph.query(qstr)

        qstr = ('prefix bald: <https://www.opengis.net/def/binary-array-ld/> '
                'prefix skos: <http://www.w3.org/2004/02/skos/core#> '
                'prefix owl: <http://www.w3.org/2002/07/owl#> '
                'select ?s '
                'where { '
                '  ?s rdfs:range ?type . '
                '  ?type rdf:type ?rtype . '
                'filter(?rtype = owl:Class) '
                '}')
        
        qstr = ('prefix bald: <https://www.opengis.net/def/binary-array-ld/> '
                'prefix skos: <http://www.w3.org/2004/02/skos/core#> '
                'prefix owl: <http://www.w3.org/2002/07/owl#> '
                'select ?s '
                'where { '
                '  ?s rdfs:range ?type . '
                'filter(?type in (rdfs:Literal, skos:Concept)) '
                '}')
        
        refs = reference_graph.query(qstr)

        non_ref_prefs = [str(ref[0]) for ref in list(refs)]

        qstr = ('prefix bald: <https://www.opengis.net/def/binary-array-ld/> '
                'prefix skos: <http://www.w3.org/2004/02/skos/core#> '
                'prefix owl: <http://www.w3.org/2002/07/owl#> '
                'select ?s '
                'where { '
                '   {?s rdfs:range bald:Resource .} '
                '  UNION '
                '  {?s rdfs:range ?as . '
                '  ?as rdfs:subClassOf bald:Resource .} '
                '}')
        
        refs = reference_graph.query(qstr)

        ref_prefs = [str(ref[0]) for ref in list(refs)]

        # cycle again and find references
        for name in fhandle.variables:
            if name ==  prefix_var_name:
                continue

            var = file_variables[name]
            sattrs = fhandle.variables[name].__dict__.copy()

            # coordinate variables are bald__references too
            if 'bald__Reference' not in var.rdf__type:
                for dim in fhandle.variables[name].dimensions:
                    if file_variables.get(dim) and name != dim:
                        _make_ref_entities(var, fhandle, dim, name,
                                           baseuri, root_container,
                                           file_variables, prefixes,
                                           aliases, aliasgraph)
            # import pdb; pdb.set_trace()
            # for sattr in sattrs:
            for sattr in (sattr for sattr in sattrs if
                          root_container.unpack_predicate(sattr) in ref_prefs):

                if isinstance(sattrs[sattr], six.string_types):

                    if sattrs[sattr].startswith('(') and sattrs[sattr].endswith(')'):
                        potrefs_list = sattrs[sattr].lstrip('( ').rstrip(' )').split(' ')
                        refs = np.array([file_variables.get(pref) is not None
                                         for pref in potrefs_list])
                        if np.all(refs):
                            var.attrs[sattr] = [file_variables.get(pref)
                                                for pref in potrefs_list]
                            for pref in potrefs_list:
                                _make_ref_entities(var, fhandle,
                                                   pref, name, baseuri,
                                                   root_container,
                                                   file_variables, prefixes,
                                                   aliases, aliasgraph)

                    else:
                        potrefs_set = sattrs[sattr].split(' ')
                        refs = np.array([file_variables.get(pref) is not None
                                         for pref in potrefs_set])
                        if np.all(refs):
                            var.attrs[sattr] = set([file_variables.get(pref)
                                                    for pref in potrefs_set])
                            for pref in potrefs_set:
                                # coordinate variables already handled
                                if pref not in fhandle.variables[name].dimensions:
                                    _make_ref_entities(var, fhandle,
                                                       pref, name, baseuri,
                                                       root_container,
                                                       file_variables, prefixes,
                                                       aliases, aliasgraph)

    return root_container

def _make_ref_entities(var, fhandle, pref, name, baseuri,
                       root_container, file_variables,
                       prefixes, aliases, aliasgraph):
    shapematch = (fhandle.variables[name].shape ==
                  fhandle.variables[pref].shape)

    if (fhandle.variables[name].shape and not shapematch and
        fhandle.variables[pref].shape):
        try:
            refset = var.attrs.get('bald__references', set())
            if not isinstance(refset, set):
                refset = set((refset,))
            identity = None
            rattrs = {}

            reshapes = netcdf_shared_dimensions(fhandle.variables[name],
                                                fhandle.variables[pref])

            rattrs['bald__targetShape'] = list(fhandle.variables[pref].shape)
            sourceReshape =  [i[1] for i in reshapes['sourceReshape'].items()]
            if sourceReshape != list(fhandle.variables[name].shape):
                rattrs['bald__sourceReshape'] = sourceReshape
            targetReshape = [i[1] for i in reshapes['targetReshape'].items()]
            if targetReshape != list(fhandle.variables[pref].shape):
                rattrs['bald__targetReshape'] = targetReshape
            rattrs['bald__target'] = set((file_variables.get(pref),))
            ref_node = Reference(baseuri, identity, rattrs,
                               prefixes=prefixes,
                               aliases=aliases,
                               alias_graph=aliasgraph)

            refset.add(ref_node)
            var.attrs['bald__references'] = refset
        except ValueError:
            # Indexing and dimension identification can fail, especially
            # with unexpectedy formated files.  Fail silently on load, to
            # that a partial graph may be returned.  Issues like this are
            # deferred to validation.
            pass


def validate_netcdf(afilepath, baseuri=None, cache=None, uris_resolve=False):
    """
    Validate a file with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`

    """
    root_container = load_netcdf(afilepath, baseuri=baseuri, cache=cache)
    return validate(root_container, cache=cache, uris_resolve=uris_resolve)


def validate_hdf5(afilepath, baseuri=None, cache=None, uris_resolve=False):
    """
    Validate a file with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`

    """
    root_container = load_hdf5(afilepath, baseuri=baseuri, cache=cache)
    return validate(root_container, cache=cache, uris_resolve=uris_resolve)

def validate(root_container, sval=None, cache=None, uris_resolve=False):
    """
    Validate a Container with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`

    """
    if sval is None:
        sval = bv.StoredValidation()

    root_val = bv.ContainerValidation(resource=root_container, httpcache=cache,
                                      uris_resolve=uris_resolve)
    sval.stored_exceptions += root_val.exceptions()
    for resource in root_container.attrs.get('bald__contains', set()):
        if isinstance(resource, Array):
            array_val = bv.ArrayValidation(resource, httpcache=cache,
                                           uris_resolve=uris_resolve)
            sval.stored_exceptions += array_val.exceptions()
        elif isinstance(resource, Container):
            sval = validate(resource, sval=sval, cache=cache,
                            uris_resolve=uris_resolve)
        elif isinstance(resource, Resource):
            resource_val = bv.ResourceValidation(resource, httpcache=cache,
                                               uris_resolve=uris_resolve)
            sval.stored_exceptions += resource_val.exceptions()

    return sval

def careful_update(adict, bdict):
    """
    Carefully updates a dictionary with another dictionary, raising a
    ValueError if keys are shared.
    
    """
    if not set(adict.keys()).isdisjoint(set(bdict.keys())):
        raise ValueError('adict shares keys with bdict')
    else:
        adict.update(bdict)
        return adict

def load_hdf5(afilepath, baseuri=None, alias_dict=None, cache=None):
    if cache is None:
        cache = HttpCache()
    with load(afilepath) as fhandle:
        # unused?
        cache = {}
        if baseuri is None:
            baseuri = 'file://{}/'.format(afilepath)

        elif type(baseuri) == str and not baseuri.endswith('/'):
            baseuri = '{}/'.format(baseuri)

        root_container, file_variables = _hdf_group(fhandle, baseuri=baseuri,
                                                    alias_dict=alias_dict, cache=cache)
        _hdf_references(fhandle, root_container, file_variables)
    return root_container

def _hdf_group(fhandle, identity='root', baseuri=None, prefixes=None,
               aliases=None, alias_dict=None, cache=None):
    if cache is None:
        cache = HttpCache()

    prefix_group = fhandle.attrs.get('bald__isPrefixedBy')
    if prefixes is None:
        prefixes = {}
    if prefix_group:
        prefixes = careful_update(prefixes, dict(fhandle[prefix_group].attrs))
    alias_group = fhandle.attrs.get('bald__isAliasedBy')
    if aliases is None:
        aliases = {}
    if alias_dict is None:
        alias_dict = {}
    if alias_group:
        aliases = careful_update(aliases, dict(fhandle[alias_group].attrs))
    attrs = dict(fhandle.attrs)
    aliasgraph = rdflib.Graph()
    root_container = Container(baseuri, identity, attrs, prefixes=prefixes,
                               aliases=aliases, alias_graph=aliasgraph)

    root_container.attrs['bald__contains'] = set()

    file_variables = {}
    # iterate through the datasets and groups
    for name, dataset in fhandle.items():
        # skip pattern
        skip = ((prefix_group and dataset == fhandle[prefix_group]) or
                (alias_group and dataset == fhandle[alias_group]))
        if not skip:
            if isinstance(dataset, h5py._hl.group.Group):
                new_cont, new_fvars = _hdf_group(dataset, name, baseuri, prefixes, aliases)
                root_container.attrs['bald__contains'].add(new_cont)
                file_variables = careful_update(file_variables, new_fvars)
            #if hasattr(dataset, 'shape'):
            elif isinstance(dataset, h5py._hl.dataset.Dataset):
                sattrs = dict(dataset.attrs)
                sattrs['bald__shape'] = list(dataset.shape)
                dset = Array(baseuri, name, sattrs, prefixes, aliases, aliasgraph)
                root_container.attrs['bald__contains'].add(dset)
                file_variables[dataset.name] = dset
    return root_container, file_variables

def _hdf_references(fhandle, root_container, file_variables):
    for member in root_container.bald__contains:
        for attr in member.attrs:
            vals = member.attrs[attr]
            if not isinstance(vals, np.ndarray):
                vals = [vals]
            new_vals = set(())
            for val in vals:
                if isinstance(val, h5py.h5r.Reference):
                    new_vals.add(file_variables[fhandle[val].name])
            if new_vals:
                member.attrs[attr] = new_vals
        if isinstance(member, Container):
            _hdf_references(fhandle, member, file_variables)




    
