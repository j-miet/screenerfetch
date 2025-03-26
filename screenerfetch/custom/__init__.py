"""All custom command packages.

Each should implement their own commands, importantly workbook creation, and set base values for settings files
if commands require specific settings.json values.

Remember to:  
-add workbook create command under run._custom_create, and  
-add command to enter its custom command interface under run._select_custom_package  
    -->see small_cap1.c_commands.select_custom_command() for an example - this opens a sub-interface similar to main 
    interface.  
-add package import under run.py 

Custom script commands should be added under run_script.py.
"""