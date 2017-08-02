from __future__ import print_function
from neo4jrestclient.client import GraphDatabase, Node, Relationship

import pyh2
import re
import sys


def getSymbolTag(symbol):
    symbolTag = symbol
    
    if symbol == '\'':
        symbolTag = 'SingleQuote'
    elif symbol == '"':
        symbolTag = 'FullQuote'
    elif symbol == '%':
        symbolTag = 'PercentSign'
    
    return symbolTag


def writeUnitsTable(dB, parent):
    rows = dB.query(q = 'MATCH (n:UnitName)-->(u:Unit) ' \
                        'WITH n, u ' \
                        'OPTIONAL MATCH (u)<--(o) ' \
                        'WHERE o.name <> n.name ' \
                        'WITH n, u, COLLECT(o) AS os ' \
                        'WITH n, u, FILTER(x in os WHERE x:UnitName) AS n2, FILTER(x in os WHERE x:UnitSymbol) AS s ' \
                        'RETURN n.name AS name, n.plural AS plural, n.comments as comments1, u.definition AS definition, u.comment as comment2, u.formula AS formula, u.references AS references, u.sources AS sources, ' \
                        'EXTRACT(x in n2 | x.name) AS names, EXTRACT(x in s | x.name) AS symbols ' \
                        'ORDER BY LOWER(n.name)')
    
    divTabPanel = parent << pyh2.div(**{'role' : 'tabpanel', 'class' : 'tab-pane active', 'id' : 'UnitsByName'})
    
    divTabPanel << pyh2.h2('Units by Name')
    
    table = divTabPanel << pyh2.table(**{'class' : 'table table-bordered table-condensed table-hover'})
    
    row = table << pyh2.tr()

    row << pyh2.th('Unit', **{'class' : 'col-md-2'})
    row << pyh2.th('Plural', **{'class' : 'col-md-2'})
    row << pyh2.th('Formula', **{'class' : 'col-md-2'})
    row << pyh2.th('Definition', **{'class' : 'col-md-3'})
    row << pyh2.th('Symbol(s)', **{'class' : 'col-md-1'})
    row << pyh2.th('Other names', **{'class' : 'col-md-2'})
    
    seenUnitList = list()
    
    for entry in rows:
        name = entry[0].encode(errors = 'xmlcharrefreplace')
        
        if name in seenUnitList:
            continue
        
        seenUnitList.append(name)
        
        plural = ''
        
        if entry[1] is not None:
            plural = entry[1].encode(errors = 'xmlcharrefreplace')
        
        nameComments = list()
          
        if entry[2] is not None:
            for item in entry[2]:
                nameComments.append(item.encode(errors = 'xmlcharrefreplace'))
        
        definition = ''
        
        if entry[3] is not None:
            definition = entry[3].encode(errors = 'xmlcharrefreplace')
        
        definitionComment = ''
        
        if entry[4] is not None:
            definitionComment = entry[4].encode(errors = 'xmlcharrefreplace')
        
        formula = entry[5].encode(errors = 'xmlcharrefreplace')
        
        references = list()
        sources    = list()
        
        if entry[6] is not None:
            for item in entry[6]:
                references.append(item.encode(errors = 'xmlcharrefreplace'))
            
            for item in entry[7]:
                sources.append(item.encode(errors = 'xmlcharrefreplace'))
        
        otherNames = list()
        
        for item in entry[8]:
            otherName = item.encode(errors = 'xmlcharrefreplace')
            
            if otherName not in otherNames:
                otherNames.append(otherName)
        
        otherNames.sort()
        
        symbols = list()
        
        for item in entry[9]:
            symbol = item.encode(errors = 'xmlcharrefreplace')
            
            if symbol not in symbols:
                symbols.append(symbol)
        
        symbols.sort()
        
        row = table << pyh2.tr()
        
        column = row << pyh2.td()
        
        column << pyh2.a(id = name)
        
        column << name
        
        if 0 < len(nameComments):
            column << ' (' + nameComments[0]
            
            for comment in nameComments[1:]:
                column << ',<br/>' + comment
            
            column << ')'
        
        row << pyh2.td(plural)
        
        column = row << pyh2.td()
        
        if 0 < len(references):
            for index in range(0, len(references)):
                parts = formula.partition(sources[index])
                
                head    = parts[0]
                ref     = references[index]
                pre     = parts[1][0:-len(ref)]
                formula = parts[2]
                
                column << head + pre
                column << pyh2.a(ref, href = '#' + getSymbolTag(ref))
            
        if '' != formula:
            column << formula
        
        column = row << pyh2.td()
        
        column << definition
        
        if '' != definitionComment:
            column << ' (' + definitionComment + ')'
        
        column = row << pyh2.td()
        
        if 0 < len(symbols):
            column << pyh2.a(symbols[0], href = '#' + getSymbolTag(symbols[0]))
            
            del symbols[0]
            
            for symbol in symbols:
                column << ', '
                column << pyh2.a(symbol, href = '#' + getSymbolTag(symbol))
        
        column = row << pyh2.td()
        
        if 0 < len(otherNames):
            column << pyh2.a(otherNames[0], href = '#' + otherNames[0])
            
            del otherNames[0]
            
            for otherName in otherNames:
                column << ', '
                column << pyh2.a(otherName, href = '#' + otherName)


def writeSymbolsTable(dB, parent):
    rows = dB.query(q = 'MATCH (s:UnitSymbol)-->(u:Unit) ' \
                        'WITH s, u '\
                        'OPTIONAL MATCH (u)<--(o) ' \
                        'WHERE o.name <> s.name ' \
                        'WITH s, u, COLLECT(o) AS os ' \
                        'WITH s, u, FILTER(x in os WHERE x:UnitName) AS n, FILTER(x in os WHERE x:UnitSymbol) AS s2 ' \
                        'RETURN s.name AS symbol, s.comment as comment1, u.formula AS formula, u.definition as definition, u.comment as comment2, u.references AS references, u.sources AS sources, ' \
                        'EXTRACT(x in n | x.name) AS names, EXTRACT(x in s2 | x.name) AS symbols ' \
                        'ORDER BY LOWER(s.name)')
    
    divTabPanel = parent << pyh2.div(**{'role' : 'tabpanel', 'class' : 'tab-pane', 'id' : 'UnitsBySymbol'})
    
    divTabPanel << pyh2.h2('Units by Symbol')
    
    table = divTabPanel << pyh2.table(**{'class' : 'table table-bordered table-condensed table-hover'})
    
    row = table << pyh2.tr()

    row << pyh2.th('Symbol', **{'class' : 'col-md-2'})
    row << pyh2.th('Formula', **{'class' : 'col-md-2'})
    row << pyh2.th('Definition', **{'class' : 'col-md-4'})
    row << pyh2.th('Name(s)', **{'class' : 'col-md-2'})
    row << pyh2.th('Other Symbols', **{'class' : 'col-md-2'})
    
    seenSymbolList = list()
    
    for entry in rows:
        symbol = entry[0].encode(errors = 'xmlcharrefreplace')
        
        if symbol in seenSymbolList:
            continue
        
        seenSymbolList.append(symbol)
        
        symbolComment = '' 
        
        if entry[1] is not None:
            symbolComment = entry[1].encode(errors = 'xmlcharrefreplace')
        
        formula = entry[2].encode(errors = 'xmlcharrefreplace')
        
        definition = ''
        
        if entry[3] is not None:
            definition = entry[3].encode(errors = 'xmlcharrefreplace')
        
        definitionComment = ''
        
        if entry[4] is not None:
            definitionComment = entry[4].encode(errors = 'xmlcharrefreplace')
        
        references = list()
        sources    = list()
        
        if entry[5] is not None:
            for item in entry[5]:
                references.append(item.encode(errors = 'xmlcharrefreplace'))
            
            for item in entry[6]:
                sources.append(item.encode(errors = 'xmlcharrefreplace'))
        
        names = list()
        
        for item in entry[7]:
            name = item.encode(errors = 'xmlcharrefreplace')
            
            if name not in names:
                names.append(name)
        
        names.sort()
        
        otherSymbols = list()
        
        for item in entry[8]:
            otherSymbol = item.encode(errors = 'xmlcharrefreplace')
            
            if otherSymbol not in otherSymbols:
                otherSymbols.append(otherSymbol)
        
        otherSymbols.sort()
        
        row = table << pyh2.tr()
        
        column = row << pyh2.td()

        column << pyh2.a(id = getSymbolTag(symbol))
        column << symbol
        
        if '' != symbolComment:
            column << ' (' + symbolComment + ')'
        
        column = row << pyh2.td()
        
        if 0 < len(references):
            for index in range(0, len(references)):
                parts = formula.partition(sources[index])
                
                head    = parts[0]
                ref     = references[index]
                pre     = parts[1][0:-len(ref)]
                formula = parts[2]
                
                refTag = ref
                
                column << head + pre
                column << pyh2.a(ref, href = '#' + getSymbolTag(ref))
            
        if '' != formula:
            column << formula
        
        column = row << pyh2.td()
        
        column << definition
        
        if '' != definitionComment:
            column << ' (' + definitionComment + ')'
        
        column = row << pyh2.td()
        
        if 0 < len(names):
            column << pyh2.a(names[0], href = '#' + names[0])
            
            del names[0]
            
            for name in names:
                column << ', '
                column << pyh2.a(name, href = '#' + name)
        
        column = row << pyh2.td()
        
        if 0 < len(otherSymbols):
            column << pyh2.a(otherSymbols[0], href = '#' + getSymbolTag(otherSymbols[0]))
            
            del otherSymbols[0]
            
            for otherSymbol in otherSymbols:
                column << ', '
                column << pyh2.a(otherSymbol, href = '#' + getSymbolTag(otherSymbol))


def writePrefixesTable(dB, parent):
    rows = dB.query(q = 'MATCH (p:Prefix)<--(s:PrefixSymbol) ' \
                        'WITH p, COLLECT(s.comment) as comments, COLLECT(s.name) AS symbols ' \
                        'RETURN p.name AS prefix, p.value AS definition, ' \
                        'symbols AS symbols, comments as comments ' \
                        'ORDER BY TOFLOAT(p.value) DESC')
    
    divTabPanel = parent << pyh2.div(**{'role' : 'tabpanel', 'class' : 'tab-pane', 'id' : 'Prefixes'})
    
    divTabPanel << pyh2.h2('Unit Prefixes')
    
    table = divTabPanel << pyh2.table(**{'class' : 'table table-bordered table-condensed table-hover'})
    
    table << pyh2.tr(pyh2.th('Prefix') + pyh2.th('Definition') + pyh2.th('Symbol(s)') + pyh2.th('Comments'))
    
    seenPrefixList = list()
    
    for entry in rows:
        prefix = entry[0].encode(errors = 'xmlcharrefreplace')
        
        if prefix in seenPrefixList:
            continue
        
        seenPrefixList.append(prefix)
        
        value = entry[1].encode(errors = 'xmlcharrefreplace')
        
        symbols = list()
        
        for item in entry[2]:
            symbol = item.encode(errors = 'xmlcharrefreplace')
            
            if symbol not in symbols:
                symbols.append(symbol)
        
        comments = list()
        
        if entry[3] is not None:
            for item in entry[3]:
                comments.append(item)
        
        row = table << pyh2.tr()
        
        row << pyh2.td(prefix) + pyh2.td(value)
        
        column = row << pyh2.td()
        
        if 0 < len(symbols):
            for symbol in symbols:
                column << symbol
                column << pyh2.br()
        
        column = row << pyh2.td()
        
        if 0 < len(comments):
            for comment in comments:
                column << comment
                column << pyh2.br()


def writeUnitTablesPage(dB, version, outFile):
    page = pyh2.PyH('UDUNITS2 Units and Symbols (ver. ' + version + ')')
    
    page.addCSS('https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css', 
                'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap-theme.min.css',
                'https://fonts.googleapis.com/css?family=Roboto:100,300',
                'https://fonts.googleapis.com/css?family=Open+Sans:300,400,600')
    page.addJS('https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js',
               'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js')
    
    styleSection = \
    '''
    <style>
        body
        {
            font-family: "Open Sans", Helvetica, sans-serif;
        }
        h1, h2, h3, h4, h5
        {
            font-family: Roboto, Helvetica, Arial, sans-serif;
            font-weight: 300;
            font-style: normal;
        }
        table
        {
            table-layout: fixed;
            word-wrap: break-word;
        }
        th
        {
            background-color: #888;
            color: #fff;
        }
        tr.selected
        {
            background-color: yellow;
        }
        .tabpanel { margin-top: 30px; }
    </style>
    '''
    
    page.head << styleSection
    
    divContainer = page << pyh2.div(**{'class' : 'container'})
    divRow       = divContainer << pyh2.div(**{'class' : 'row'})
    
    divRow << pyh2.h1('Units and Symbols Found in the UDUNITS2 Database')
    
    para = divRow << pyh2.p()
    
    para << 'The '
    para << pyh2.a('UDUNITS2', href = 'http://www.unidata.ucar.edu/software/udunits/')
    para << ' package provides recognition and conversion of wide variety of measurement units.' \
            ' This page contains a full list of all of the units and prefixes, by name and by symbol, contained' \
            ' in the UDUNIT2 units database. Each entry shows the definition of the unit or symbol and lists the' \
            ' other units and symbols that share that same definition.'
    
    para = divRow << pyh2.p()
    
    para << 'These tables are based on UDUNITS version ' + version
    
    filterForm = divRow << pyh2.form(**{'class' : 'form-inline', 'id' : 'filterForm'}) << pyh2.div(**{'class' : 'form-group'})
    filterForm << '\n<label for="filterInput">Filter</label>\n'
    
    filterForm << pyh2.select(id = 'filterType') << pyh2.option('begins with') + pyh2.option('contains') + pyh2.option('ends with')
    filterForm << pyh2.input(**{'id' : 'filterInput', 'type' : 'text', 'class' : 'form-control'})
    filterForm << pyh2.input(**{'id' : 'filterApply', 'type' : 'button', 'value' : 'Apply'})
    filterForm << pyh2.input(**{'id' : 'filterClear', 'type' : 'button', 'value' : 'Clear'})
    
    divRow = divContainer << pyh2.div(**{'class' : 'row'})
    
    divOuterTabPanel = divRow << pyh2.div(**{'class' : 'tabpanel', 'role' : 'tabpanel'})
    
    ulTabs = divOuterTabPanel << pyh2.ul(**{'class' : 'nav nav-tabs', 'role' : 'tablist', 'id' : 'myTabList'})
    
    liUnitsByName = ulTabs << pyh2.li(**{'role' : 'presentation', 'class' : 'active'})
    liUnitsByName << pyh2.a('Units by Name', **{'href' : '#UnitsByName', 'aria-controls' : 'UnitsByName', 'role' : 'tab', 'data-toggle' : 'tab'})
    
    liUnitsBySymbol = ulTabs << pyh2.li(role = 'presentation')
    liUnitsBySymbol << pyh2.a('Units by Symbol', **{'href' : '#UnitsBySymbol', 'aria-controls' : 'UnitsBySymbol', 'role' : 'tab', 'data-toggle' : 'tab'})
    
    liPrefixes = ulTabs << pyh2.li(role = 'presentation')
    liPrefixes << pyh2.a('Prefixes', **{'href' : '#Prefixes', 'aria-controls' : 'Prefixes', 'role' : 'tab', 'data-toggle' : 'tab'})
    
    divTabContent = divOuterTabPanel << pyh2.div(**{'class' : 'tab-content'})
    
    writeUnitsTable(dB, divTabContent)
    writeSymbolsTable(dB, divTabContent)
    writePrefixesTable(dB, divTabContent)
    
    scriptContents = \
    '''
    $(document).ready(function () {
        // Cache the outer tab panel, tab list, and the tables.
        //
        var filterForm    = $('#filterForm');
        var filterText    = $('#filterInput');
        var filterType    = $('#filterType');
        var outerTabPanel = $('#outerTabPanel');
        var tabList       = $('#tabList');
        var tables        = $('table');
        
        // Apply a filter when the 'Filter' button is clicked or the text box
        // loses focus. Clear the filter if the 'Clear' button is pressed.
        //
        filterForm.on('click change', 'input', function(e) {
            // Get the target item.
            //
            var theTarget = $(e.target);

            // Prevent the default behavior.
            //
            e.preventDefault();

            var theText = '';

            if (theTarget.attr('id') == 'filterInput' && e.type == 'change')
            {
                // A change event on the text box has been received. Set the
                // filter to the contents of the text box.
                //
                theText = filterText.val().trim();
            }
            else if (theTarget.attr('id') == 'filterApply' && e.type == 'click')
            {
                // A click event on the Apply button has been received. Set the
                // filter to the contents of the text box.
                //
                theText = filterText.val().trim();
            }
            else if (theTarget.attr('id') == 'filterClear' && e.type == 'click')
            {
                // A click event on the Clear button has been received. Set the
                // text box contentsand the filter to ''.
                //
                filterText.val('');

                theText = '';
            }
            else
            {
                // Nothing we care about happened, so return.
                //
                return;
            }

            // Make all rows visible.
            //
            $('tr').filter(':hidden').show();

            // If the filter text is empty, return.
            //
            if (0 == theText.length)
            {
                return;
            }

            // Get the filter type.
            //
            theType = filterType.val();

            // Create the filter based on the text and the type.
            //
            var theFilter;

            if ('begins with' == theType)
            {
                theFilter = new RegExp('\\\\b' + theText, 'i');
            }
            else if ('ends with' == theType)
            {
                theFilter = new RegExp(theText + '\\\\b', 'i');
            }
            else
            {
                theFilter = new RegExp(theText, 'i');
            }

            // Set all rows that don't have a first column matching the filter
            // to hidden.
            //
            $('tr').filter(function(index) {
                var colText = $(this).children('td:first-child').text().trim();

                if ('' == colText)
                {
                    return false;
                }

                return !theFilter.test(colText);
            }).hide();
        });

        // Activate the appropriate tab when a link is clicked and update the address bar.
        //
        tabList.on('click', 'a', function (e) {
            // Get the link.
            //
            var theTabLink = $(e.target);

            // Prevent the Default behavior.
            //
            e.preventDefault();

            // Send the tab bookmark hash to the address bar.
            //
            window.location.hash = theTabLink.attr('href');

            // Activate the clicked tab.
            //
            theTabLink.tab('show');
        });
        
        // Handle clicks in table links.
        //
        tables.on('click', 'a', function(e) {
            // Get the target link.
            //
            var target = $(e.target);
            
            // Prevent the default behavior.
            //
            e.preventDefault();
            
            // Get the target bookmark.
            //
            var href = target.attr('href');

            // Activate the tab that contains the target bookmark.
            //
            var tabId = $('a' + href).closest('div').attr('id');
            
            var theTabLink = $("a[href='#" + tabId + "']");

            theTabLink.tab('show')
            
            // Send the target bookmark hash to the address bar.
            //
            window.location.hash = href;

            // Go the the target table row and highlight it. Remove any existing
            // highlighting.
            //
            scroll_to_div(href, 50);
            $('tr').removeClass('selected');
            $(href).closest('tr').addClass('selected');
        });
        
        // Handle clicks in table cells.
        //
        tables.on('click', 'td', function(e) {
            // Get the target cell.
            //
            var target = $(e.target);

            if (!target.is('td'))
            {
                return;
            }
            
            // Prevent the default behavior.
            //
            e.preventDefault();
            
            // Remove all highlighted rows from the table.
            // If the row clicked in wasn't highlighted, highlight it.
            //
            if (target.closest('tr').hasClass('selected')) {
                $('tr').removeClass('selected');
            }
            else {
                $('tr').removeClass('selected');
                target.closest('tr').addClass('selected');
            }
        });
        
        // Show the tab based on the hash.
        //
        function refreshHash() {
            // Attempt to find the bookmark in the tab list.
            //
            tabLink = tabList.find('a[href="'+window.location.hash+'"]')

            // If the bookmark wasn't found, attempt to find it in the tables.
            //
            if (0 == tabLink.length) {
                var tabId = $('a' + href).closest('div').attr('id');
                
                tabLink = $("a[href='#" + tabId + "']");
            }
                
            // Activate the tab.
            //
            tabLink.tab('show');
        }

        // Scroll to the selected table location.
        //
        function scroll_to_div(selector, offset) {
            $("html,body").animate({ scrollTop: jQuery(selector).offset().top - offset }, 'slow');
        }
        
        // Show the tab if the hash changes in the address bar.
        //
        $(window).bind('hashchange', refreshHash);
        
        // Read the hash from the address bar and show it.
        //
        if (window.location.hash) {
            // show tab on load
            refreshHash();
        }
    });


    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

    ga('create', 'UA-15028616-4', 'auto');
    ga('send', 'pageview');
    '''
    
    page << pyh2.script(scriptContents)
    
    
    page.printOut(file = outFile)


def main():
    dB = GraphDatabase('http://localhost:7474/db/data/') 
    
    writeUnitTablesPage(dB, sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main() 
