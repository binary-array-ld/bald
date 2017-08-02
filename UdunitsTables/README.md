The two applications in this project create a web page that displays UDUNITS data in a set of tables.

INSTALLING
The first application, BuildUnitsGraph.py, parses the UDUNITS XML files that contain the definitions of units, their names, and their symbols and builds a graph database linking all the information together. The second application, WriteUnitsPage.py traverses the graph, creating an HTML file containing the information displayed in a group of tables on tabbed subpages.

The applications are built on Neo4j. You must install Neo4j and run the server in order for them to work. They both depend on the Python neo4jrestclient package. The WriteUnitsPage.py application also depends on the Python pyH2 package. Both Python packages are available via pip.

You can download Neo4j community edition for free from https://neo4j.com/download/community-edition/

You will need to disable authorization (at least temporarily) in Neo4j by setting the parameter dbms.security.auth_enabled=false in the .neo4j.conf file.

UDUNITS FILES
The UDUNITS-2 files can be obtained from github using the command:

    git clone https://github.com/Unidata/UDUNITS-2.git

The files of interest are:

    UDUNITS-2/lib/udunits2-accepted.xml
    UDUNITS-2/lib/udunits2-base.xml
    UDUNITS-2/lib/udunits2-common.xml
    UDUNITS-2/lib/udunits2-derived.xml
    UDUNITS-2/lib/udunits2-prefixes.xml

RUNNING
To run the applications, first start the Neo4j database engine. On a *nix system, run the command 'neo4j start'. On MacOS, run the Neo4j application and press the Start button. (I don't know how it works on Windows.)

To run the BuildUnitsGraph application:

    python BuildUnitsGraph.py UDUNITS-2/lib/udunits2-*.xml

To run the WriteUnitsPage application:

    python WriteUnitsPage.py <version> <HTML file name>

where <version> is the version of UDUNITS-2 to write into the text of the HTML file and <HTML file name> is the name of the HTML file to create.

![alt text](https://github.com/binary-array-ld/bald/tree/master/UdunitsTables/graph.png "View of graph built from UDUNITS-2 2.2.25.")
