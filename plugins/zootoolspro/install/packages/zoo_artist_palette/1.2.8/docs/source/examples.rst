Examples
########################################

===============================
Shelves
===============================

Shelves are built using a json file and python file.
The  json file is to design the layout of each shelf, what tools are displayed
their icons and if a shelf button contains a popup menu. 

The python files contain what we call ToolDefinitions these contain persistent
default settings for the shelf icons, labels etc but also contain python code 
to be executed when the button is triggered or any of the popup action are also
triggered.

These tooldefinitions also contain an Id class Variable which will be registered
as a plugin and will be referenced in the layout files.

Shelf layout file can be registry by either using an existing layout file 
or adding a new one and then appending the file path to the "ZOO_SHELF_LAYOUTS"
Environment Variable.

To add to the tooldefinitions this has the same behaviour as the layout path
but using the environment variable ZOO_TOOLDEFINITION_MODULES.


Simple Example of a layout file:
--------------------------------
.. code-block:: json

    {
        "id": "zoo.maya.curves.match",
        "type": "command",
        "displayLabel": false
        "icon": ""
        "varients": [],
        "arguments": {}
    }

Example using a popup Menu.
--------------------------------

.. code-block:: json

    {
    "id": "zoo.maya.connect.selection.localsrt",
    "type": "command",
    "displayLabel": false,
    "icon": "",
    "variants": [
        {
            "name": "Connect_srt",
            "label": "Connect SRT",
            "icon": "",
            "arguments": {
                "translate": true,
                "rotate": true,
                "scale": true
            }
        }
        ]
    }


Description of each key
--------------------------------

+---------------------+-------+----------------------------------------------------------+
|        Key          | Type  |                     Description                          |
+=====================+=======+==========================================================+
| id                  |  str  | the command or definition id specfied on the class       |
+---------------------+-------+----------------------------------------------------------+
| type                |  str  | The Type of tool, either command or tooldefinition       |
+---------------------+-------+----------------------------------------------------------+
| displayLabel        |  str  | The Ui label for the action                              |
+---------------------+-------+----------------------------------------------------------+
| icon                |  str  | The icon in the zootools library to use ie. "arrow"      |
+---------------------+-------+----------------------------------------------------------+
| varients            |  list | A list of dicts in the same form as above                |
+---------------------+-------+----------------------------------------------------------+
| arguments           |  dict | extra arguments to pass to the tooldefinition or command |
+---------------------+-------+----------------------------------------------------------+


===============================
Zoo Menu
===============================

Just like the shelf we use a layout json file and a tooldefinition file.
The tooldefinition can be the same as the shelf file that way we can share tools between
the shelf and the menu. While the Layout json file must be separate.
The layout file for the menu can be set using the ZOO_MENU_LAYOUTS environment variable.

.. code-block:: json

    {
        "menu": [
        {   "name": "General",
            "type": "menu",
            "children": [
                "zoo.renamer",
                "zoo.nodes.Aligner",
                "zoo.toolsets",
                "zoo.browserui"
            ]
        }
    ],
        "standalone": []
    }


Description of each key
--------------------------------

+---------------------+-------+----------------------------------------------------------------+
|        Key          | Type  |                     Description                                |
+=====================+=======+================================================================+
| menu                |  list | A list of dicts which  will have nested menus                  |
+---------------------+-------+----------------------------------------------------------------+
| type                |  str  | The Type of tool, current just supports "menu"                 |
+---------------------+-------+----------------------------------------------------------------+
| name                |  str  | The name for the menu, consider this the display label         |
+---------------------+-------+----------------------------------------------------------------+
| children            |  str  | A list of strings each containing the id of a tool definition  |
+---------------------+-------+----------------------------------------------------------------+
| standalone          |  list | A list of strings each containing the id of a tool definition  |
+---------------------+-------+----------------------------------------------------------------+
