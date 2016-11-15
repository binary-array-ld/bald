import contextlib
import re

import h5py
import jinja2
import netCDF4
import requests

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
         labels: [{ position: .5, attrs: { text: { text: label || '', 'font-weight': 'bold' } } }],

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
    return isinstance(item, basestring) and (item.startswith('http://') or item.startswith('https://'))


class HttpCache(object):
    """
    Requests cache.
    """
    def __init__(self):
        self.cache = {}

    def is_http_uri(self, item):
        return isinstance(item, basestring) and (item.startswith('http://') or item.startswith('https://'))

    def __getitem__(self, item):

        if not self.is_http_uri(item):
            raise ValueError('{} is not a HTTP URI.'.format(item))
        if item not in self.cache:
            headers = {'Accept': 'text/turtle'}
            self.cache[item] = requests.get(item, headers=headers)

        return self.cache[item]

    def check_uri(self, uri):
        result = False
        if self[uri].status_code == 200:
            result = True
        return result


class Subject(object):
    def __init__(self, attrs=None, prefixes=None, aliases=None,
                 rdftype='bald__Subject'):
        """
        A subject of metadata statements.

        attrs: an dictionary of key value pair attributes
        """
        if attrs is None:
            attrs = {}
        if prefixes is None:
            prefixes = {}
        if aliases is None:
            aliases = {}
        self.attrs = attrs
        if 'rdf__type' not in attrs:
            attrs['rdf__type'] = set([rdftype])
        elif rdftype not in attrs['rdf__type']:
            if isinstance(attrs['rdf__type'], list):
                attrs['rdf__type'].append(rdftype)
            elif isinstance(attrs['rdf__type'], set):
                attrs['rdf__type'].add(rdftype)
            else:
                attrs['rdf__type'] = set((attrs['rdf__type'], rdftype))
        elif isinstance(attrs['rdf__type'], basestring):
            attrs['rdf__type'] = set([attrs['rdf__type']])

        self.aliases = aliases
        self._prefixes = prefixes
        self._prefix_suffix = re.compile('(^(?:(?!__).)*)__((?!.*__).*$)')
        _http_p = 'http[s]?://.*'
        self._http_uri = re.compile('{}'.format(_http_p))
        self._http_uri_prefix = re.compile('{}/|#'.format(_http_p))

    def __str__(self):
        return '{}: {}'.format(type(self), self.attrs)

    def __repr__(self):
        return str(self)

    def __getattr__(self, attr):
        if attr not in self.attrs:
            msg = '{} object has no attribute {}'.format(type(self), attr)
            raise AttributeError(msg)
        return self.attrs[attr]

    def prefixes(self):
        prefixes = {}
        for key, value in self._prefixes.iteritems():
            if key.endswith('__') and self._http_uri_prefix.match(value):
                pref = key.rstrip('__')
                if pref in prefixes:
                    raise ValueError('This container has conflicting prefix'
                                     ' definitions.')
                prefixes[pref] = value
        return prefixes

    def unpack_uri(self, astring):
        result = astring
        if isinstance(astring, basestring) and self._prefix_suffix.match(astring):
            prefix, suffix = self._prefix_suffix.match(astring).groups()
            if prefix in self.prefixes():
                if self._http_uri.match(self.prefixes()[prefix]):
                    result = astring.replace('{}__'.format(prefix),
                                             self.prefixes()[prefix])
        elif isinstance(astring, basestring) and astring in self.aliases:
            result = self.aliases[astring]
        return result

    @property
    def link_template(self):
        return '<a xlink:href="{url}" xlink:show=new text-decoration="underline">{key}</a>'

    def graph_elem_attrs(self, remaining_attrs):
        attrs = []
        for attr in remaining_attrs:
            if is_http_uri(self.unpack_uri(attr)):
                kstr = self.link_template + ': '
                kstr = kstr.format(url=self.unpack_uri(attr), key=attr)
            else:
                kstr = '{key}: '.format(key=attr)
            vals = remaining_attrs[attr]
            if isinstance(vals, basestring):
                if is_http_uri(self.unpack_uri(vals)):
                    vstr = self.link_template
                    vstr = vstr.format(url=self.unpack_uri(vals), key=vals)
                else:
                    vstr = '{key}'.format(key=vals)
            else:
                vstrlist = []
                for val in vals:
                    if is_http_uri(self.unpack_uri(val)):
                        vstr = self.link_template
                        vstr = vstr.format(url=self.unpack_uri(val), key=val)
                    elif isinstance(val, Subject):
                        vstr = ''
                    else:
                        vstr = '{key}'.format(key=val)
                    if vstr:
                        vstrlist.append(vstr)
                if vstrlist == []:
                    vstrlist = ['|']
                vstr = ', '.join(vstrlist)

            attrs.append("'{}'".format(kstr + vstr))

        attrs = ''.join(['[' + ', '.join(attrs) + ']'])
        avar = "var {var} = instance('{var}:{type}', {attrs}, '#878800');"
        atype = self.link_template
        type_links = []
        for rdftype in self.rdf__type:
            type_links.append(atype.format(url=self.unpack_uri(rdftype), key=rdftype))
        avar = avar.format(var=self.attrs['@id'], type=', '.join(type_links), attrs=attrs)

        return avar


    def viewgraph(self):

        instances, links = self.graph_elems()
        ascript = '\n'.join([_network_js(), '\n'.join(instances), '\n'.join(links),  _network_js_close()])

        html = jinja2.Environment().from_string(_graph_html()).render(title='agraph', script=ascript)

        return html

    def rdfgraph(self):
        graph = rdflib.Graph()
        
        
        return graph
        

class Array(Subject):
    def __init__(self, attrs=None, prefixes=None, aliases=None,
                 shape=None):
        self.shape = shape
        rdftype = 'bald__Array'
        super(Array, self).__init__(attrs, prefixes, aliases, rdftype)
        if shape:
            self.attrs['bald__shape'] = self.shape

    @property
    def array_references(self):
        return self.attrs.get('bald__references', [])

    def graph_elems(self):
        instances = []
        links = []
        remaining_attrs = self.attrs.copy()
        structural_attrs = ['@id', 'rdf__type']
        for att in structural_attrs:
            if att in remaining_attrs:
                _ = remaining_attrs.pop(att)
        instances.append(self.graph_elem_attrs(remaining_attrs))

        if hasattr(self, 'bald__references'):
            for aref in self.bald__references:
                alink = "link({var}, {target}, 'bald__references');"
                alink = alink.format(var=self.attrs['@id'], target=aref.attrs.get('@id', ''))
                links.append(alink)

        if hasattr(self, 'bald__array'):
            for aref in self.bald__array:
                alink = "link({var}, {target}, 'bald__array', 'bottom');"
                alink = alink.format(var=self.attrs['@id'], target=aref.attrs.get('@id', ''))
                links.append(alink)


        return instances, links


class Container(Subject):
    def __init__(self, attrs=None, prefixes=None, aliases=None,
                 shape=None):
        rdftype = 'bald__Container'
        super(Container, self).__init__(attrs, prefixes, aliases, rdftype)

    def graph_elems(self):
        instances = []
        links = []

        remaining_attrs = self.attrs.copy()
        structural_attrs = ['@id', 'rdf__type',
                            'bald__isAliasedBy', 'bald__isPrefixedBy']
        for att in structural_attrs:
            if att in remaining_attrs:
                _ = remaining_attrs.pop(att)

        instances.append(self.graph_elem_attrs(remaining_attrs))

        for member in self.bald__contains:
            new_inst, new_links = member.graph_elems()
            instances = instances + new_inst
            links = links + new_links
            alink = "link({var}, {target}, 'bald__contains', 'top', true);"
            alink = alink.format(var=self.attrs['@id'], target=member.attrs['@id'])
            links.append(alink)

        return instances, links


@contextlib.contextmanager
def load(afilepath):
    if afilepath.endswith('.hdf'):
        loader = h5py.File
    else:
        raise ValueError('filepath suffix not supported')
    try:
        f = loader(afilepath, "r")
        yield f
    finally:
        f.close()


@contextlib.contextmanager
def load(afilepath):
    if afilepath.endswith('.hdf'):
        loader = h5py.File
    elif afilepath.endswith('.nc'):
        loader = netCDF4.Dataset
    else:
        raise ValueError('filepath suffix not supported')
    try:
        f = loader(afilepath, "r")
        yield f
    finally:
        f.close()

def load_netcdf(afilepath):
    """
    Validate a file with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`
    """

    with load(afilepath) as fhandle:
        prefix_group = (fhandle[fhandle.bald__isPrefixedBy] if
                        hasattr(fhandle, 'bald__isPrefixedBy') else {})
        prefixes = {}
        if prefix_group:
            prefixes = (dict([(prefix, getattr(prefix_group, prefix)) for
                              prefix in prefix_group.ncattrs()]))
        else:
            for k in fhandle.ncattrs():
                if k.endswith('__'):
                    prefixes[k] = getattr(fhandle, k)
        alias_group = (fhandle[fhandle.bald__isAliasedBy]
                       if hasattr(fhandle, 'bald__isAliasedBy') else {})
        aliases = {}
        if alias_group:
            aliases = (dict([(alias, getattr(alias_group, alias))
                             for alias in alias_group.ncattrs()]))

        attrs = {}
        for k in fhandle.ncattrs():
            attrs[k] = getattr(fhandle, k)
        # It would be nice to use the URI of the file if it is known. 
        attrs['@id'] = 'root'
        root_container = Container(attrs, prefixes=prefixes,
                                   aliases=aliases)
        root_container.attrs['bald__contains'] = []
        file_variables = {}
        for name in fhandle.variables:

            sattrs = fhandle.variables[name].__dict__.copy()
            # inconsistent use of '/'; fix it
            # sattrs['@id'] = '/{}'.format(name)
            sattrs['@id'] = '{}'.format(name)

            # netCDF coordinate variable special case
            if (len(fhandle.variables[name].dimensions) == 1 and
                fhandle.variables[name].dimensions[0] == name):
                sattrs['bald__array'] = name
                sattrs['rdf__type'] = 'bald__Reference'

            var = Array(sattrs, prefixes=prefixes, aliases=aliases,
                        shape=fhandle.variables[name].shape)
            root_container.attrs['bald__contains'].append(var)
            file_variables[name] = var
                


        # cycle again and find references
        for name in fhandle.variables:
            var = file_variables[name]
            # reverse lookup based on type to be added
            lookups = ['bald__references', 'bald__array']
            for lookup in lookups:
                if lookup in var.attrs:
                    child_dset_set = var.attrs[lookup].split(' ')
                    var.attrs[lookup] = set()
                    for child_dset_name in child_dset_set:
                        carray = file_variables.get(child_dset_name)
                    var.attrs[lookup].add(carray)
            # coordinate variables are bald__references except for
            # variables that already declare themselves as bald__Reference 
            if 'bald__Reference' not in var.rdf__type:
                for dim in fhandle.variables[name].dimensions:
                    if file_variables.get(dim):
                        refset = var.attrs.get('bald__references', set())
                        refset.add(file_variables.get(dim))
                        var.attrs['bald__references'] = refset


    return root_container


def validate_netcdf(afilepath):
    """
    Validate a file with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`

    """
    root_container = load_netcdf(afilepath)
    return validate(root_container)


def validate_hdf5(afilepath):
    """
    Validate a file with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`

    """
    root_container = load_hdf5(afilepath)
    return validate(root_container)

def validate(root_container):
    """
    Validate a Container with respect to binary-array-linked-data.
    Returns a :class:`bald.validation.Validation`

    """
    sval = bv.StoredValidation()

    root_val = bv.ContainerValidation(subject=root_container)
    sval.stored_exceptions += root_val.exceptions()
    for subject in root_container.attrs.get('bald__contains', []):
        
        # a dataset's attribute collection inherits from and
        # specialises it's container's attrbiute collection
        # this only helps with prefixes, afaik, hence:
        # #
        array_val = bv.ArrayValidation(subject)
        sval.stored_exceptions += array_val.exceptions()

    return sval

def load_hdf5(afilepath):
    with load(afilepath) as fhandle:
        # unused?
        cache = {}
        prefix_group = fhandle.attrs.get('bald__isPrefixedBy')
        prefixes = {}
        if prefix_group:
            prefixes = dict(fhandle[prefix_group].attrs)
        alias_group = fhandle.attrs.get('bald__isAliasedBy')
        aliases = {}
        if alias_group:
            aliases = dict(fhandle[alias_group].attrs)
        attrs = dict(fhandle.attrs)
        attrs['@id'] = 'root'
        root_container = Container(attrs, prefixes=prefixes, aliases=aliases)

        root_container.attrs['bald__contains'] = []

        # iterate through the datasets
        for name, dataset in fhandle.items():
            if hasattr(dataset, 'shape'):
                sattrs = dict(dataset.attrs)
                sattrs['@id'] = dataset.name
                ref = sattrs.get('bald__references', '')
                if ref:
                    ref_dset = fhandle[ref]
                    child_dset = fhandle[ref_dset.attrs.get('bald__array',
                                                            None)]
                    if child_dset:
                        cattrs = dict(child_dset.attrs)
                        cattrs['@id'] = child_dset.name
                        carray = Array(cattrs, prefixes, aliases,
                                       child_dset.shape)
                        sattrs['bald__references'] = [carray]
                dset = Array(sattrs, prefixes, aliases, dataset.shape)
                root_container.attrs['bald__contains'].append(dset)
            
    return root_container

    
