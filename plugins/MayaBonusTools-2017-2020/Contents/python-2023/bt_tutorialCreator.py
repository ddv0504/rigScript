#Interactive Tutorial Creator app by Matthew Chan

"""
Use this tool to create interactive tutorials through an easy-to-use user interface.  With it, you can create steps, edit and place text, automate actions 
(via python code), and monitor for specific trigger events.  The app will handle creating and connecting the appropriate nodes behind the scene for you.

To use this tool:
    1.) Open the Bonus Tools.
    2.) Click "Interactive Tutorial Creator App".
    
You can also manually run this script by loading it into a Python tab in the Script Editor and executing the runTutorialCreator() procedure.

The Tutorial Creator window is divided into a number of sections.  Clockwise from top-left they are:
1.	New Step button – Click this to add a step to the tutorial.  When creating a step, you can also specify where the step should go (default to the end of the current set of steps, but you can also choose to insert a step between existing ones), as well as what components a step should include (text, triggers, etc).  Don’t worry, you can always add more components after you’ve created a step (see “Step Components” below).
2.	Play buttons – Click the appropriate play button to start the tutorial from the beginning, or from a specific selected step in the Node List (see 4).
3.	Editor Panel – This is where you can customize the behavior of the tutorial.  The Editor Panel will change depending on the node you have selected in the Node List (see 4).
4.	Node List – Displays a list of all relevant tutorial nodes connected to Stage0 (the start of your tutorial).  You can select nodes in here to manipulate their behavior via the Editor Panel (see 3).  You can also rename or delete nodes via the two buttons under the Node List.  
•	Stage nodes represent each step of the tutorial.  Options for stage nodes include: adding a new component (see Step Components), auto-playing the Time Slider when a step begins, moving to the next step when the animation finishes or immediately or after a certain time delay, and creating / linking a Time Slider Bookmark to the step to immediately jump to that frame range when the step begins. 
•	Step Components are indented under stage nodes and represent the support nodes that determine what happens at each step (see Step Components below).

Step Components
For each stage node in your tutorial, you may have an arbitrary number of step components associated with it.  The four types of step components are:
1.	Text Overlay: Display and position text on screen.  This can take the form of either a non-interactable word bubble, or a fully movable dialog box.
2.	Controller Update: Update the tutorial controller.  Updates may include changing the text, locking buttons, or incrementing the step counter.
3.	Stage Setup: automate things to happen in Maya before a step begins.  For example, you may want to show or hide the Attribute Editor or Channel box, change the current active camera, or even execute entire Python strings for more complex setup automations.
4.	Trigger: Define a trigger to execute code when a specific event occurs.  The default setting will move the tutorial to the next step, but you can customize the behavior to do whatever you want.  For example, you may want to monitor for the user to select a specific tool, then display some additional text.

Additional Options
In the Tutorial Creator windows menu bar, you will find some additional options.  These are:
•	Jump to selected stage time: Enable this if you want Maya to automatically set the Time Slider range to appropriate Time Slider bookmark when you select nodes in the Node List.  Note: If you select a stage (or step component) without an accompanying bookmark, then Maya will jump to the nearest applicable bookmark from the stages before the selected one.
•	Jump to selected stage camera: Enable this if you want Maya to automatically set the current camera to that of the selected stage (or step component) when you select nodes in the Node List.
•	Source text from dictionary: Allows you to bypass the “text_overlay” or “update_controller” components and instead source text from a single dictionary script node (populateText).  This is mostly useful if you want to centralize the text for localization purposes.
•	Show in Node Editor: Select this to show the tutorial nodes in Maya’s Node Editor.  Useful for advanced manipulation of the nodes.
•	Show in Expression Editor: Select this to display the Step Components in the Expression Editor.  Useful for advanced manipulation of the Python scripts.
•	Utilities: Several miscellaneous tools that you may find useful when creating tutorials, including: Showing your current selection, showing a list of contexts, and merging text from the “text_overlay” and “update_controller” nodes to the aforementioned dictionary script node (populateText).  There are also options to export a json file for localization, as well as importing the translations to alternate languages of the tutorial and overriding the current Maya language (for testing localized scripts).


"""

from functools import partial
import maya.cmds as cmds
import maya.mel
import time
import moverlay as mo
from PySide2.QtCore import QSize, QPoint
from PySide2.QtGui import QColor
from PySide2 import QtWidgets

#Inject python data into the appropriate script node when editing an existing stage template
def injectData(*args):
    selected_node = args[0]
    selected_type = cmds.getAttr(selected_node+".before").split("%NODETYPEID%")[1]
    parsed_input_list = cmds.getAttr(selected_node+".before").split('#%INPUT%')
    reassembled_input = ""       
    
    menu_mode_UI = "StatusLine|MainStatusLineLayout|formLayout4|flowLayout1|optionMenuForm|menuMode"
    
    #if we're injecting a new name
    if args[1][0] == 0:
        parsed_input_list = cmds.getAttr(selected_node+".before").split('#%THISID%')
        parsed_input_list[1] = '\nthis = "'+selected_node+'"\n'
        
        for x in parsed_input_list[:-1]:
            reassembled_input = reassembled_input + x + '#%THISID%'
        reassembled_input = reassembled_input + parsed_input_list[len(parsed_input_list)-1]
        
    #Else we're injecting some other data
    else:
        if selected_type == "initialize":
            for x in args[1]:
                if x == 1:
                    if cmds.checkBoxGrp("UI_vis", q=True, v1=True):
                        parsed_input_list[1] = '\nis_ae_visible = True\n'
                    else:
                        parsed_input_list[1] = '\nis_ae_visible = False\n'   
                elif x == 3:
                    if cmds.checkBoxGrp("UI_vis", q=True, v2=True):
                        parsed_input_list[3] = '\nis_cb_visible = True\n'
                    else:
                        parsed_input_list[3] = '\nis_cb_visible = False\n'  
                elif x == 5:
                    if cmds.checkBoxGrp("UI_vis", q=True, v3=True):
                        parsed_input_list[5] = '\nis_outliner_visible = True\n'
                    else:
                        parsed_input_list[5] = '\nis_outliner_visible = False\n'  
                elif x == 7:
                    if cmds.checkBoxGrp("UI_vis", q=True, v4=True):
                        parsed_input_list[7] = '\nis_mtk_visible = True\n'
                    else:
                        parsed_input_list[7] = '\nis_mtk_visible = False\n'  
                elif x == 9:
                    parsed_input_list[9] = "\ndefault_speech_style = '"+'"'+cmds.textField("default_speech_style", q=True, text=True)+'"'+"'\n"
                    cmds.setAttr("controller.speech_html_style", cmds.textField("default_speech_style", q=True, text=True), type="string")
                elif x == 11:
                    parsed_input_list[11] = "\ndefault_dialog_style = '"+'"'+cmds.textField("default_dialog_style", q=True, text=True)+'"'+"'\n"
                    cmds.setAttr("controller.reference_html_style", cmds.textField("default_dialog_style", q=True, text=True), type="string")
                elif x == 13:
                    parsed_input_list[13] = "\ndefault_control_style = '"+'"'+cmds.textField("default_controller_style", q=True, text=True)+'"'+"'\n"
                    cmds.setAttr("controller.instruct_html_style", cmds.textField("default_controller_style", q=True, text=True), type="string")
                elif x == 15:
                    parsed_input_list[15] = '\nshot_camera = "'+cmds.optionMenu("initial_shot_camera", q=True, v=True)+'"\n'
                elif x == 17:
                    parsed_input_list[17] = '\nmenu_set = '+str(cmds.optionMenu("menu_mode", q=True, sl=True))+'\n'
                elif x == 19:
                    parsed_input_list[19] = '\ntool_ctx = "'+cmds.optionMenu("tool_ctx", q=True, v=True)+'"\n'
                elif x == 21:
                    parsed_input_list[21] = '\n'+cmds.scrollField("initial_setup_code", q=True, text=True)+'\n'
                    parsed_input_list[21] = parsed_input_list[21].replace("    ", "\t")
            clearAllPreviews()
            
        elif selected_type == "stage_setup":
            for x in args[1]:
                if x == 1:
                    if cmds.checkBoxGrp("UI_vis", q=True, v1=True):
                        parsed_input_list[1] = '\nis_ae_visible = True\n'
                    else:
                        parsed_input_list[1] = '\nis_ae_visible = False\n'   
                elif x == 3:
                    if cmds.checkBoxGrp("UI_vis", q=True, v2=True):
                        parsed_input_list[3] = '\nis_cb_visible = True\n'
                    else:
                        parsed_input_list[3] = '\nis_cb_visible = False\n'  
                elif x == 5:
                    if cmds.checkBoxGrp("UI_vis", q=True, v3=True):
                        parsed_input_list[5] = '\nis_outliner_visible = True\n'
                    else:
                        parsed_input_list[5] = '\nis_outliner_visible = False\n'  
                elif x == 7:
                    if cmds.checkBoxGrp("UI_vis", q=True, v4=True):
                        parsed_input_list[7] = '\nis_mtk_visible = True\n'
                    else:
                        parsed_input_list[7] = '\nis_mtk_visible = False\n'  
                elif x == 9:
                    parsed_input_list[9] = '\nmenu_set = "'+cmds.optionMenu("menu_mode", q=True, sl=True)+'"\n'
                elif x == 11:
                    parsed_input_list[11] = '\ntool_ctx = "'+cmds.optionMenu("tool_ctx", q=True, v=True)+'"\n'
                elif x == 13:
                    parsed_input_list[13] = '\nshot_camera = "'+cmds.optionMenu("setup_shot_camera", q=True, v=True)+'"\n'
                elif x == 15:
                    reset_step_code = '\n'+cmds.scrollField("setup_reset_code", q=True, text=True)
                    reset_step_code = reset_step_code.replace("    ", "\t")
                    reset_step_code = reset_step_code.replace("\n", "\n\t")
                    parsed_input_list[15] = reset_step_code+'\n'
                elif x == 17:
                    parsed_input_list[17] = '\n'+cmds.scrollField("setup_code", q=True, text=True)+'\n'
                    parsed_input_list[17] = parsed_input_list[17].replace("    ", "\t")

            
            clearAllPreviews()
                                       
        elif selected_type == "text_overlay":
            for x in args[1]:
                if x == 1:
                    if cmds.getAttr("controller.use_dictionary"):
                        dictionaryModeWarning()
                        
                    parsed_input_list[1] = '\nhtml_text = """'+cmds.textField("text_overlay_html_text", q=True, text=True)+'"""\n'
                elif x == 3:
                    if cmds.optionMenu("text_overlay_is_offset_absolute", q=True, sl=True) == 1:
                        parsed_input_list[3] = "\nis_offset_absolute = True\n"
                        cmds.optionMenu("text_overlay_rel_to", e=True, enable=True)
                    else:
                        parsed_input_list[3] = "\nis_offset_absolute = False\n"
                        cmds.optionMenu("text_overlay_rel_to", e=True, sl=1, enable=False)
                elif x == 5:
                    parsed_input_list[5] = "\nx_offset = "+str(cmds.intFieldGrp("text_overlay_xy_offset", q=True, v1=True))+"\n"
                elif x == 7:    
                    parsed_input_list[7] = "\ny_offset = "+str(cmds.intFieldGrp("text_overlay_xy_offset", q=True, v2=True))+"\n"
                elif x == 9:
                    if cmds.optionMenu("text_overlay_rel_to", q=True, sl=True) == 10:
                        cmds.textField("text_overlay_rel_to_custom", e=True, enable=True)
                        parsed_input_list[9] = '\nrel_to = "'+cmds.textField("text_overlay_rel_to_custom", q=True, text=True)+'"\n'   
                    else:
                        parsed_input_list[9] = '\nrel_to = "'+str(cmds.optionMenu("text_overlay_rel_to", q=True, v=True))+'"\n'
                        cmds.textField("text_overlay_rel_to_custom", e=True, enable=False)
                elif x == 11:
                    parsed_input_list[11] = '\ntail_orientation = "'+str(cmds.optionMenu("text_overlay_tail_dir", q=True, v=True))+'"\n'
                elif x == 13:
                    parsed_input_list[13] = '\ntail_position = '+str(cmds.floatSliderGrp("text_overlay_tail_pos", q=True, v=True))+'\n'
                elif x == 15:
                    parsed_input_list[15] = '\noverlay_width = '+str(cmds.intField("text_overlay_width", q=True, v=True))+'\n'          
                elif x == 17:
                    if cmds.checkBox("text_overlay_dialog_style", q=True, v=True):
                        cmds.optionMenu("text_overlay_is_offset_absolute", e=True, sl=2)
                        cmds.optionMenu("text_overlay_is_offset_absolute", e=True, enable=False)
                        cmds.optionMenu("text_overlay_rel_to", e=True, sl=1, enable=False)
                        cmds.floatSliderGrp("text_overlay_tail_pos", e=True, enable=False)
                        cmds.optionMenu("text_overlay_tail_dir", e=True, enable=False)
                    else:
                        cmds.optionMenu("text_overlay_is_offset_absolute", e=True, enable=True)
                        cmds.optionMenu("text_overlay_rel_to", e=True, enable=True)
                        cmds.floatSliderGrp("text_overlay_tail_pos", e=True, enable=True)
                        cmds.optionMenu("text_overlay_tail_dir", e=True, enable=True)
                
                    parsed_input_list[17] = '\ndialog_style = '+str(cmds.checkBox("text_overlay_dialog_style", q=True, v=True))+'\n' 
                    injectData(selected_node, [3])
                    
            clearAllPreviews()
            displayPreviewOverlay(selected_node)

        elif selected_type == "update_controller":
            deletePreviewController()
            for x in args[1]:
                if x == 1:
                    if cmds.getAttr("controller.use_dictionary"):
                        dictionaryModeWarning()
                                
                    parsed_input_list[1] = '\ntitle = """'+cmds.textField("update_controller_title", q=True, text=True)+'"""\n'
                elif x == 3:
                    if cmds.getAttr("controller.use_dictionary"):
                        dictionaryModeWarning()
                        
                    parsed_input_list[3] = '\ndescription = """'+cmds.scrollField("update_controller_description", q=True, text=True)+'"""\n'
                elif x == 5:
                    if cmds.getAttr("controller.use_dictionary"):
                        dictionaryModeWarning()
                        
                    parsed_input_list[5] = '\nbutton0 = "'+cmds.textField("update_controller_left_button", q=True, text=True)+'"\n'
                elif x == 7:
                    if cmds.getAttr("controller.use_dictionary"):
                        dictionaryModeWarning()
                        
                    parsed_input_list[7] = '\nbutton1 = "'+cmds.textField("update_controller_right_button", q=True, text=True)+'"\n'        
                elif x == 9:
                    parsed_input_list[9] = '\ndisable_reset = '+str(cmds.checkBox("update_controller_disable_reset", q=True, v=True))+'\n'
                elif x == 11:
                    parsed_input_list[11] = '\ndisable_next = '+str(cmds.checkBox("update_controller_disable_next", q=True, v=True))+'\n'    
                elif x == 13:
                    parsed_input_list[13] = '\nincrement_step = '+str(cmds.checkBox("update_controller_increment_step", q=True, v=True))+'\n'
                elif x == 15:
                    parsed_input_list[15] = '\nx_offset = '+str(cmds.intFieldGrp("controller_xy_offset", q=True, v1=True))+'\n'
                elif x == 17:
                    parsed_input_list[17] = '\ny_offset = '+str(cmds.intFieldGrp("controller_xy_offset", q=True, v2=True))+'\n'
                   
            clearAllPreviews()
            displayPreviewController()
        
        elif selected_type == "trigger":
            trigger_change = False
            for x in args[1]:    
                
                if x == 1:
                    parsed_input_list[1] = '\ntrigger_type = "'+cmds.optionMenu("trigger_type", q=True, v=True)+'"\n'
                    buildDynamicTriggerUI(selected_node, parsed_input_list)
                    
                elif x == 3:
                    
                    if cmds.optionMenu("trigger_type", q=True, v=True) == "Attribute Change" or cmds.optionMenu("trigger_type", q=True, v=True) == "Connection Change":
                        parsed_input_list[3] = '\ntrigger_ID = "'+cmds.textField("trigger_ID", q=True, text=True)+'"\n'
                    else:
                        parsed_input_list[3] = '\ntrigger_ID = "'+cmds.optionMenu("trigger_ID", q=True, v=True)+'"\n'
                elif x == 5:
                    trigger_code = cmds.scrollField("trigger_code", q=True, text=True)
                    trigger_code = trigger_code.replace("    ", "\t")
                    trigger_code = trigger_code.replace("\n", "\n\t")
                    parsed_input_list[5] = "\n\t"+trigger_code+"\n"

            clearAllPreviews()      
             
        for x in parsed_input_list[:-1]:
            reassembled_input = reassembled_input + x + '#%INPUT%'
        reassembled_input = reassembled_input + parsed_input_list[len(parsed_input_list)-1]
    
    cmds.setAttr(selected_node+".before", reassembled_input, type="string")

#Warn users when the tutorial is in "use_dictionary" mode and the user tries to change text values in the tutorial app.
def dictionaryModeWarning():
    
    def closeDMWarning(*args):
        if cmds.window("dm_window", exists=True):
            cmds.deleteUI("dm_window") 
    
    def disableDictionary(*args):
        cmds.setAttr("controller.use_dictionary", False)
        closeDMWarning()
        
    if cmds.window("dm_window", exists=True):
        cmds.deleteUI("dm_window")    

    dm_window = cmds.window ("dm_window", title="Warning", sizeable=True, widthHeight=(100, 100))
    cmds.columnLayout("dm_main", columnAlign = "left", rs=5, parent=dm_window)
    cmds.text("override_lang_text", label = "\nThe changes you are about to make won't be visible in the tutorial\nunless you disable Use Dictionary Mode.  \n\nWould you like to do that now?\n", parent="dm_main")
    cmds.rowLayout("dm_buttons", parent="dm_main", numberOfColumns=2)
    cmds.button ("dm_yes", label = "Yes", parent="dm_buttons", width=50, command=disableDictionary)
    cmds.button ("dm_no", label = "No", parent="dm_buttons", width=50, command=closeDMWarning)
    cmds.text("dm_spacer", label="", parent="dm_main")
    cmds.showWindow( dm_window )

#Removes all preview objects from the screen
def clearAllPreviews(*args):
    cmds.scriptNode("clearOverlays", eb=True)
    cmds.scriptNode("clearDialogs", eb=True)
    deletePreviewController()  

#Display a preview of the step's overlay if a text_overlay node is selected
def displayPreviewOverlay(*args):
    import sys, imp
    from PySide2.QtCore import QSize
    from PySide2.QtGui import QColor
    
    selected_node = args[0]

    html_text =  cmds.textField("text_overlay_html_text", q=True, text=True)    
    
    is_offset_absolute = True
    if cmds.optionMenu("text_overlay_is_offset_absolute", q=True, sl=True) != 1:
        is_offset_absolute = False
    
    x_offset = cmds.intFieldGrp("text_overlay_xy_offset", q=True, v1=True)
    y_offset = cmds.intFieldGrp("text_overlay_xy_offset", q=True, v2=True)
    
    rel_to = cmds.optionMenu("text_overlay_rel_to", q=True, v=True)

    if rel_to == "UI code":
        rel_to = cmds.textField("text_overlay_rel_to_custom", q=True, text=True)
    
    tail_orientation = cmds.optionMenu("text_overlay_tail_dir", q=True, v=True)

    tail_position = cmds.floatSliderGrp("text_overlay_tail_pos", q=True, v=True)

    overlay_width = cmds.intField("text_overlay_width", q=True, v=True)

    dialog_style = cmds.checkBox("text_overlay_dialog_style", q=True, v=True)
    
    #set and apply initial style to text
    style=""
    if not dialog_style:
    	style = cmds.getAttr("controller.speech_html_style")
    else:
    	style = cmds.getAttr("controller.reference_html_style")
    text="<span style = "+style+" >"+html_text+"</span>"
    
    con_browse = QPoint(0, 0)
    UI_success = False
    cardinal_points = ["topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright"]
    
    #check if the user has indicated a valid UI component to place the overlay relative to
    if not rel_to in cardinal_points:
        try:
    	    con_browse=mo.getUIPosition(rel_to)
    	    UI_success = True
        except:
    	    print (rel_to+" not found!")
    
    #if user has specified a valid part of the UI to place relative to
    if (UI_success):
        x_offset = con_browse.x()+x_offset
        y_offset = con_browse.y()+y_offset
    
    manager = mo.maya.overlayManager()
    #run the appropriate script to display the chosen overlay style
    if not dialog_style:
        
        #if user is defining position by main window %age rather than absolute 
        if not is_offset_absolute:
        	percent_to_pos = manager.getMainWindow().mapToGlobal(mo.coordinateFromPercentage(x_offset, y_offset))
        	x_offset = percent_to_pos.x()
        	y_offset = percent_to_pos.y()
        

        offset = QSize(mo.utils.DPIScale(x_offset), mo.utils.DPIScale(y_offset))

        #position the dialog box
        od = mo.overlayDef.OverlayDef(offset=offset)
       
        #get/set UI relative reference point for bubble positioning
        if (rel_to == "center"):
        	od.attachment = mo.enums.RelTo.Center
        elif (rel_to == "topleft" or not is_offset_absolute):
        	od.attachment = mo.enums.RelTo.TopLeft
        elif (rel_to == "left"):
        	od.attachment = mo.enums.RelTo.Left
        elif (rel_to == "bottomleft"):
        	od.attachment = mo.enums.RelTo.BottomLeft
        elif (rel_to == "top"):
        	od.attachment = mo.enums.RelTo.Top
        elif (rel_to == "topright"):
        	od.attachment = mo.enums.RelTo.TopRight
        elif (rel_to == "right"):
        	od.attachment = mo.enums.RelTo.Right
        elif (rel_to == "bottomright"):
        	od.attachment = mo.enums.RelTo.BottomRight
        elif (rel_to == "bottom"):
        	od.attachment = mo.enums.RelTo.Bottom
       
        #set bubble BG color
        od.bgColor = QColor(217, 217, 217, 255)
        
        #get/set the overlay style

        od.style = mo.enums.OverlayStyle.SpeechBubble
        od.bgColor = QColor(217, 217, 217, 255)

        #populate bubble with text
        overlay = manager.createOverlay(od)
        
        label=overlay.setAsLabel(text)
        
        #determine if bubble needs to be wrapped (i.e. too big)
        label.setWordWrap(False)
        overlay_width_scaled = mo.utils.DPIScale(overlay_width)
        if label.sizeHint().width() > overlay_width_scaled:
            label.setWordWrap(True)
            label.setFixedWidth(overlay_width_scaled)
        else:
            label.setWordWrap(False)
        
        #add the tail 
        if(tail_orientation == "top"):
            overlay.addSpeechBubbleTail(mo.enums.Direction.Top, tail_position)
        elif(tail_orientation == "left"):
            overlay.addSpeechBubbleTail(mo.enums.Direction.Left, tail_position)
        elif(tail_orientation == "bottom"):
            overlay.addSpeechBubbleTail(mo.enums.Direction.Bottom, tail_position)
        else:
            overlay.addSpeechBubbleTail(mo.enums.Direction.Right, tail_position)
    
        #display the overlay bubble
        manager.showAll()
    else:
        #destroy the dialog box when the X button is pushed
        def pressClosed(dialog):
        	dialog.theDialog().deleteLater()

        dialog = mo.higDialog.HIGDialog(manager.getMainWindow())
        hinDropShadow = mo.higDropShadow.HIGDropShadow(manager.getMainWindow(), dialog)
        
        #Add the dialog to the global list of dialog boxes
        mo.dialog_list.append(dialog)
        
        tl = cmds.internalVar(mid=True)
        tl = tl+"/resources/tutorial_resources/"
        
        label = dialog.setAsLabel(text)
        #label.setMaximumWidth(mo.utils.DPIScale(100))
        dialog.setCloseCallback(pressClosed)
        
        #dialog.theDialog().setMaximumWidth(mo.utils.DPIScale(100))
        
        #position the dialog box
        if not is_offset_absolute:
        	dialog.theDialog().moveToScreenPos(manager.getMainWindow().mapToGlobal(mo.coordinateFromPercentage(x_offset, y_offset)))
        else:
        	dialog.theDialog().moveToScreenPos(manager.getMainWindow().mapToGlobal(QPoint(mo.utils.DPIScale(x_offset), mo.utils.DPIScale(y_offset))))
        
        dialog.showAndRaise()
    

def deletePreviewController(*args):
    try:
        mo.g_overlay_manager.controller.close()
    except:
        pass

#Display a non-functional version of the controller at the selected step
def displayPreviewController(*args):
    
    def pressClosed(dialog):
        deletePreviewController()
        
    mo.g_overlay_manager = mo.maya.overlayManager()
    mo.g_overlay_manager.controller = mo.progressDialog.ProgressDialog(mo.g_overlay_manager.getMainWindow())
    dropShadow = mo.higDropShadow.HIGDropShadow(mo.g_overlay_manager.getMainWindow(), mo.g_overlay_manager.controller)
    
    style = cmds.getAttr("controller.instruct_html_style")
    title = "<p style = "+style+" ><h3>"+cmds.textField("update_controller_title", q=True, text=True)+"</h3></p>"
    description = "<p style = "+style+" >"+cmds.scrollField("update_controller_description", q=True, text=True)+"</p>"
    mo.g_overlay_manager.controller.setTitle(title)
    mo.g_overlay_manager.controller.setBodyText(description)
    button0 = cmds.textField("update_controller_left_button", q=True, text=True)
    button1 = cmds.textField("update_controller_right_button", q=True, text=True)
    mo.g_overlay_manager.controller.button(0).setText(button0)
    mo.g_overlay_manager.controller.button(1).setText(button1)
    
    disable_restart = cmds.checkBox("update_controller_disable_reset", q=True, v=True)
    disable_next = cmds.checkBox("update_controller_disable_next", q=True, v=True)
    
    if disable_restart:
        mo.g_overlay_manager.controller.button(0).setEnabled(False)
        mo.g_overlay_manager.controller.button(0).setVisible(False)
    else:
        mo.g_overlay_manager.controller.button(0).setEnabled(True)
        mo.g_overlay_manager.controller.button(0).setVisible(True)
    
    if disable_next:
        mo.g_overlay_manager.controller.button(1).setEnabled(False)
    else:
        mo.g_overlay_manager.controller.button(1).setEnabled(True)
    
    mo.g_overlay_manager.controller.setCloseCallback(pressClosed)
    num_steps = len(cmds.ls(type="stage"))-2
    mo.g_overlay_manager.controller.progressBar().resetSteps(0, num_steps)
    
    xy_offset = cmds.intFieldGrp("controller_xy_offset", q=True, v=True)
    
    mo.g_overlay_manager.controller.theDialog().resize(mo.utils.DPIScale(180), mo.utils.DPIScale(250))
    mo.g_overlay_manager.controller.theDialog().moveToScreenPos(mo.g_overlay_manager.getMainWindow().mapToGlobal(mo.coordinateFromPercentage(xy_offset[0], xy_offset[1])))
    
    #refresh the controller
    mo.g_overlay_manager.controller.showAndRaise()


#scriptjob that waits until the "Create new Time Slider Bookmark" options window is closed, then connects that bookmark to the current stage
def tsCreate(old_bookmark_list, selected_node, old_connected_bookmark):
    bookmark_list = cmds.ls(type="timeSliderBookmark")
    new_bookmarks = set(old_bookmark_list) ^ set(bookmark_list)
    new_connected_bookmark = cmds.listConnections(selected_node+".timeSliderBookmark")
 
    if new_bookmarks:
        latest_bookmark = list(new_bookmarks)
        if new_connected_bookmark != latest_bookmark:
            set1=cmds.ls("GRAPH_MY_CHILDREN")[0]
            cmds.sets(latest_bookmark[0], e=True, addElement=set1)
            new_bookmark_name = cmds.getAttr(latest_bookmark[0]+".name")
            cmds.connectAttr(latest_bookmark[0]+".name", selected_node+".timeSliderBookmark", force=True)
            cmds.menuItem(new_bookmark_name, parent="tc_window|main|section_edit|UI_edit_pane_main|UI_edit_pane|time_slider_bookmark_list")
            cmds.optionMenu("tc_window|main|section_edit|UI_edit_pane_main|UI_edit_pane|time_slider_bookmark_list", e=True, v=new_bookmark_name)
            
            if cmds.lsUI("step_range_text"):
                cmds.deleteUI("step_range_text")
            if cmds.lsUI("step_frame_range"):
                cmds.deleteUI("step_frame_range")

            cmds.text("step_range_text", label="Step Frame Range ", parent="UI_edit_pane")
            cmds.intFieldGrp("step_frame_range", parent="UI_edit_pane", numberOfFields = 2, v1=cmds.getAttr(latest_bookmark[0]+".timeRangeStart"), v2=cmds.getAttr(latest_bookmark[0]+".timeRangeStop"))
            setPlaybackRange()


#Add a new bookmark via the "Create new Time Slider Bookmark" window 
def newBookmark(*args):
    selected_node = args[0]
    bookmark_list = cmds.ls(type="timeSliderBookmark")
    current_bookmark = cmds.listConnections(selected_node+".timeSliderBookmark")
    cmds.CreateTimeSliderBookmark()
    job_num=cmds.scriptJob( event = ["idle", partial(tsCreate, bookmark_list, selected_node, current_bookmark)])
    mo.listener_list.append(job_num) 

def setPlaybackRange(*args):
    min = cmds.intFieldGrp("step_frame_range", q=True, v1=True)
    max = cmds.intFieldGrp("step_frame_range", q=True, v2=True)
    cmds.playbackOptions(min=min, max=max)
    cmds.currentTime(max)
    
#Connect a time slider bookmark to the stage
def connectTimeSliderBookmark(*args):

    selected_node = args[0]
    bookmark_name = cmds.optionMenu("tc_window|main|section_edit|UI_edit_pane_main|UI_edit_pane|time_slider_bookmark_list", q=True, v=True)
    bookmark_list = cmds.ls(type="timeSliderBookmark")
    
    bookmark_ID=""
    for x in bookmark_list:
        if cmds.getAttr(x+".name") == bookmark_name:
            bookmark_ID = x

    current_bookmark = cmds.listConnections(selected_node+".timeSliderBookmark")
    
    if bookmark_name == "None":
        if current_bookmark:
            cmds.disconnectAttr(current_bookmark[0]+".name", selected_node+".timeSliderBookmark")        
    else:
        cmds.connectAttr(bookmark_ID+".name", selected_node+".timeSliderBookmark", force=True)
            
    buildEditPane()

#Update a connected time slider bookmark with the values in the edit pane    
def updateTimeSliderBookmark(*args):
    selected_node = args[0]
    current_bookmark = cmds.listConnections(selected_node+".timeSliderBookmark")[0]
    cmds.setAttr(current_bookmark+".timeRangeStart", cmds.intFieldGrp("step_frame_range", q=True, v1=True))
    cmds.setAttr(current_bookmark+".timeRangeStop", cmds.intFieldGrp("step_frame_range", q=True, v2=True))  

#Rebuild the trigger UI specifically when the trigger-type changes.  We cannot just refresh the UI using "buildEditPane" because it causes an infinite loop
def buildDynamicTriggerUI(*args):
     
    #clear the previous dynamic contents of the pane
    dynamic_UI_elements = ["attribute_name", "trigger_ID", "condition_ID", "event_ID", "trigger_ID_row", "trigger_help", "trigger_code_text", "trigger_code", "trigger_code_layout", "trigger_code_help_spacer", "trigger_help_spacer2", "trigger_help_button"]
    for x in dynamic_UI_elements:
        try:
            cmds.deleteUI(x)
        except:
            pass
        
    selected_node = args[0]
    parsed_input_list = args[1]

    #3 Trigger ID

    trigger_type = parsed_input_list[1].split('\ntrigger_type = "')[1][:-2]
    trigger_ID = parsed_input_list[3].split('\ntrigger_ID = "')[1][:-2]
    
    if trigger_type == "Attribute Change":
        cmds.text("attribute_name", label = "Attribute Name(s)\n(Separate multiple\nwith commas) ", parent="UI_edit_pane")
        cmds.textField("trigger_ID", parent = "UI_edit_pane", text=trigger_ID, cc=partial(injectData, selected_node, [3]))
    elif trigger_type == "Connection Change":
        cmds.text("attribute_name", label = "Attribute Name(s)\n(Separate multiple\nwith commas) ", parent="UI_edit_pane")
        cmds.textField("trigger_ID", parent = "UI_edit_pane", text=trigger_ID, cc=partial(injectData, selected_node, [3]))
    elif trigger_type == "Condition":
        condition_list = sorted(cmds.scriptJob(lc=True))    
        cmds.text("condition_ID", label = "Condition ID ", parent="UI_edit_pane")
        cmds.rowLayout("trigger_ID_row", parent = "UI_edit_pane", numberOfColumns=2)
        cmds.optionMenu("trigger_ID", parent = "trigger_ID_row", cc=partial(injectData, selected_node, [3]))  
        for x in condition_list:
            cmds.menuItem(x)
        try:
            cmds.optionMenu("trigger_ID", e=True, v=trigger_ID)
        except:
            pass
        cmds.button("trigger_help", label = "?", width = 25, parent = "trigger_ID_row", command = 'cmds.showHelp("https://help.autodesk.com/cloudhelp/2022/ENU/Maya-Tech-Docs/CommandsPython/scriptJob.html#flaglistConditions", absolute = True)')
    else:
        event_list = sorted(cmds.scriptJob(le=True))
        cmds.text("event_ID", label = "Event ID ", parent="UI_edit_pane")
        cmds.rowLayout("trigger_ID_row", parent = "UI_edit_pane", numberOfColumns=2)
        cmds.optionMenu("trigger_ID", parent = "trigger_ID_row", cc=partial(injectData, selected_node, [3]))  
        for x in event_list:
            cmds.menuItem(x)
        try:
            cmds.optionMenu("trigger_ID", e=True, v=trigger_ID)
        except:
            pass
        cmds.button("trigger_help", label = "?", width = 25, parent = "trigger_ID_row", command = 'cmds.showHelp("https://help.autodesk.com/cloudhelp/2022/ENU/Maya-Tech-Docs/CommandsPython/scriptJob.html#flaglistEvents", absolute = True)')
        
    #5 Trigger code
    trigger_code_lines = parsed_input_list[5].split("\n")
    trigger_code=""
    
    count = 2
    #strip out first indentation on each line
    for x in trigger_code_lines[1:]:
        trigger_code = trigger_code+x.replace("\t", "", 1)
        if count == len(trigger_code_lines)-1:
            break
        else:
            trigger_code = trigger_code+"\n"
            count = count+1
    
    cmds.columnLayout("trigger_code_layout", parent="UI_edit_pane")
    cmds.text("trigger_code_text", label = "\n\n\n\n\nTrigger Instructions \n(Python code) ", parent="trigger_code_layout")
    cmds.text("trigger_help_spacer", label = "", parent="trigger_code_layout")
    cmds.rowLayout("trigger_help_layout", parent="trigger_code_layout", numberOfColumns = 3, columnAlign1 = "center", ct1="both")
    cmds.text("trigger_help_spacer2", label = "            ", parent="trigger_help_layout")
    cmds.button("trigger_help_button", label = "?", parent="trigger_help_layout", align="center", width=25, command = 'cmds.showHelp("http://areadownloads.autodesk.com/wdm/maya/interactive_tutorial_common_conditions.html", absolute = True)')
    cmds.scrollField("trigger_code", wordWrap=False, parent="UI_edit_pane", width = 540, height=300, text=trigger_code, cc=partial(injectData, selected_node, [5]))


#Pass this method any node in the tutorial to get the current stage
def getStage(selected_node):
    current_node = selected_node
    
    while True:
        if cmds.nodeType(current_node) == "stage":
            break
        else:
            current_node = cmds.listConnections(current_node+".before")[0]
     
    return current_node

#Get the most recent camera relative ot the selected node
def getCamera(selected_node):
        
    current_stage = getStage(selected_node)
    
    camera_node = cmds.listConnections(current_stage+".onActivateScript")[0]
    selected_type = cmds.getAttr(camera_node+".before").split("%NODETYPEID%")[1]

    #find the first stage with a setup node (or failing that, Initialize)
    while selected_type != "stage_setup" and current_stage != "stage0":   
        current_stage = cmds.listConnections(current_stage+".previousState")[0]
        camera_node = cmds.listConnections(current_stage+".onActivateScript")[0]
        selected_type = cmds.getAttr(camera_node+".before").split("%NODETYPEID%")[1]

    
    #if a stage with a setup was found, iterate through all possible setup nodes on it to find the last one (in case there's multiple)
    if selected_type == "stage_setup":
        while True:
            next_node = cmds.listConnections(camera_node+".after")
            if next_node:
                selected_type = cmds.getAttr(next_node[0]+".before").split("%NODETYPEID%")[1]
                if selected_type != "stage_setup":
                    break
                else: 
                    camera_node = next_node
            else:
                break

        #camera_node = cmds.listConnections(camera_node+".before")[0]        
    
    parsed_input_list = cmds.getAttr(camera_node+".before").split('#%INPUT%')
    
    selected_type = cmds.getAttr(camera_node+".before").split("%NODETYPEID%")[1]
    
    if selected_type == "stage_setup":
        return parsed_input_list[13].split('\nshot_camera = "')[1][:-2]
    else:
        return parsed_input_list[15].split('\nshot_camera = "')[1][:-2]
           
#Convert absolute placement coordinates to relative % to window size
def convertToRelative(absolute_position):
    mainWindow = mo.maya.getMainMayaWindow()
    maya_window_width = mainWindow.frameGeometry().width()
    maya_window_height = mainWindow.frameGeometry().height()
    
    relative_xy = [int(absolute_position[0] / maya_window_width * 100), int(absolute_position[1] / maya_window_height * 100)-3]
    return relative_xy

#Create a helper window that allows the user to interactively position an overlay
def placeOverlay(*args):
    
    def applyOverlayPosition(*args):
        cmds.deleteUI("positioner_window")    
    
    def cancelOverlayPosition(*args):
        clearAllPreviews()
        selected_node = args[2]
        x_offset = args[0][0]
        y_offset = args[0][1]
        width = args[1]
        
        cmds.deleteUI("positioner_window")  
        cmds.intFieldGrp("text_overlay_xy_offset", e=True, v1=x_offset, v2=y_offset)
        cmds.intField("text_overlay_width", e=True, v=width)
        injectData(selected_node, [5, 7, 15])
        displayPreviewOverlay(selected_node)  
        
    def closeOverlayHelper(*args):
        cmds.scriptJob(kill = args[0])
    
    def updatePreviewOverlay(*args):
        selected_node = args[0]
        window_pos = cmds.window("positioner_window", q=True, tlc=True)
        window_width = cmds.window("positioner_window", q=True, width=True)
        old_overlay_pos =  cmds.intFieldGrp("text_overlay_xy_offset", q=True, v=True)
        overlay_width = cmds.intField("text_overlay_width", q=True, v=True)
        
        rel_to = cmds.optionMenu("text_overlay_rel_to", q=True, v=True)
        maya_window_top_left = cmds.window('MayaWindow', q=True, tlc=True)
        maya_window_width = cmds.window('MayaWindow', q=True, width=True)
        maya_window_height = cmds.window('MayaWindow', q=True, height=True)
        
        x_offset = 0
        y_offset = 0
        placer_offset = 60
        
        if rel_to == "topleft":
            x_offset = window_pos[1] - maya_window_top_left[1]
            y_offset = window_pos[0] - maya_window_top_left[0] - placer_offset
           
        elif rel_to == "top":
            x_offset = window_pos[1] - maya_window_top_left[1] - maya_window_width / 2 + window_width / 2
            y_offset = window_pos[0] - maya_window_top_left[0] - placer_offset
        
        elif rel_to == "topright":
            x_offset = (1920-window_pos[1]-window_width/3) - (1920-maya_window_top_left[1] - maya_window_width)
            y_offset = window_pos[0] - maya_window_top_left[0] - placer_offset
            
        elif rel_to == "left":
            x_offset = window_pos[1] - maya_window_top_left[1]   
            y_offset = window_pos[0] - maya_window_top_left[0] - maya_window_height / 2 - placer_offset + 20
        
        elif rel_to == "center":
            x_offset = window_pos[1] - maya_window_top_left[1] - maya_window_width / 2 + window_width / 2
            y_offset = window_pos[0] - maya_window_top_left[0] - maya_window_height / 2 - placer_offset + 20
        
        elif rel_to == "right":
            x_offset = (1920-window_pos[1]-window_width/3) - (1920-maya_window_top_left[1] - maya_window_width)
            y_offset = window_pos[0] - maya_window_top_left[0] - maya_window_height / 2 - placer_offset + 20
            
        elif rel_to == "bottomleft":
            x_offset = window_pos[1] - maya_window_top_left[1]
            y_offset = (1080-window_pos[0]) - (1080-maya_window_top_left[0]-maya_window_height) + 30
        
        elif rel_to == "bottom":
            x_offset = window_pos[1] - maya_window_top_left[1] - maya_window_width / 2 + window_width / 2
            y_offset = (1080-window_pos[0]) - (1080-maya_window_top_left[0]-maya_window_height) + 30
            
        elif rel_to == "bottomright":
            x_offset = (1920-window_pos[1]-window_width/1.25) - (1920-maya_window_top_left[1] - maya_window_width)
            y_offset = (1080-window_pos[0]) - (1080-maya_window_top_left[0]-maya_window_height) + 30
                
        elif rel_to == "UI code":
            rel_to = cmds.textField("text_overlay_rel_to_custom", q=True, text=True)
            con_browse=[]
            try:
                con_browse=mo.getUIPosition(rel_to)
            except:
                print("UI code not found!")
         
            if con_browse:
                x_offset = window_pos[1] - con_browse.x() - maya_window_top_left[1]
                y_offset = window_pos[0] - con_browse.y() - maya_window_top_left[0] - 90
        
        
        if cmds.optionMenu("text_overlay_is_offset_absolute", q=True, sl=True) == 2:
            relative_xy = convertToRelative([x_offset, y_offset])
            x_offset = relative_xy[0]
            y_offset = relative_xy[1]
            cmds.optionMenu("text_overlay_rel_to", e=True, v="topleft", enable=False)
        else:
            cmds.optionMenu("text_overlay_rel_to", e=True, enable=True)
        
        if old_overlay_pos[0] != x_offset or old_overlay_pos[1] != y_offset or overlay_width != window_width:      
            cmds.intFieldGrp("text_overlay_xy_offset", e=True, v1=x_offset, v2=y_offset)
            cmds.intField("text_overlay_width", e=True, v=window_width)
            displayPreviewOverlay(selected_node)
            injectData(selected_node, [5, 7, 15])
    
    selected_node=args[0]
    
    original_xy_offset = cmds.intFieldGrp("text_overlay_xy_offset", q=True, v=True)
    original_width = cmds.intField("text_overlay_width", q=True, v=True)
    
    if cmds.window("positioner_window", exists=True):
        cmds.deleteUI("positioner_window")    
    
    update_job=cmds.scriptJob(permanent=False, kws=True, event = ["idle", partial(updatePreviewOverlay, selected_node)])    
    
    positioner_window = cmds.window ("positioner_window", title="Position Helper", sizeable=True, widthHeight=(600, 300), closeCommand = partial(closeOverlayHelper, update_job))
    cmds.columnLayout("pw_main", parent=positioner_window)
    cmds.text (align="left", parent = "pw_main", label="\n1. Position and resize this window.\n\n2. Press Apply or Apply and Close.")
    cmds.text ("pw_spacer", label="", parent="pw_main")

    cmds.rowLayout("position_button_layout", numberOfColumns=2, parent = "pw_main")
    cmds.separator(horizontal=True, parent="pw_main")
    cmds.button ("set_postion_button", label="Apply", parent="position_button_layout", command=applyOverlayPosition) 
    cmds.button ("position_close_button", label="Cancel", parent="position_button_layout", command=partial(cancelOverlayPosition, original_xy_offset, original_width, selected_node))
    cmds.showWindow( positioner_window )
    

def openInExpressionEditor(*args):
    cmds.ExpressionEditor()
    maya.mel.eval('EEselectFilterCB scriptNode')

#place the controller in the tutorial creator based on its current position    
def setControllerCurrent(*args):
    selected_node = args[0]
    x=mo.g_overlay_manager.controller.theDialog().x()
    
    y=mo.g_overlay_manager.controller.theDialog().y()
    
    mainWindow = mo.maya.getMainMayaWindow()
    maya_window_top_left = mainWindow.frameGeometry().topLeft()
    maya_window_width = mainWindow.frameGeometry().width()
    maya_window_height = mainWindow.frameGeometry().height()
    """
    maya_window_top_left = cmds.window('MayaWindow', q=True, tlc=True)
    maya_window_width = cmds.window('MayaWindow', q=True, width=True)
    maya_window_height = cmds.window('MayaWindow', q=True, height=True)
    """
    cmds.intFieldGrp("controller_xy_offset", e=True, v1=int((x-maya_window_top_left.x()) / maya_window_width *100), v2=int((y-maya_window_top_left.y()) / maya_window_height *100))
    injectData(selected_node, [15, 17])

    buildEditPane()  
    
#Helper window to allow user to find UI codes easily by hovering over them    
def uiCodeHelper(*args):
    from PySide2.QtWidgets import QApplication
    from PySide2.QtGui import QCursor
    from shiboken2 import getCppPointer as unwrapInstance
    from maya import OpenMayaUI as omui 
    
    if cmds.window("UI_component_finder_window", exists=True):
        cmds.deleteUI("UI_component_finder_window")    
    
    cid_window = cmds.window ("UI_component_finder_window", title="UI component finder", sizeable=True, widthHeight=(600, 300))
    cmds.columnLayout("cf_main", columnAlign = "center", rs=2, parent=cid_window)
    cmds.text (align="center", parent = "cf_main", label="\nHover the cursor over a UI component to display its component ID below.")
    cmds.text ("cf_spacer", label="", parent="cf_main")
    cmds.text ("component_id", label="", parent="cf_main")
    
    def getQtWidgetAtPos(x,y):
        app = QApplication.instance()
        return app.widgetAt(x,y)
    
    def getWidgetNameAtPos(x,y):
        a = getQtWidgetAtPos(x, y)
        name = ''
        outstring = ""
        print(omui.MQtUtil.fullName( int(unwrapInstance(a)[0]) ))
        try:
            name = omui.MQtUtil.fullName( int(unwrapInstance(a)[0]) ).split("|")
            for x in name[::-1]:
                if x:
                    outstring = x
                    break
        except:
            outstring = "No code found"
            
        return outstring
        
    
    def close_component_finder(*args):
        cmds.scriptJob(kill=args[0])
        
    def displayCursor(*args):
        name = getWidgetNameAtPos(QCursor.pos().x(), QCursor.pos().y())
        cmds.text ("component_id", e=True, label=name)
       
        
    job_num = cmds.scriptJob( event = ["idle", displayCursor])
    cid_window = cmds.window ("UI_component_finder_window", e=True, closeCommand = partial(close_component_finder, job_num))
    cmds.showWindow( cid_window )

#assign the current camera + its TRS and Center of Interest to the Initialize or Setup field    
def importCamera(*args):
    node_type = args[1]
    camera_inject = args[2][0]
    code_inject = args[2][1]
      
    curr_camera = 'persp'
    for vp in cmds.getPanel(type="modelPanel"):
        curr_camera=cmds.modelEditor(vp,q=1,av=1,cam=1).split("|")
        
    cam_t = cmds.xform(curr_camera[1], absolute=True, query=True, t=True)
    cam_r = cmds.xform(curr_camera[1], absolute=True, query=True, ro=True)
    coi = cmds.getAttr(curr_camera[1]+"Shape.centerOfInterest") 
     
    code_field = ""
    inject1 = 0
    inject2 = 0
    
    if node_type == "initialize":
        cmds.optionMenu("initial_shot_camera", e=True, v=curr_camera[1])
        code_field = "initial_setup_code"
        
    else:
        cmds.optionMenu("setup_shot_camera", e=True, v=curr_camera[1])
        code_field = "setup_code"
        
    setup_code = cmds.scrollField(code_field, q=True, text=True)
    setup_code = setup_code + "cmds.xform('"+curr_camera[1]+"', absolute=True, t=("+str(cam_t[0])+", "+str(cam_t[1])+", "+str(cam_t[2])+"), ro=("+str(cam_r[0])+", "+str(cam_r[1])+", "+str(cam_r[2])+"))\n" 
    setup_code = setup_code + "\ncmds.setAttr('"+curr_camera[1]+"Shape.centerOfInterest', "+str(coi)+")\n"
    cmds.scrollField(code_field, e=True, text=setup_code)
    injectData(args[0], args[1], [camera_inject, code_inject])
    
#Provide a stage and this method will set the current time range to the nearest time slider bookmark (even if it is on a previous stage)
def jumpToNearestBookmark(current_stage):
    current_bookmark = cmds.listConnections(current_stage+".timeSliderBookmark")
        
    if not current_bookmark:
        while not current_bookmark:
            try:
                current_stage = cmds.listConnections(current_stage+".previousState")[0]
                current_bookmark = cmds.listConnections(current_stage+".timeSliderBookmark")
            except:
                break
    if current_bookmark:    
        start_frame = cmds.getAttr(current_bookmark[0]+".timeRangeStart")
        end_frame = cmds.getAttr(current_bookmark[0]+".timeRangeStop")
        
        cmds.playbackOptions(min=start_frame, max=end_frame)  
        cmds.currentTime(start_frame)

   
def sortChronologically(tsbm_list):
    
    start_frame_list =[]
    for x in tsbm_list:
        start_frame_list.append(cmds.getAttr(x+".timeRangeStart"))
        
    start_frame_list.sort()
    
    output_list = []
    for x in start_frame_list:
         for y in tsbm_list:
             if cmds.getAttr(y+".timeRangeStart") == x:
                 output_list.append(y)
                 tsbm_list.remove(y)
                 break
    return output_list          

#Update the edit pane to reflect the proper options for the selected node type
def buildEditPane(*args):
    clearAllPreviews()
              
    node_list = "tc_window|main|section_edit|node_list"
    menu_mode_UI = "StatusLine|MainStatusLineLayout|formLayout4|flowLayout1|optionMenuForm|menuMode"
    
    #clear the previous contents of the pane
    current_pane_contents = cmds.rowColumnLayout("UI_edit_pane", q=True, ca=True)
    for x in current_pane_contents:
       cmds.deleteUI(x)
	 
    selected_node = cmds.textScrollList(node_list, q=True, si=True)[0]
    selected_node = selected_node.replace("    ", "")
    cmds.select(selected_node)
    node_type = cmds.nodeType(selected_node)
    
    current_stage = getStage(selected_node)
    
    cmds.button("rename_node_button", e=True, enable=True)
    cmds.button("delete_node_button", e=True, enable=True)
    
    if node_type == "script":
        selected_type = cmds.getAttr(selected_node+".before").split("%NODETYPEID%")[1]
        parsed_input_list = cmds.getAttr(selected_node+".before").split('#%INPUT%')

        if selected_type == "initialize":
            
            #9 Speech style
            speech_style = parsed_input_list[9].split("\ndefault_speech_style = '")[1][1:][:-3]
            cmds.text("Default Speech Style", parent="UI_edit_pane")
            cmds.textField("default_speech_style", parent="UI_edit_pane", text=speech_style, cc=partial(injectData, selected_node, [9]))

            #11 dialog style
            dialog_style = parsed_input_list[11].split("\ndefault_dialog_style = '")[1][1:][:-3]
            cmds.text("Default Dialog Style", parent="UI_edit_pane")
            cmds.textField("default_dialog_style", parent="UI_edit_pane", text=dialog_style, cc=partial(injectData, selected_node, [11]))
            
            #13 control_style
            controller_style = parsed_input_list[13].split("\ndefault_control_style = '")[1][1:][:-3]
            cmds.text("Default Controller Style", parent="UI_edit_pane")
            cmds.textField("default_controller_style", parent="UI_edit_pane", text=controller_style, cc=partial(injectData, selected_node, [13]))

            #1, 3, 5, 7 UI Visiblity
            ae_vis = True
            if parsed_input_list[1].split('\nis_ae_visible = ')[1][:-1] == "False":
                ae_vis = False
            cb_vis = True
            if parsed_input_list[3].split('\nis_cb_visible = ')[1][:-1] == "False":
                cb_vis = False
            outliner_vis = True
            if parsed_input_list[5].split('\nis_outliner_visible = ')[1][:-1] == "False":
                outliner_vis = False
            mtk_vis = True
            if parsed_input_list[7].split('\nis_mtk_visible = ')[1][:-1] == "False":
                mtk_vis = False
                
            cmds.text("UI Visibility ", parent="UI_edit_pane")
            cmds.checkBoxGrp("UI_vis", parent="UI_edit_pane", numberOfCheckBoxes=4, vr=False, labelArray4=['Attribute\nEditor', 'Channel\nBox', 'Outliner', 'Modeling\nToolkit'], v1=ae_vis, v2=cb_vis, v3=outliner_vis, v4=mtk_vis, cc=partial(injectData, selected_node, [1, 3, 5, 7]))
            
            #17 Menu set
            menu_set = parsed_input_list[17].split('\nmenu_set = ')[1]
            cmds.text("Menu Set", parent="UI_edit_pane")
            cmds.optionMenu("menu_mode", parent="UI_edit_pane", cc=partial(injectData, selected_node, [17]))
            menu_list = cmds.optionMenu(menu_mode_UI, q=True, ill=True)
            for x in menu_list:
                cmds.menuItem(cmds.menuItem(x, q=True, label=True))
            cmds.optionMenu("menu_mode", e=True, sl=int(menu_set))

            #19 Current Tool
            current_tool = parsed_input_list[19].split('\ntool_ctx = "')[1][:-2]
            cmds.text("Tool Context", parent="UI_edit_pane")
            cmds.optionMenu("tool_ctx", parent="UI_edit_pane", cc=partial(injectData, selected_node, [19]))
            menu_list = cmds.lsUI(contexts=True)
            for x in menu_list:
                cmds.menuItem(x)
            cmds.optionMenu("tool_ctx", e=True, v=current_tool)
            
            #15 Shot camera
            shot_cam = parsed_input_list[15].split('\nshot_camera = "')[1][:-2]
            cmds.text("Look Through Camera ", parent="UI_edit_pane")
            cmds.optionMenu("initial_shot_camera", parent = "UI_edit_pane", cc=partial(injectData, selected_node, [15]))
            camera_list = cmds.listCameras()
            for x in camera_list:
                cmds.menuItem(x)
            cmds.optionMenu("initial_shot_camera", e=True, v=shot_cam)
            
            #21 Additional setup
            setup_code = ""
            setup_lines = parsed_input_list[21].split("\n")
            count = 2
            for x in setup_lines[1:]:
                setup_code = setup_code+x
                if count == len(setup_lines)-1:
                    break
                else:
                    setup_code = setup_code+"\n"
                    count = count+1
            
            cmds.text("Additional Setup Instructions \n(Python code) ", parent="UI_edit_pane")
            cmds.scrollField("initial_setup_code", wordWrap=False, parent="UI_edit_pane", text=setup_code, cc=partial(injectData, selected_node, [21]))
            
            cmds.text("setup_spacer", label="", parent="UI_edit_pane")
            cmds.button("import_camera", label="Import current camera + values", parent="UI_edit_pane", command = partial(importCamera, selected_node, node_type, [15, 21]))
            
        elif selected_type == "stage_setup":
            
            #1, 3, 5, 7 UI Visiblity
            ae_vis = True
            if parsed_input_list[1].split('\nis_ae_visible = ')[1][:-1] == "False":
                ae_vis = False
            cb_vis = True
            if parsed_input_list[3].split('\nis_cb_visible = ')[1][:-1] == "False":
                cb_vis = False
            outliner_vis = True
            if parsed_input_list[5].split('\nis_outliner_visible = ')[1][:-1] == "False":
                outliner_vis = False
            mtk_vis = True
            if parsed_input_list[7].split('\nis_mtk_visible = ')[1][:-1] == "False":
                mtk_vis = False
            
            cmds.text("UI Visibility ", parent="UI_edit_pane")
            cmds.checkBoxGrp("UI_vis", parent="UI_edit_pane", numberOfCheckBoxes=4, vr=False, labelArray4=['Attribute\nEditor', 'Channel\nBox', 'Outliner', 'Modeling\nToolkit'], v1=ae_vis, v2=cb_vis, v3=outliner_vis, v4=mtk_vis, cc=partial(injectData, selected_node, [1, 3, 5, 7]))
            
            #9 Menu set
            menu_set = parsed_input_list[9].split('\nmenu_set = ')[1]
            cmds.text("Menu Set", parent="UI_edit_pane")
            cmds.optionMenu("menu_mode", parent="UI_edit_pane", cc=partial(injectData, selected_node, [9]))
            menu_list = cmds.optionMenu(menu_mode_UI, q=True, ill=True)

            for x in menu_list:
                cmds.menuItem(cmds.menuItem(x, q=True, label=True))
            cmds.optionMenu("menu_mode", e=True, sl=int(menu_set))
            
            #11 Current Tool
            current_tool = parsed_input_list[11].split('\ntool_ctx = "')[1][:-2]
            cmds.text("Tool Context", parent="UI_edit_pane")
            cmds.optionMenu("tool_ctx", parent="UI_edit_pane", cc=partial(injectData, selected_node, [11]))
            menu_list = cmds.lsUI(contexts=True)
            for x in menu_list:
                cmds.menuItem(x)
            cmds.optionMenu("tool_ctx", e=True, v=current_tool)
            
            #13 Shot camera
            shot_cam = parsed_input_list[13].split('\nshot_camera = "')[1][:-2]
            cmds.text("Look Through Camera ", parent="UI_edit_pane")
            cmds.optionMenu("setup_shot_camera", parent = "UI_edit_pane", cc=partial(injectData, selected_node, [13]))
            camera_list = cmds.listCameras()
            for x in camera_list:
                cmds.menuItem(x)
            cmds.optionMenu("setup_shot_camera", e=True, v=shot_cam)
                
            #15 Reset Step
            reset_step_code = ""
            reset_step_lines = parsed_input_list[15].split("\n")
            count = 2
            for x in reset_step_lines[1:]:
                reset_step_code = reset_step_code+x.replace("\t", "", 1)
                if count == len(reset_step_lines)-1:
                    break
                else:
                    reset_step_code = reset_step_code+"\n"
                    count = count+1

            cmds.text("Reset Step Instructions \n(Python code) ", parent="UI_edit_pane")
            cmds.scrollField("setup_reset_code", wordWrap=False, parent="UI_edit_pane", width = 400, text=reset_step_code, cc=partial(injectData, selected_node, [15]))
            
            #17 Additional setup
            setup_code = ""
            setup_lines = parsed_input_list[17].split("\n")
            count = 2
            for x in setup_lines[1:]:
                setup_code = setup_code+x
                if count == len(setup_lines)-1:
                    break
                else:
                    setup_code = setup_code+"\n"
                    count = count+1


            cmds.text("Step Setup Instructions \n(Python code) ", parent="UI_edit_pane")
            cmds.scrollField("setup_code", wordWrap=False, parent="UI_edit_pane", width = 400, text=setup_code, cc=partial(injectData, selected_node, [17]))
            
            cmds.text("setup_spacer", label="", parent="UI_edit_pane")
            cmds.button("import_camera", label="Import current camera + values", parent="UI_edit_pane", command = partial(importCamera, selected_node, node_type, [13, 17]))
            
        elif selected_type == "text_overlay":
            #1 Step text
            step_text = parsed_input_list[1].split('\nhtml_text = """')[1][:-4]
            cmds.text("Step Text ", parent="UI_edit_pane")
            cmds.textField("text_overlay_html_text", parent="UI_edit_pane", text=step_text, cc=partial(injectData, selected_node, [1]))
            
            #5, 7 XY Offset
            x_offset = parsed_input_list[5].split("\nx_offset = ")[1][:-1]
            y_offset = parsed_input_list[7].split("\ny_offset = ")[1][:-1]
            cmds.text("XY Offset ", parent="UI_edit_pane")

            cmds.intFieldGrp("text_overlay_xy_offset", parent="UI_edit_pane", numberOfFields = 2, v1=int(x_offset), v2=int(y_offset), cc=partial(injectData, selected_node, [5, 7]))
            
            #3 Offset Type
            is_absolute = parsed_input_list[3].split('\nis_offset_absolute = ')[1][:-1]
            cmds.text("Offset Type ", parent="UI_edit_pane")
            cmds.optionMenu("text_overlay_is_offset_absolute", parent = "UI_edit_pane", cc=partial(injectData, selected_node, [3]))
            cmds.menuItem("Absolute Coordinates")
            cmds.menuItem("Relative % to window size")
            if is_absolute == "True":
                cmds.optionMenu("text_overlay_is_offset_absolute", e=True, sl=1)
            else:
                 cmds.optionMenu("text_overlay_is_offset_absolute", e=True, sl=2)

                   
            #9 Rel_to
            rel_to = parsed_input_list[9].split('\nrel_to = "')[1][:-2]
    
            cmds.text("Relative to ", parent="UI_edit_pane")
            cmds.optionMenu("text_overlay_rel_to", parent="UI_edit_pane", cc=partial(injectData, selected_node, [9]))
            cmds.menuItem("topleft")
            cmds.menuItem("top")
            cmds.menuItem("topright")
            cmds.menuItem("left")
            cmds.menuItem("center")
            cmds.menuItem("right")
            cmds.menuItem("bottomleft")
            cmds.menuItem("bottom")
            cmds.menuItem("bottomright")
            cmds.menuItem("UI code") 
           
            custom_UI = False 
            
            if is_absolute == "False":
                cmds.optionMenu("text_overlay_rel_to", e=True, sl=1, enable=False)
            else:
                cmds.optionMenu("text_overlay_rel_to", e=True, enable=True)
                 
                try:
                    cmds.optionMenu("text_overlay_rel_to", e=True, v=rel_to)
                except:
                    cmds.optionMenu("text_overlay_rel_to", e=True, sl=10)
                    custom_UI=True
    
            #9 UI code     
            cmds.text("UI Code ", parent="UI_edit_pane")
            cmds.rowLayout("ui_code_layout", parent="UI_edit_pane", numberOfColumns=2)
            cmds.textField("text_overlay_rel_to_custom", parent="ui_code_layout", width=200, cc=partial(injectData, selected_node, [9]))
            if custom_UI:
                cmds.textField("text_overlay_rel_to_custom", e=True, text=rel_to, enable=True)
            else:
                cmds.textField("text_overlay_rel_to_custom", e=True, enable=False)
    
            cmds.button("get_ui_code_button", label="Find UI code", parent="ui_code_layout", command=uiCodeHelper) 
    
            #11 Bubble Tail Direction
            tail_orientation = parsed_input_list[11].split('\ntail_orientation = "')[1][:-2]
            cmds.text("Bubble Tail Direction ", parent="UI_edit_pane")
            cmds.optionMenu("text_overlay_tail_dir", parent="UI_edit_pane", cc=partial(injectData, selected_node, [11]))
            cmds.menuItem("top")
            cmds.menuItem("left")
            cmds.menuItem("right")
            cmds.menuItem("bottom")
            
            cmds.optionMenu("text_overlay_tail_dir", e=True, v=tail_orientation)
    
            #13 Bubble tail position
            tail_pos = parsed_input_list[13].split('\ntail_position = ')[1][:-1]    
            cmds.text("Bubble Tail Position ", parent="UI_edit_pane")
            cmds.floatSliderGrp("text_overlay_tail_pos", parent="UI_edit_pane", field=True, minValue= 0.00, maxValue=1.00, fieldMinValue = 0.0, fieldMaxValue = 1.0, precision=3, value=float(tail_pos), cc=partial(injectData, selected_node, [13] ))
            
            #15 Overlay width
            overlay_width = parsed_input_list[15].split('\noverlay_width = ')[1][:-1]    
            cmds.text("Overlay Width ", parent="UI_edit_pane")  
            cmds.intField("text_overlay_width", parent="UI_edit_pane", v=int(overlay_width), cc=partial(injectData, selected_node, [15]))
            
            #17 Dialog Style
            is_dialog = parsed_input_list[17].split('\ndialog_style = ')[1][:-1] 
            cmds.text("Dialog Style ", parent="UI_edit_pane")
            cmds.checkBox("text_overlay_dialog_style", label="Enable", parent="UI_edit_pane", cc=partial(injectData, selected_node, [17]))
            
            if is_dialog == "True":
                cmds.checkBox("text_overlay_dialog_style", e=True, v=True)
                cmds.optionMenu("text_overlay_is_offset_absolute", e=True, sl=2)
                cmds.optionMenu("text_overlay_is_offset_absolute", e=True, enable=False)
                cmds.optionMenu("text_overlay_rel_to", e=True, sl=1, enable=False)
                cmds.floatSliderGrp("text_overlay_tail_pos", e=True, enable=False)
                cmds.optionMenu("text_overlay_tail_dir", e=True, enable=False)
            else:
                cmds.checkBox("text_overlay_dialog_style", e=True, v=False)
                cmds.optionMenu("text_overlay_is_offset_absolute", e=True, enable=True)
                cmds.optionMenu("text_overlay_rel_to", e=True, enable=True)
                cmds.floatSliderGrp("text_overlay_tail_pos", e=True, enable=True)
                cmds.optionMenu("text_overlay_tail_dir", e=True, enable=True)
                
            cmds.text("spacer1", label="", parent="UI_edit_pane")
            cmds.text("spacer2", label="", parent="UI_edit_pane")
            cmds.text("spacer3", label="", parent="UI_edit_pane")
            
            cmds.button("Placement Helper", parent="UI_edit_pane", command = partial(placeOverlay, selected_node))
            cmds.text("spacer4", label="", parent="UI_edit_pane")
            cmds.button("Clear Previews", parent="UI_edit_pane", width=100, command = clearAllPreviews)
            displayPreviewOverlay(selected_node)    
    
        elif selected_type == "update_controller":
            #1 Step title
            instruct_title = parsed_input_list[1].split('\ntitle = """')[1][:-4]
            cmds.text("Controller Title ", parent="UI_edit_pane")
            cmds.textField("update_controller_title", parent="UI_edit_pane", width=300, text=instruct_title, cc=partial(injectData, selected_node, [1]))
            
            #3 Step description
            instruct_description = parsed_input_list[3].split('\ndescription = """')[1][:-4]
            cmds.text("Controller Description ", parent="UI_edit_pane")
            cmds.scrollField("update_controller_description", wordWrap=False, height=100, parent="UI_edit_pane", text=instruct_description, cc=partial(injectData, selected_node, [3]))
            
            #5 Left Button Text
            left_button_text = parsed_input_list[5].split('\nbutton0 = "')[1][:-2]
            cmds.text("Left Button Text ", parent="UI_edit_pane")
            cmds.textField("update_controller_left_button", parent="UI_edit_pane", text=left_button_text, cc=partial(injectData, selected_node, [5]))
            
            #7 right Button Text
            right_button_text = parsed_input_list[7].split('\nbutton1 = "')[1][:-2]
            cmds.text("Right Button Text ", parent="UI_edit_pane")
            cmds.textField("update_controller_right_button", parent="UI_edit_pane", text=right_button_text, cc=partial(injectData, selected_node, [7]))
            
            #9 Disable Reset
            disable_reset = parsed_input_list[9].split('\ndisable_reset = ')[1][:-1] 
            cmds.text("Disable Reset Button ", parent="UI_edit_pane")
            cmds.checkBox("update_controller_disable_reset", label="", parent="UI_edit_pane", cc=partial(injectData, selected_node, [9]))   
            if disable_reset == "True":
                cmds.checkBox("update_controller_disable_reset", e=True, v=True)
            else:    
                cmds.checkBox("update_controller_disable_reset", e=True, v=False)
            
            #11 Disable Next
            disable_next = parsed_input_list[11].split('\ndisable_next = ')[1][:-1] 
            cmds.text("Disable Next Button ", parent="UI_edit_pane")
            cmds.checkBox("update_controller_disable_next", label="", parent="UI_edit_pane", cc=partial(injectData, selected_node, [11]))   
            if disable_next == "True":
                cmds.checkBox("update_controller_disable_next", e=True, v=True)
            else:    
                cmds.checkBox("update_controller_disable_next", e=True, v=False)
                
            #13 Increment step counter
            increment_step = parsed_input_list[13].split('\nincrement_step = ')[1][:-1] 
            cmds.text("Increment step counter ", parent="UI_edit_pane")
            cmds.checkBox("update_controller_increment_step", label="", parent="UI_edit_pane", cc=partial(injectData, selected_node, [13]))   
            if increment_step == "True":
                cmds.checkBox("update_controller_increment_step", e=True, v=True)
            else:    
                cmds.checkBox("update_controller_increment_step", e=True, v=False)
            
            #15, 17 Place overlay
            x_offset = parsed_input_list[15].split('\nx_offset = ')[1][:-1] 
            y_offset = parsed_input_list[17].split('\ny_offset = ')[1][:-1] 
            cmds.text("XY Offset (Window relative %) ", parent="UI_edit_pane")
            cmds.rowLayout("controller_offset_layout", parent="UI_edit_pane", numberOfColumns = 3)
            cmds.intFieldGrp("controller_xy_offset", parent="controller_offset_layout", numberOfFields = 2, v1=int(x_offset), v2=int(y_offset), cc=partial(injectData, selected_node, [15, 17]))
            cmds.text("offset_or", label="or   ", parent="controller_offset_layout")
            cmds.button("set_as_current", label="Set current location", parent="controller_offset_layout", command = partial(setControllerCurrent, selected_node))

            cmds.text("spacer1", label="", parent="UI_edit_pane")
            cmds.text("spacer2", label="", parent="UI_edit_pane")
            cmds.text("spacer3", label="", parent="UI_edit_pane")
            
            cmds.button("Clear Previews", parent="UI_edit_pane", width=100, command = clearAllPreviews)

            displayPreviewController()
            
                       
        elif selected_type == "trigger":
            
            #1: Trigger Type
            trigger_type = parsed_input_list[1].split('\ntrigger_type = "')[1][:-2]
            cmds.text("Trigger Type", parent="UI_edit_pane")
            cmds.optionMenu("trigger_type", parent = "UI_edit_pane", cc=partial(injectData, selected_node, [1, 3]))
            cmds.menuItem("Attribute Change")
            cmds.menuItem("Connection Change")
            cmds.menuItem("Condition")
            cmds.menuItem("Event")
            cmds.optionMenu("trigger_type", e=True, v=trigger_type)
            
            buildDynamicTriggerUI(selected_node, parsed_input_list)
                
        else:
            cmds.text("error_spacer1", label = "         ", parent="UI_edit_pane")
            cmds.text("Sorry, but this node is not compatible with the Tutorial Creator App.", parent="UI_edit_pane")    
            cmds.text("error_spacer2", label = "", parent="UI_edit_pane")
            cmds.button("open_expression_editor", label="View in Expression Editor", parent="UI_edit_pane", command=openInExpressionEditor)
            
    
    #if a stage node is selected
    else:
        cmds.text("Add New Component ", parent="UI_edit_pane")
        cmds.button("+New Component", parent="UI_edit_pane", height=50, width=100, command = partial(addStepNodesWindow, False))
        cmds.text("Auto Play ", parent="UI_edit_pane")
        cmds.checkBox("auto_play_checkbox", label="", parent="UI_edit_pane", v=cmds.getAttr(selected_node+".autoPlay"), cc = partial(updateStage, selected_node))
        cmds.text("End of Animation ", parent="UI_edit_pane")
        cmds.checkBox("end_animation_checkbox", label="", parent="UI_edit_pane", v=cmds.getAttr(selected_node+".endOfAnimation"), cc = partial(updateStage, selected_node))   
        cmds.text("Condition ", parent="UI_edit_pane")
        cmds.checkBox("condition_checkbox", label="", parent="UI_edit_pane", v=cmds.getAttr(selected_node+".condition"), cc = partial(updateStage, selected_node))     
        cmds.text("Time Delay ", parent="UI_edit_pane")
        cmds.floatField("time_delay_field", parent="UI_edit_pane", precision=3, v=cmds.getAttr(selected_node+".timeDelay"), cc = partial(updateStage, selected_node))
        cmds.text("Time Slider Bookmark ", parent="UI_edit_pane")
        cmds.optionMenu("time_slider_bookmark_list", parent="UI_edit_pane", cc= partial(connectTimeSliderBookmark, selected_node))
        cmds.menuItem("None")
        time_slider_bookmark_list = cmds.ls(type="timeSliderBookmark")
        sorted_time_slider_bookmark_list = sortChronologically(time_slider_bookmark_list)
        for x in sorted_time_slider_bookmark_list:
            cmds.menuItem(cmds.getAttr(x+".name"))    
        
        current_bookmark = cmds.listConnections(selected_node+".timeSliderBookmark")
        if current_bookmark:
            cmds.optionMenu("time_slider_bookmark_list", e=True, v=cmds.getAttr(current_bookmark[0]+".name"))
        else:
            cmds.optionMenu("time_slider_bookmark_list", e=True, sl=1)
        
                
        cmds.text("bookmark_spacer", label="", parent="UI_edit_pane")
        cmds.button("Create New Bookmark", parent="UI_edit_pane", command=partial(newBookmark, selected_node))
        
        if current_bookmark:
            cmds.text("Step Frame Range ", parent="UI_edit_pane")
            cmds.intFieldGrp("step_frame_range", parent="UI_edit_pane", numberOfFields = 2, v1=cmds.getAttr(current_bookmark[0]+".timeRangeStart"), v2=cmds.getAttr(current_bookmark[0]+".timeRangeStop"), cc=partial(updateTimeSliderBookmark, selected_node))    
            cmds.text("frame_range_button", label="", parent="UI_edit_pane")
            cmds.button("Go to Frame Range", parent="UI_edit_pane", command=setPlaybackRange)
    
    if cmds.menuItem("jump_to_stage", q=True, checkBox=True):
        jumpToNearestBookmark(current_stage)
        
    if cmds.menuItem("jump_to_camera", q=True, checkBox=True):
        cmds.lookThru(getCamera(selected_node))     

#Update stage node values based on values in the edit pane
def updateStage(*args):
    selected_node = args[0]
    cmds.setAttr(selected_node+".autoPlay", cmds.checkBox("auto_play_checkbox", q=True, v=True))
    cmds.setAttr(selected_node+".endOfAnimation", cmds.checkBox("end_animation_checkbox", q=True, v=True))
    cmds.setAttr(selected_node+".condition", cmds.checkBox("condition_checkbox", q=True, v=True))
    cmds.setAttr(selected_node+".timeDelay", cmds.floatField("time_delay_field", q=True, v=True))

#refresh the node list UI
def populateNodeList(*args):
    node_list = "tc_window|main|section_edit|node_list"
    cmds.textScrollList(node_list, e=True, removeAll=True) 
    current_stage = cmds.ls("stage0")
    while current_stage and current_stage[0] != "final_stage":
        cmds.textScrollList(node_list, e=True, append=current_stage[0])
        current_script = cmds.listConnections(current_stage[0]+".onActivateScript")
        while current_script:
            cmds.textScrollList(node_list, e=True, append="    "+current_script[0])
            current_script = cmds.listConnections(current_script[0]+".after")
        
        current_stage = cmds.listConnections(current_stage[0]+".nextState")
        
        
#Insert a new stage in the tutorial at the location indicated by the Create New Step window
def addStepNodes(*args):
    node_list = "tc_window|main|section_edit|node_list"
    insertion_stage = args[0]
    is_new_step = args[1]
    next_stage = cmds.listConnections(insertion_stage, d=True, s=False, type="stage")
    new_stage = ""
    
    if is_new_step:
        #create a new stage and store the current last stage number
        new_stage = cmds.stage()[0] 
        set1=cmds.ls("GRAPH_MY_CHILDREN")[0]
        cmds.sets(new_stage, e=True, addElement=set1)
            
        cmds.connectAttr(insertion_stage+".nextState", new_stage+".previousState")
        cmds.connectAttr(insertion_stage+".onDeactivateScript", new_stage+".onDeactivateScript")

        
        #if we're inserting mid-tutorial
        if next_stage and next_stage[0] != "final_stage":
            if len(insertion_stage.split("_")) < 2:
                cmds.rename(new_stage, insertion_stage+"_1")
                new_stage = insertion_stage+"_1"
            else:
                #We must use this selection process in case the code attempts to rename the node to one that already exists
                cmds.select(new_stage)
                cmds.rename(new_stage, insertion_stage)
                new_name = cmds.ls(sl=True)[0]
                new_stage = new_name
                
            cmds.disconnectAttr(insertion_stage+".nextState", next_stage[0]+".previousState" )
            cmds.connectAttr(new_stage+".nextState", next_stage[0]+".previousState")
            cmds.disconnectAttr(insertion_stage+".onDeactivateScript", next_stage[0]+".onDeactivateScript" )
            cmds.connectAttr(new_stage+".onDeactivateScript", next_stage[0]+".onDeactivateScript")            
    
        else:
            cmds.disconnectAttr(insertion_stage+".nextState", "final_stage.previousState")
            cmds.connectAttr(new_stage+".nextState", "final_stage.previousState")
    else:
        new_stage = insertion_stage
    
    existing_nodes = []
    if not is_new_step:
        next_node = cmds.listConnections(insertion_stage+".onActivateScript")[0]
        
        while next_node:
            existing_nodes.append(next_node)
            try:
                next_node = cmds.listConnections(next_node+".after")[0]
            except:
                break 
    
    #add additional nodes to the network depending on checkboxes
    is_setup = cmds.checkBoxGrp("include_nodes", q=True, v1=True)
    is_text = cmds.checkBoxGrp("include_nodes", q=True, v2=True)
    is_controller_update = cmds.checkBoxGrp("include_nodes", q=True, v3=True)
    is_trigger = cmds.checkBoxGrp("include_nodes", q=True, v4=True)
    
    last_node = ""
    if is_new_step:
        last_node = new_stage
    else:
        last_node = insertion_stage
        
    current_type = ""
    count = 0
    
    new_node = ""
    
    if is_setup:
        last_setup = new_stage+"_setup"

        cmds.duplicate("_template_stage_setup", name="_setup_temp_")
        last_setup = renameNode("_setup_temp_", last_setup)
        
        if not is_new_step:
            current_type = cmds.getAttr(existing_nodes[count]+".before").split("%NODETYPEID%")[1]
            
            for x in existing_nodes:
                
                current_type = cmds.getAttr(existing_nodes[count]+".before").split("%NODETYPEID%")[1]
                if current_type == "stage_setup" or current_type == "initialize":
                    last_node = x
                    count=count+1
                else:    
                    break
                       
        if (cmds.nodeType(last_node) == "stage"):
            cmds.connectAttr(last_setup+".before", last_node+".onActivateScript", force=True)
        else:
            cmds.connectAttr(last_setup+".before", last_node+".after", force=True)
        last_node = last_setup  
        
        try:
            cmds.connectAttr(existing_nodes[count]+".before", last_node+".after", force=True)
        except:
            pass
        
    if is_text:
        last_text_overlay= new_stage+"_text_overlay"

        cmds.duplicate("_template_text_overlay", name="_setup_temp_")
        last_text_overlay = renameNode("_setup_temp_", last_text_overlay)
        
        if not is_new_step:
            current_type = cmds.getAttr(existing_nodes[count]+".before").split("%NODETYPEID%")[1]
            
            for x in existing_nodes:
                current_type = cmds.getAttr(existing_nodes[count]+".before").split("%NODETYPEID%")[1]
                if current_type == "text_overlay" or current_type == "stage_setup" or current_type == "initialize":
                    last_node = existing_nodes[count]
                    count=count+1
                else:
                    break
        
        if (cmds.nodeType(last_node) == "stage"):
            cmds.connectAttr(last_text_overlay+".before", last_node+".onActivateScript", force=True)
        else:
            cmds.connectAttr(last_text_overlay+".before", last_node+".after", force=True)
        last_node = last_text_overlay  
        
        try:
            cmds.connectAttr(existing_nodes[count]+".before", last_node+".after", force=True)
        except:
            pass
    
    if is_controller_update:
        last_update_controller = new_stage+"_update_controller"

        cmds.duplicate("_template_update_controller", name="_setup_temp_")
        last_update_controller = renameNode("_setup_temp_", last_update_controller)
        
        if not is_new_step:
            current_type = cmds.getAttr(existing_nodes[count]+".before").split("%NODETYPEID%")[1]
            
            for x in existing_nodes:
                current_type = cmds.getAttr(existing_nodes[count]+".before").split("%NODETYPEID%")[1]
                if current_type == "text_overlay" or current_type == "stage_setup" or current_type == "update_controller" or current_type == "initialize":
                    last_node = existing_nodes[count]
                    count=count+1
                else:
                    break
        
        if (cmds.nodeType(last_node) == "stage"):
            cmds.connectAttr(last_update_controller+".before", last_node+".onActivateScript", force=True)
        else:
            cmds.connectAttr(last_update_controller+".before", last_node+".after", force=True)
        last_node = last_update_controller  
        
        try:
            cmds.connectAttr(existing_nodes[count]+".before", last_node+".after", force=True)
        except:
            pass
        
    if is_trigger:
        last_trigger = new_stage
        cmds.duplicate("_template_trigger", name="_setup_temp_")
        last_trigger = last_trigger+"_trigger"

        last_trigger = renameNode("_setup_temp_", last_trigger)    
        
        if not is_new_step:
            last_node = existing_nodes[len(existing_nodes)-1]
            
        if (cmds.nodeType(last_node) == "stage"):
            cmds.connectAttr(last_trigger+".before", last_node+".onActivateScript", force=True)
        else:
            cmds.connectAttr(last_trigger+".before", last_node+".after", force=True)
        last_node = last_trigger  

    try:
        cmds.deleteUI("new_step_window")
    except:
        pass
    
    if is_new_step:      
        populateNodeList(new_stage)
        cmds.textScrollList("tc_window|main|section_edit|node_list", e=True, si=new_stage)
    else:
        populateNodeList("    "+last_node)
        cmds.textScrollList("tc_window|main|section_edit|node_list", e=True, si="    "+last_node)
    buildEditPane()
        

def updateSelectedStage(*args):
    is_new_step = args[0]
    selected_stage = cmds.optionMenu("stage_list", q=True, v=True)
    cmds.button( "add_stage_button", e=True, command = partial(addStepNodes, selected_stage, is_new_step)) 
        
      

#Create new step option window
def addStepNodesWindow(*args):
    
    is_new_step = args[0]
    node_list = "tc_window|main|section_edit|node_list"
    
    if cmds.window("new_step_window", exists=True):
        cmds.deleteUI("new_step_window")         
        
    new_step_window = cmds.window ("new_step_window", title="Add Nodes", widthHeight=(600, 400))
    cmds.columnLayout("new_step_window_main", parent = new_step_window, width = 600)
    
    cmds.rowColumnLayout("step_options", parent="new_step_window_main", numberOfColumns=2, cs = (2, 5), rs = (2, 5), cal=(1, "left"))
    cmds.text("Step includes: ", parent = "step_options")
    cmds.checkBoxGrp( "include_nodes", parent = "step_options", numberOfCheckBoxes=4, vr=False, labelArray4=['Setup', 'Text', 'Controller\n Update', 'Trigger'] )
    
    #Default values when creating a new step
    if is_new_step:
        cmds.checkBoxGrp( "include_nodes", e=True, v2=True, v3=True )
        cmds.window ("new_step_window", e=True, title="Add New Step")

    cmds.text("insert_after", label="Insert after: ", parent = "step_options")
    cmds.optionMenu("stage_list", parent = "step_options", cc=partial(updateSelectedStage, is_new_step))
    current_stage = cmds.ls("stage0")
    while current_stage and current_stage[0] != "final_stage":
        cmds.menuItem(current_stage[0])
        current_stage = cmds.listConnections(current_stage[0]+".nextState")

    if is_new_step:
        cmds.text("insert_after", e=True, visible=True)
        cmds.optionMenu("stage_list", e=True, visible=True, sl=cmds.optionMenu("stage_list", q=True, numberOfItems=True))
    else:
        cmds.text("insert_after", e=True, visible=False)
        cmds.optionMenu("stage_list", e=True, visible=False, v=cmds.textScrollList(node_list, q=True, si=True)[0])
    
    
    cmds.separator(parent="new_step_window_main", height=50)
    cmds.rowColumnLayout("add_button_layout", numberOfColumns=3, cal=(1, "both"), parent="new_step_window_main")
    cmds.text("                                                                ", parent="add_button_layout")
    selected_stage= cmds.optionMenu("stage_list", q=True, v=True)
    cmds.button( "add_stage_button", label='Add', parent="add_button_layout", height=50, width=100, command = partial(addStepNodes, selected_stage, is_new_step))    
    cmds.setParent( '..' )
    cmds.showWindow( new_step_window )

#Rename the node and inject the new node name into the appropriate script
def renameNode(*args):
    selected_node = cmds.ls(args[0])[0]
    if args[1]:
        new_name = args[1]
    else:
        new_name = cmds.textField("node_name_field", q=True, text=True)
    #Must rename using this selection method just in case we're duplicating a name that already exists
    cmds.select(selected_node)
    node_type = cmds.nodeType(selected_node)
    cmds.rename(selected_node, new_name)
    new_name = cmds.ls(sl=True)[0]
    cmds.select(clear=True)
    if node_type != "stage":
        injectData(new_name, [0])
        
    populateNodeList()
    try:
        cmds.deleteUI("rename_node_window")
    except:
        pass
    
    return new_name
    
#UI to rename the selected node    
def renameWindow(*args):
 
    node_list = "tc_window|main|section_edit|node_list"

    if cmds.window("rename_node_window", exists=True):
        cmds.deleteUI("rename_node_window")   
    selected_node = cmds.textScrollList(node_list, q=True, si=True)[0]
        
    rename_node_window = cmds.window ("rename_node_window", title="Rename Node", widthHeight=(200, 100))   
    cmds.columnLayout("rename_node_window_main", parent = rename_node_window)
    cmds.rowColumnLayout("rename_options", parent="rename_node_window_main", numberOfColumns=2, cs = (2, 5), rs = (2, 5), cal=(1, "left"))
    cmds.text("Node Name: ", parent = "rename_options")
    cmds.textField( "node_name_field", parent = "rename_options", width = 150, text=selected_node)

    cmds.rowColumnLayout("rename_button_layout", numberOfColumns=3, cal=(1, "both"), cs = (2, 5), rs = (2, 5),parent="rename_node_window_main")
    cmds.text("                              ", parent="rename_button_layout")
    cmds.button( "rename_node_button", label='Rename', parent="rename_button_layout", height=50, width=100, command = partial(renameNode, selected_node))    
    cmds.setParent( '..' )
    cmds.showWindow( rename_node_window )       


#Remove the selected node in the node list and reconnect surrounding nodes appropriately    
def deleteNode(*args):
    
    def disconnectAll(node, source=True, destination=True):
        connectionPairs = []
        if source:
            conns = cmds.listConnections(node, plugs=True, connections=True, destination=False)
            if conns:
                connectionPairs.extend(zip(conns[1::2], conns[::2]))
        
        if destination:
            conns = cmds.listConnections(node, plugs=True, connections=True, source=False)
            if conns:
                connectionPairs.extend(zip(conns[::2], conns[1::2]))
        
        for srcAttr, destAttr in connectionPairs:
            cmds.disconnectAttr(srcAttr, destAttr)
            
    node_list = "tc_window|main|section_edit|node_list"
    selected_node = cmds.textScrollList(node_list, q=True, si=True)[0]
    selected_index = cmds.textScrollList(node_list, q=True, sii=True)[0]
    next_node = cmds.listConnections(selected_node, d=True, s=False, t="stage")
    if not next_node:
        next_node = cmds.listConnections(selected_node, d=True, s=False, t="script")
        
    
    prev_node = cmds.listConnections(selected_node, d=False, s=True, t="stage")
    if not prev_node:
        prev_node = cmds.listConnections(selected_node, d=False, s=True, t="script")
   
    disconnectAll(selected_node, True, True)
    
    cmds.delete(selected_node)
    next_node_type = ""
    prev_node_type = ""
    if next_node:
        next_node_type = cmds.nodeType(next_node[0])
    if prev_node:
        prev_node_type = cmds.nodeType(prev_node[0])
    prev_attr=""
    next_attr=""
    
    if prev_node_type == "stage":
        prev_attr=".nextState"
    else:
        prev_attr=".before"
        
    if next_node_type == "stage" and prev_node_type=="stage":
        next_attr=".previousState"
    elif next_node_type == "stage" and (prev_node_type=="script" or not prev_node_type):
        next_attr=".onActivateScript"
    elif next_node_type == "script" and (prev_node_type=="script" or not prev_node_type):
        next_attr=".after"
        cmds.setAttr(next_node[0]+next_attr, 'print(" ")', type="string")
     
    if prev_node and next_node:
        cmds.connectAttr(prev_node[0]+prev_attr, next_node[0]+next_attr)
        if prev_node_type == "stage" and next_node_type == "stage":
            cmds.connectAttr(prev_node[0]+".onDeactivateScript", next_node[0]+".onDeactivateScript")

    populateNodeList()    
    cmds.textScrollList(node_list, e=True, sii=selected_index-1) 
    buildEditPane()
    

#Play the tutorial from Stage 0         
def playFromStart(*args):
    try:
        mo.g_overlay_manager.controller.close()
    except:
        pass
    clearAllPreviews()
    cmds.stage(da=True)
    cmds.evalDeferred('cmds.stage("stage0", e=True, a=True)')
             
#Play the tutorial form the selected stage
def playFromCurrent(*args):
    try:
        mo.g_overlay_manager.controller.close()
    except:
        pass
    clearAllPreviews()
    selected_node = cmds.textScrollList( "tc_window|main|section_edit|node_list", q=True, si=True)[0]
    selected_node = selected_node.replace("    ", "")
    current_stage = getStage(selected_node)

    cmds.setAttr("controller.current_stage", current_stage, type="string")

    cmds.stage(da=True)
    cmds.stage(current_stage, e=True, a=True)

def setupNodeEditor(*args):
    tutorial_network = "node_editor_panelNodeEditorEd"
    
    cmds.nodeEditor(tutorial_network, e=True, addNode="", frameAll=True, run=True)
    cmds.nodeEditor(tutorial_network, e=True, frameAll=True)
    
#Opens the tutorial node network in the Node Editor
def openNodeNetwork(*args):

    if cmds.window("tutorial_network_window", exists=True):
        cmds.deleteUI("tutorial_network_window")
    
    if cmds.scriptedPanel("node_editor_panel", exists=True):
        cmds.deleteUI("node_editor_panel")
    
    graph_target = cmds.sets("GRAPH_MY_CHILDREN", q=True)
    cmds.select(graph_target)
    
    tnw = cmds.window("tutorial_network_window", title="Tutorial Network")
    form = cmds.formLayout()
    p = cmds.scriptedPanel("node_editor_panel", type="nodeEditorPanel", label="Node Editor")
    tutorial_network = p+"NodeEditorEd"
    cmds.formLayout(form, e=True, af=[(p,s,0) for s in ("top","bottom","left","right")])
    cmds.evalDeferred('setupNodeEditor()')
    cmds.showWindow(tnw)

    node_list = "tc_window|main|section_edit|node_list"
    selected_node_list = cmds.textScrollList(node_list, q=True, si=True)
    if(selected_node_list):
        selected_node = selected_node_list[0].replace("    ", "", 1)
        cmds.evalDeferred('cmds.select("'+selected_node+'")')
        cmds.evalDeferred('cmds.nodeEditor("node_editor_panelNodeEditorEd", e=True, fs=True)')

def createNewTutorial(*args):
    
    pressed = cmds.framelessDialog(title='Warning', message='Creating a new tutorial will delete your current tutorial.  Are you sure you want to proceed?', button=['Cancel','Confirm'], primary=['Confirm'])
    
    if pressed == 'Confirm':
        stage_list = cmds.ls(type="stage")
        cmds.delete(stage_list)
        tutorial_node_list = ["GRAPH_MY_CHILDREN", "_template_stage_setup", "_template_text_overlay", "_template_trigger", "_template_update_controller", "clearDialogs", "clearListeners", "clearOverlays", "closeController", "controller", "deactivateStage", "initialize", "loadTranscript", "overlayBubble", "overlayDialog", "populateText", "refreshController", "updateMenuMode", "shutdownScript", "startScript", "welcomeDialog"]
        for x in tutorial_node_list:
            try:
                cmds.delete(x)
            except:
                pass
                
        createBaseTutorial()

        

def createBaseTutorial(*args):
    template_stage_setup = """#------------------------------%NODETYPEID%stage_setup%NODETYPEID%---------------------------------------------------------------------------

#Use this to perform any necessary extra setup before a stage begins (including things that need to happen if
#the user hits the "Restart Step" button.

#Due to the nature of being a stage's initial setup, you should plug this node into the stage node
#AHEAD of any other nodes in the chain.

#------------------------------------------------------------------------------------------------------------

#-------------Customizable values------------------------------------------

#0. *DEPRECATED - You can now ignore this requirement* Replace this with the same name as this script node
#this = "_template_stage_setup"

#1. Determines visibility of the Attribute Editor at the start of the tutorial
#%INPUT%
is_ae_visible = False
#%INPUT%

#2. Determines visibility of the Channel Box at the start of the tutorial
#%INPUT%
is_cb_visible = False
#%INPUT%

#3. Determines visibility of the Outliner at the start of the tutorial
#%INPUT%
is_outliner_visible = False
#%INPUT%

#4. Determines visibility of the modeling toolkit at the start of the tutorial
#%INPUT%
is_mtk_visible = False
#%INPUT%

#5. Set up the initial menuset
#%INPUT%
menu_set = 1
#%INPUT%

#6. Set the current tool context
#%INPUT%
tool_ctx = "selectSuperContext"
#%INPUT%

#7. Set the camera for this step
#%INPUT%
shot_camera = "shot1_cam"
#%INPUT%

#8. If the step can be reset, place all reset actions in here
def reset():
#%INPUT%
	print("reset step!")
	
#%INPUT%
#-------------Advanced section---------------------------------------------

current_stage = cmds.getAttr("controller.current_stage").split("stage")[1]

#%THISID%
this = "stage"+current_stage+"_setup"
#%THISID%

#if the step is being restarted
is_reset = cmds.getAttr('controller.reset_step')
if is_reset:
	reset()

cmds.workspaceControl('AttributeEditor', e=True, visible=is_ae_visible)
cmds.workspaceControl('ChannelBoxLayerEditor', e=True, visible=is_cb_visible)
cmds.workspaceControl('Outliner', e=True, visible=is_outliner_visible)
cmds.workspaceControl('NEXDockControl', e=True, visible=is_mtk_visible) 

cmds.optionMenu("StatusLine|MainStatusLineLayout|formLayout4|flowLayout1|optionMenuForm|menuMode", e=True, sl=menu_set)
cmds.scriptNode("updateMenuMode", eb=True)

cmds.setToolTo(tool_ctx)

cmds.lookThru(shot_camera)

#%INPUT%
#<add any additional setup python code here>
#%INPUT%

#execute the next script in the chain (if there is one)
cmds.evalDeferred('cmds.scriptNode("'+this+'", ea=True)')
    
"""    

    template_text_overlay = """#------------------------------%NODETYPEID%text_overlay%NODETYPEID%---------------------------------------------------------------------------

#Displays a custom speech bubble at custom X, Y coordinates.  Default values place the word bubble at the 
#bottom center of the screen (ideal for primary "speech" style instructions).

#Use this to customize the placement and orientation of a speech bubble on screen.

#------------------------------------------------------------------------------------------------------------

#-------------Customizable values------------------------------------------

#1. *DEPRECATED - You can now ignore this requirement* Replace this with the same name as this script node
#this = "stage1_text_overlay"

#2. Replace "Hello World" with the text for this speech bubble.  HTML tags are supported for formatting.
#Note: This is disabled for this tutorial (text is instead sourced from the "populateText" script.
#%INPUT%
html_text = """+ '"""<b>Hello World</b>"""\n' + """#%INPUT%

#3. Set to 'False' if you'd like to position the overlay via a % of the main window size, rather than an absolute screen coordinate position
#%INPUT%
is_offset_absolute = True
#%INPUT%

#4. X position
#%INPUT%
x_offset = 0
#%INPUT%

#5. Y position
#%INPUT%
y_offset = 150
#%INPUT%

#6. Main window poisition to offset X and Y position from (valid values: topleft, top, topright, left, center, right, bottomleft, bottom, bottomright, or any valid UI component).
#This only has an effect when is_offset_absolute = True.
#Note: To find various UI components, use the MEL/Python command lsUI with either the -controls, -panels, or -windows flag (https://help.autodesk.com/cloudhelp/2022/ENU/Maya-Tech-Docs/Commands/lsUI.html)
#Note2: This only has an effect on non-dialog overlays.  Dialog-style overlays are always placed relative to the top-left of the main Maya window.
#%INPUT%
rel_to = "bottom"
#%INPUT%

#7. Bubble tail direction: tail_orientation (valid values: top, bottom, left, right)
#%INPUT%
tail_orientation = "top"
#%INPUT%

#8. Bubble tail position (valid values: 0 to 1)
#%INPUT%
tail_position = 0.5
#%INPUT%

#9. Bubble maximum width (before wrapping)
#%INPUT%
overlay_width = 500
#%INPUT%

#10. Set this to "True" to use a dialog-style overlay.  Dialogs can be moved and closed by the user
#%INPUT%
dialog_style = False
#%INPUT%

#-------------Advanced section---------------------------------------------

import moverlay as mo
from PySide2.QtCore import QPoint

lang = cmds.about(uil=True)

current_stage = cmds.getAttr("controller.current_stage").split("stage")[1]

#%THISID%
this = "stage"+current_stage+"_text_overlay"
#%THISID%

#set and apply initial style to text
style=""
if not dialog_style:
	style = cmds.getAttr("controller.speech_html_style")
else:
	style = cmds.getAttr("controller.reference_html_style")
text="<span style = "+style+" >"+html_text+"</span>"

con_browse = QPoint(0, 0)
UI_success = False
cardinal_points = ["topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright"]

#check if the user has indicated a valid UI component to place the overlay relative to
if not rel_to in cardinal_points :
	try:
		con_browse=mo.getUIPosition(rel_to)
		UI_success = True
	except:
		print (UI_component+" not found!")

#set the various overlay values based on user's input above
cmds.setAttr('controller.overlay_text', text, type="string")
cmds.setAttr('controller.overlay_style', "speech", type="string")

#if user has specified a valid part of the UI to place relative to
if (UI_success):
	cmds.setAttr('controller.is_offset_absolute', True)
	cmds.setAttr('controller.overlay_rel_to', "topleft", type="string")
	cmds.setAttr('controller.overlay_offset_x', con_browse.x()+x_offset)
	cmds.setAttr('controller.overlay_offset_y', con_browse.y()+y_offset)
else:
	cmds.setAttr('controller.is_offset_absolute', is_offset_absolute)
	cmds.setAttr('controller.overlay_rel_to', rel_to, type="string")
	cmds.setAttr('controller.overlay_offset_x', x_offset)
	cmds.setAttr('controller.overlay_offset_y', y_offset)

cmds.setAttr('controller.overlay_tail_direction', tail_orientation, type="string")
cmds.setAttr('controller.overlay_tail_position', tail_position)
cmds.setAttr('controller.overlay_width', overlay_width)

#run the appropriate script to display the chosen overlay style
if not dialog_style:
	cmds.scriptNode("overlayBubble", executeBefore=True)
else:
	cmds.scriptNode("overlayDialog", executeBefore=True)

#execute the next script in the chain (if there is one)
cmds.scriptNode(this, ea=True)
    
    """

    template_trigger = """#------------------------%NODETYPEID%trigger%NODETYPEID%---------------------------------------------------------------------------------

#Locks the controller's 'Next' button until a specified trigger is activated.

#Use this for steps where you want the user to do something before they're allowed to move on.


#------------------------------------------------------------------------------------------------------------

#-------------Customizable values------------------------------------------

#1. *DEPRECATED - You can now ignore this requirement* Replace this with the same name as this script node
#this = "_template_event_trigger"

#2. Defines the type of trigger.  Valid values are "Attribute Change", "Condition", or "Event"
#%INPUT%
trigger_type = "Event"
#%INPUT%

#3. Define the trigger event that must happen before the user can continue.  In this example, the trigger will evaluate whenever the scene is at rest.
#Hint: To view a list of available event triggers, run the MEL command "scriptJob -le", or see the documentaiton here: https://help.autodesk.com/cloudhelp/2022/ENU/Maya-Tech-Docs/Commands/scriptJob.html
#%INPUT%
trigger_ID = "idle"
#%INPUT%

#4. Define what happens when the trigger is activated.  The default action is to print a diagnostic message and move to the next step automatically.
def activateTrigger():	
	
#%INPUT%
	#Replace this if statement with your own conditional check (see ? for help)
	if True:
		#Replace this print statement with any automations you want to happen if the conditional check is true
		print("Triggered!")
	
		#automatically move to the next step if the conditional check is true (you can delete this line to make the user have to click 'Next' to move on)
		cmds.setAttr('controller.push_next', True)
#%INPUT%

#-------------Advanced section---------------------------------------------

import moverlay as mo

current_stage = cmds.getAttr("controller.current_stage").split("stage")[1]

#%THISID%
this = "stage"+current_stage+"_event_trigger"
#%THISID%


job_num = ""

if trigger_type == "Attribute Change":
	attribute_list = trigger_ID.split(", ")

	for attribute in attribute_list:
		job_num=cmds.scriptJob( ac = [attribute, activateTrigger])
		#add the job to the list of current event listners
		mo.listener_list.append(job_num)

elif trigger_type == "Connection Change":
	attribute_list = trigger_ID.split(", ")

	for attribute in attribute_list:
		job_num=cmds.scriptJob( con = [attribute, activateTrigger])
		#add the job to the list of current event listners
		mo.listener_list.append(job_num)

elif trigger_type == "Condition":
	job_num=cmds.scriptJob( ct = [trigger_ID, activateTrigger])
	#add the job to the list of current event listners
	mo.listener_list.append(job_num)

else:
	job_num=cmds.scriptJob( event = [trigger_ID, activateTrigger])
	#add the job to the list of current event listners
	mo.listener_list.append(job_num)

#execute the next script in the chain (if there is one)
cmds.evalDeferred('cmds.scriptNode("'+this+'", ea=True)')
    
    """
    
    template_update_controller = """#------------------------------%NODETYPEID%update_controller%NODETYPEID%---------------------------------------------------------------------------

#Use this to update the contents of the controller.

#------------------------------------------------------------------------------------------------------------

#-------------Customizable values------------------------------------------

#1. *DEPRECATED - You can now ignore this requirement* Replace this with the same name as this script node
#this = "_template_update_controller"

#2. Replace "Step title" with the text for the controller's title bar.  HTML tags are supported for formatting.
#%INPUT%
title = """+'"""Step title"""\n'+"""#%INPUT%

#3. Replace "Step body text" with the text for the controller's body.  HTML tags are supported for formatting.
#%INPUT%
description = """+'"""Step description"""\n'+"""#%INPUT%

#4. Replace "Restart Step" with the text for left button.
#%INPUT%
button0 = "Restart Step"
#%INPUT%

#5. Replace "Next" with the text for right button.
#%INPUT%
button1 = "Next"
#%INPUT%

#6. Set this to 'True' to hide the 'Reset' button
#%INPUT%
disable_reset = False
#%INPUT%

#7. Set this to 'True' to lock the 'Next' button
#%INPUT%
disable_next = False
#%INPUT%

#8. Set this to 'True' to increment the step counter
#%INPUT%
increment_step = True
#%INPUT%

#9. Set the x offset (in % of window size)
#%INPUT%
x_offset = 80
#%INPUT%

#10. Set the y offset (in % of window size)
#%INPUT%
y_offset = 60
#%INPUT%

#-------------Advanced section---------------------------------------------
import moverlay as mo
import shiboken2

current_stage = cmds.getAttr("controller.current_stage").split("stage")[1]

#%THISID%
this = "stage"+current_stage+"_update_controller"
#%THISID%

#if the controller doesn't exist, we'll need to create a controller and set the current stage
if not shiboken2.isValid(mo.g_overlay_manager.controller):
	cmds.scriptNode('controller', eb=True)
	check = this
	node_type = ""
	while not node_type == "stage":
		check = cmds.listConnections(check+".before")[0]
		node_type = cmds.nodeType(check)
	cmds.setAttr("controller.current_stage", check, type="string")

#update the controller based on the user settings above
html_text = title+"//"+description
cmds.setAttr('controller.overlay_text', html_text, type="string")
cmds.setAttr('controller.button0', button0, type="string")
cmds.setAttr('controller.button1', button1, type="string")

mo.g_overlay_manager.controller.theDialog().moveToScreenPos(mo.g_overlay_manager.getMainWindow().mapToGlobal(mo.coordinateFromPercentage(x_offset, y_offset)))

cmds.setAttr('controller.disable_next', disable_next)
cmds.setAttr('controller.disable_reset', disable_reset)
cmds.scriptNode("refreshController", executeBefore=True)

#don't increment the step counter if user doesn't want to or step is being reset
is_reset = cmds.getAttr('controller.reset_step')
if increment_step and not is_reset:
	mo.g_overlay_manager.controller.progressBar().increment()
cmds.setAttr('controller.reset_step', False)

#execute the next script in the chain (if there is one)
cmds.scriptNode(this, ea=True)
    
    """
    
    clear_dialogs = """#---------------------------------------------------------------------------------------------------------

#Use this to clear all overlay dialogs off the screen.

#------------------------------------------------------------------------------------------------------------


import moverlay as mo

for i in mo.dialog_list:
	try:
		i.deleteLater()
	except:
		pass
	
del mo.dialog_list[:]
    """
    
    clear_listeners = """#---------------------------------------------------------------------------------------------------------

#Execute this to clean up after any listeners you may have used during a stage.

#------------------------------------------------------------------------------------------------------------

import moverlay as mo

for i in mo.listener_list:
	cmds.scriptJob(kill=i)

del mo.listener_list[:]
    
    """
    
    clear_overlays = """#---------------------------------------------------------------------------------------------------------

#Use this to clear all overlay bubbles off the screen.

#------------------------------------------------------------------------------------------------------------

import moverlay as mo
manage = mo.maya.overlayManager()
manage.deleteAll()
    
    """
    
    close_controller = """#---------------------------------------------------------------------------------------------------------

#This script cleans up after the tutorial when you close the controller window (but stay in the scene file).

#When executed, it will destroy the controller and free up any memory being used by the tutorial.

#------------------------------------------------------------------------------------------------------------

import moverlay as mo    

#clear all leftover overlays
cmds.scriptNode("clearOverlays", executeBefore=True)

#destroy any dialog boxes
cmds.scriptNode("clearDialogs", eb=True)

#clear all active event listeners
cmds.scriptNode("clearListeners", eb=True)

#kill any protected scriptJobs (like the controller)
mo.g_overlay_manager.controller.deleteLater()
for i in mo.protected_listener_list:
    cmds.scriptJob(kill=i)
del mo.protected_listener_list[:]

#make the Channel Box and Outliner visible
cmds.workspaceControl('ChannelBoxLayerEditor', e=True, visible=1)
cmds.workspaceControl('Outliner', e=True, visible=1)

#stop execution of all stage nodes
cmds.stage(da=True)

print("shutting down the tutorial")
    """
    
    tutorial_controller = """#---------------------------------------------------------------------------------------------------------

#This script contains all the functionality for the main controller.  

#When executed, it will display the main controller.

#------------------------------------------------------------------------------------------------------------

from functools import partial
from PySide2.QtCore import QPoint

#-------------------------Helper functions-------------------------------------

#if user presses "restart step", set "reset_step" status to true, then deactivate the current step and reactivate it again
def pressRestart(dialog, index):
	cmds.setAttr('controller.reset_step', True)
	current_stage = cmds.getAttr('controller.current_stage')
	cmds.stage(current_stage, e=True, d=True)
	cmds.stage(current_stage, e=True, a=True)

#push the next stage (based on the "current_stage" attribute)
#Because this is run as a scriptJob, it needs to contain all its own dependencies (including duplicate procedures) 
def pressNext(dialog, index):
	import moverlay as mo
	def nextStage(dialog, index):
		current = cmds.getAttr('controller.current_stage')
		cmds.stage(current, edit=True, next=True)

	nextStage(dialog, index)

#force the next stage if push_next is true
#Because this is run as a scriptJob, it needs to contain all its own dependencies (including duplicate procedures) 
def forceNext(dialog, index):
	import moverlay as mo
	def nextStage(dialog, index):
		current = cmds.getAttr('controller.current_stage')
		cmds.stage(current, edit=True, next=True)

	cond = cmds.getAttr('controller.push_next')
	if(cond==True):
		nextStage(dialog, index)
		cmds.setAttr('controller.push_next', False)

#destroy the dialog box when the X button is pushed
def pressClosed(dialog):
	cmds.scriptNode('closeController', eb=True)

#-------------------------Main script-------------------------------------

#kill any scriptJobs from previous tutorials
for i in mo.protected_listener_list:
	cmds.scriptJob(kill=i)
del mo.protected_listener_list[:]

#set up controller and assign it to a global variable
mo.g_overlay_manager = mo.maya.overlayManager()
mo.g_overlay_manager.controller = mo.progressDialog.ProgressDialog(mo.g_overlay_manager.getMainWindow())
dropShadow = mo.higDropShadow.HIGDropShadow(mo.g_overlay_manager.getMainWindow(), mo.g_overlay_manager.controller)
#mo.g_overlay_manager.controller.setTitle("title")
#mo.g_overlay_manager.controller.setBodyText("description")

button0 = cmds.getAttr('controller.button0')
button1 = cmds.getAttr('controller.button1')
mo.g_overlay_manager.controller.button(0).setText(button0)
mo.g_overlay_manager.controller.button(1).setText(button1)

#set up button commands and progress bar
mo.g_overlay_manager.controller.setupButton(0, button0, pressRestart)
mo.g_overlay_manager.controller.setupButton(1, button1, pressNext)
mo.g_overlay_manager.controller.setCloseCallback(pressClosed)
num_steps = len(cmds.ls(type="stage"))-2
mo.g_overlay_manager.controller.progressBar().resetSteps(0, num_steps)

current_stage = cmds.getAttr("controller.current_stage")
prev_stage = cmds.listConnections(current_stage+".previousState")

prev_stage_list=[]
#increment the counter appropriately if we're starting mid-tutorial
while prev_stage:
	current_stage = prev_stage[0]
	prev_stage_list.append(current_stage)
	prev_stage = cmds.listConnections(current_stage+".previousState")

for x in prev_stage_list[:-2]:
	mo.g_overlay_manager.controller.progressBar().increment()

#size and position the controller
mo.g_overlay_manager.controller.theDialog().resize(mo.utils.DPIScale(180), mo.utils.DPIScale(250))
mo.g_overlay_manager.controller.theDialog().moveToScreenPos(mo.g_overlay_manager.getMainWindow().mapToGlobal(mo.coordinateFromPercentage(80, 60)))
cmds.setAttr('controller.disable_next', False)
cmds.setAttr('controller.disable_reset', True)

#set up a listener for steps that force successful completion on condition and attach it to the button_parent window
jobnum = cmds.scriptJob(attributeChange=['controller.push_next', partial(forceNext, mo.g_overlay_manager.controller, 0)], kws=True)
mo.protected_listener_list.append(jobnum)

#refresh the controller
mo.g_overlay_manager.controller.showAndRaise()

print ("controller finished")
    
    """
    
    deactivate_stage = """#---------------------------------------------------------------------------------------------------------

#This script handles cleaning up after a stage is complete.

#Typically you can daisy chain just one of these to the stage nodes' "Deactivate Script".

#------------------------------------------------------------------------------------------------------------

import maya.cmds as cmds
import moverlay as mo

#clear all active event listeners (except the controller)
cmds.scriptNode("clearListeners", eb=True)

#check if user is currently resetting a step
is_reset = cmds.getAttr('controller.reset_step')

#setup the next stage as current if user is NOT resetting the current stage
if not is_reset:
	#swap build_controller's current stage with the next stage
	temp0 = cmds.getAttr('controller.current_stage')
	print("deactivating: "+temp0)
	temp = cmds.listConnections(temp0+'.nextState')
	temp2 = temp[0]
	cmds.setAttr('controller.current_stage', temp2, type="string")

#kill previous hint bubbles
cmds.scriptNode("clearDialogs", eb=True)

#clear all leftover overlays
cmds.scriptNode("clearOverlays", executeBefore=True)
    
    """
    
    initialize = """#-----------------------------------%NODETYPEID%initialize%NODETYPEID%----------------------------------------------------------------------

#This script handles all the initial setup for the tutorial.

#When executed, it will re-configure scene values, reset UI configurations, create a new overlay manager and 
#add helper functions to it, and create global variables needed to manage the various tutorial processes.

#------------------------------------------------------------------------------------------------------------

#-------------Customizable values------------------------------------------

#1. Determines visibility of the Attribute Editor at the start of the tutorial
#%INPUT%
is_ae_visible = False
#%INPUT%

#2. Determines visibility of the Channel Box at the start of the tutorial
#%INPUT%
is_cb_visible = False
#%INPUT%

#3. Determines visibility of the Outliner at the start of the tutorial
#%INPUT%
is_outliner_visible = False
#%INPUT%

#4. Determines visibility of the modeling toolkit at the start of the tutorial
#%INPUT%
is_mtk_visible = False
#%INPUT%

#5. Set up the default speech bubble style
#%INPUT%
default_speech_style = '"color: #3C3C3C; font-size: 16pt; font-weight: normal; font-style: normal; font-family: Artifakt Element"'
#%INPUT%

#6. Set up the default dialog box style
#%INPUT%
default_dialog_style = '"color: white; font-size: 13pt; font-weight: normal; font-style: normal; font-family: Artifakt Element"'
#%INPUT%

#7. Set up the default controller text style
#%INPUT%
default_control_style = '"color: white; font-size: 13pt; font-weight: normal; font-style: normal; font-family: Artifakt Element"'
#%INPUT%

#8. Set up your initial camera
#%INPUT%
shot_camera = "shot1_cam"
#%INPUT%

#9. Set up the initial menuset
#%INPUT%
menu_set = 1
#%INPUT%

#10. Set the current tool context
#%INPUT%
tool_ctx = "selectSuperContext"
#%INPUT%

#-------------Advanced section---------------------------------------------
import maya.cmds as cmds
import sys, imp
import moverlay as mo
import maya.mel

from PySide2.QtCore import QSize, QPoint
from PySide2.QtGui import QColor
from PySide2 import QtWidgets
from functools import partial
import maya.plugin.timeSliderBookmark.timeSliderBookmark as tsbm

#-------------------------Helper functions-------------------------------------

#adapts a point to the current DPI of the OS
def getCoordinate(x_percentage, y_percentage):
	import moverlay as mo
	from PySide2.QtCore import QPoint
	mainWindow = mo.maya.getMainMayaWindow()
	width = mainWindow.frameGeometry().width()
	height = mainWindow.frameGeometry().height()
	x_pos = (width/100) *x_percentage
	y_pos = (height/100) *y_percentage
	return QPoint(x_pos, y_pos)

#find the exact position of a UI element
def getUIPosition(uiName):
	import moverlay as mo
	from PySide2 import QtWidgets, QtCore
	import maya.OpenMayaUI as omui
	import shiboken2

	def getMainMayaWindow():		
		#returns the main maya window
		ptr = omui.MQtUtil.mainWindow()
		return shiboken2.wrapInstance(int(ptr), QtWidgets.QMainWindow)

	mainWindow = getMainMayaWindow()
	parentTopLeft = mainWindow.frameGeometry().topLeft()
	widgetptr = omui.MQtUtil.findControl(uiName)
	widget = shiboken2.wrapInstance(int(widgetptr), QtWidgets.QWidget)
	rect = widget.rect()
	screenRect = QtCore.QRect()
	screenRect.setTopLeft(widget.mapToGlobal(rect.topLeft()))
	screenRect.setSize(rect.size())
	screenRect.translate(-parentTopLeft.x(), -parentTopLeft.y())
	return QtCore.QPoint(screenRect.x()/mo.utils.DPIScale(1), screenRect.y()/mo.utils.DPIScale(1))

#assign these helper functions to moverlay so we can access them in other scriptNodes
mo.coordinateFromPercentage = getCoordinate
mo.getUIPosition = getUIPosition

#-------------------------Main script-------------------------------------

#setup global event listener lists for later use
try:
    om = mo.g_overlay_manager
except:
    mo.g_overlay_manager=""

try:
	ll = mo.listener_list
except:
    mo.listener_list=[]

try:
    pll = mo.protected_listener_list
except:
	mo.protected_listener_list=[]

try:
    dl = mo.dialog_list
except:	
	mo.dialog_list=[]

cmds.scriptNode("loadTranscript", eb=True)
	
#clean up any old items from previous iterations
cmds.scriptNode("clearOverlays", executeBefore=True)
cmds.scriptNode("clearDialogs", executeBefore=True)

cmds.optionMenu("StatusLine|MainStatusLineLayout|formLayout4|flowLayout1|optionMenuForm|menuMode", e=True, sl=menu_set)
maya.mel.eval('updateMenuMode')
maya.mel.eval('updateMenuModeUI')

cmds.setToolTo(tool_ctx)

#%INPUT%

#%INPUT%

#start the state machine's current state storage
cmds.setAttr('controller.current_stage', "stage0", type="string")

#reset scene elements
cmds.setAttr('controller.push_next', 0)
cmds.setAttr('controller.disable_next', False)
cmds.setAttr('controller.disable_reset', True)
cmds.setAttr('controller.reset_step', False)

#hide all editors
cmds.workspaceControl('AttributeEditor', e=True, visible=is_ae_visible)
cmds.workspaceControl('ChannelBoxLayerEditor', e=True, visible=is_cb_visible)
cmds.workspaceControl('Outliner', e=True, visible=is_outliner_visible)
cmds.workspaceControl('NEXDockControl', e=True, visible=is_mtk_visible) 

#set font sizes and styles
cmds.setAttr('controller.speech_html_style', default_speech_style, type="string")
cmds.setAttr('controller.instruct_html_style', default_control_style, type="string")
cmds.setAttr('controller.reference_html_style', default_dialog_style, type="string")

#switch to camera 0
cmds.lookThru (shot_camera)

#display the Welcome Dialog controller
cmds.scriptNode('initialize', executeAfter=True)
    
    """
    
    load_transcript = """#-----------------------------------------------------------------------------------------------------------------------------------------

#This script defines various language transcripts for use when a tutorial is available in multiple languages.
#You can enable controller.use_dictionary to source text from here (thus bypassing the text in each individual script node)

#-----------------------------------------------------------------------------------------------------------------------------------------

import moverlay as mo
#%EN
transcript_EN = {'stage0': {'dialogTitle': ['Welcome to my Tutorial'], 'dialogBody': ['Click <b>Start</b> to begin.'], 'bubbleText': [], 'hintText': [['Restart Step', 'Start']]},}
#%EN
#%JP
transcript_JP = {}
#%JP
#%CN
transcript_CN = {}
#%CN

#grab the current product language
lang = mo.sys_lang

if(lang=="zh_CN"):
    mo.transcript = transcript_CN
elif(lang=="ja_JP"):
    mo.transcript = transcript_JP
else:
    mo.transcript = transcript_EN	
    
"""
    
    overlay_bubble = """#---------------------------------------------------------------------------------------------------------

#This script handles displaying word bubble-style overlays  

#Execute this to display a word bubble on screen with characteristics derived from the following sources:
#Text: controller.overlay_text
#Text font & style: controller.overlay_style
#X position: controller.overlay_offset_x 
#Y position: controller.overlay_offset_y
#Position relative to: controller.overlay_rel_to
#Bubble tail direction: controller.overlay_tail_direction
#Bubble tail position: controller.overlay_tail_position
#Bubble maximum width (before wrapping): controller.overlay_width

#------------------------------------------------------------------------------------------------------------


import maya.cmds as cmds

import sys, imp
import moverlay as mo
from PySide2.QtCore import QSize
from PySide2.QtGui import QColor

#-------------------------Helper functions-------------------------------------

#Always reset back to a regular speech bubble at the end of this
def reset():
	cmds.setAttr('controller.is_offset_absolute', True)
	cmds.setAttr('controller.overlay_offset_x', 0)
	cmds.setAttr('controller.overlay_offset_y', 150)
	cmds.setAttr('controller.overlay_rel_to', "bottom", type="string")
	cmds.setAttr('controller.overlay_style', "speech", type="string")
	cmds.setAttr('controller.overlay_tail_direction', "top", type="string")
	cmds.setAttr('controller.overlay_tail_position', 0.5)
	cmds.setAttr('controller.overlay_width', 700)

#-------------------------Main script-------------------------------------

manage = mo.maya.overlayManager()

#get/set offset position
x_offset = cmds.getAttr('controller.overlay_offset_x')
y_offset = cmds.getAttr('controller.overlay_offset_y')

#if user is defining position by main window %age rather than absolute
if not (cmds.getAttr('controller.is_offset_absolute')):
	percent_to_pos = manage.getMainWindow().mapToGlobal(mo.coordinateFromPercentage(x_offset, y_offset))
	x_offset = percent_to_pos.x()
	y_offset = percent_to_pos.y()
	cmds.setAttr('controller.overlay_rel_to', "topleft", type="string")

offset = QSize(mo.utils.DPIScale(x_offset), mo.utils.DPIScale(y_offset))

#position the dialog box
od = mo.overlayDef.OverlayDef(offset=offset)

#get/set UI relative reference point for bubble positioning
r_to = cmds.getAttr('controller.overlay_rel_to')
if (r_to == "center"):
	od.attachment = mo.enums.RelTo.Center
elif (r_to == "topleft"):
	od.attachment = mo.enums.RelTo.TopLeft
elif (r_to == "left"):
	od.attachment = mo.enums.RelTo.Left
elif (r_to == "bottomleft"):
	od.attachment = mo.enums.RelTo.BottomLeft
elif (r_to == "top"):
	od.attachment = mo.enums.RelTo.Top
elif (r_to == "topright"):
	od.attachment = mo.enums.RelTo.TopRight
elif (r_to == "right"):
	od.attachment = mo.enums.RelTo.Right
elif (r_to == "bottomright"):
	od.attachment = mo.enums.RelTo.BottomRight
elif (r_to == "bottom"):
	od.attachment = mo.enums.RelTo.Bottom


#set bubble BG color
od.bgColor = QColor(217, 217, 217, 255)

#get/set the overlay style
style=cmds.getAttr('controller.overlay_style')
if (style == "speech"):
	od.style = mo.enums.OverlayStyle.SpeechBubble
	od.bgColor = QColor(217, 217, 217, 255)
elif (style == "tooltip"):
	od.style = mo.enums.OverlayStyle.ToolTip
	od.bgColor = QColor(71, 71, 71, 255)
elif (style == "darkening"):
	od.style = mo.enums.OverlayStyle.Darkening
else:
	od.style = mo.enums.OverlayStyle.Custom

#populate bubble with text
overlay = manage.createOverlay(od)
htmltext = ""

if cmds.getAttr("controller.use_dictionary"):
	#get the overlay text from the populateText dictionary
	cmds.setAttr('controller.text_query', 'bubbleText', type="string")
	cmds.scriptNode('populateText', executeBefore=True)
	html_text = cmds.getAttr('controller.overlay_text')

	#apply speech bubble style to text
	text_style = cmds.getAttr("controller.speech_html_style")
	text="<span style = "+text_style+" >"+html_text+"</span>"
	cmds.setAttr('controller.overlay_text', text, type="string")

htmltext = cmds.getAttr('controller.overlay_text')
label=overlay.setAsLabel(htmltext)

#determine if bubble needs to be wrapped (i.e. too big)
label.setWordWrap(False)
overlay_width = mo.utils.DPIScale(cmds.getAttr('controller.overlay_width'))
if label.sizeHint().width() > overlay_width:
    label.setWordWrap(True)
    label.setFixedWidth(overlay_width)
else:
    label.setWordWrap(False)

#add the tail if overlay style is "speech"
if (style == "speech"):
	t_dir = cmds.getAttr('controller.overlay_tail_direction')
	t_pos = cmds.getAttr('controller.overlay_tail_position')
	
	if(t_dir == "top"):
		overlay.addSpeechBubbleTail(mo.enums.Direction.Top, t_pos)
	elif(t_dir == "left"):
		overlay.addSpeechBubbleTail(mo.enums.Direction.Left, t_pos)
	elif(t_dir == "bottom"):
		overlay.addSpeechBubbleTail(mo.enums.Direction.Bottom, t_pos)
	else:
		overlay.addSpeechBubbleTail(mo.enums.Direction.Right, t_pos)

#display the overlay bubble
manage.showAll()

#reset back to default values for the next bubble
reset()
    
    """
    
    overlay_dialog = """#---------------------------------------------------------------------------------------------------------

#This script handles displaying word bubble-style overlays  

#Execute this to display a word bubble on screen with characteristics derived from the following sources:
#Text: controller.overlay_text
#Text font & style: controller.overlay_style
#X position (as a window %age): controller.overlay_offset_x 
#Y position (as a window %age): controller.overlay_offset_y
#Position relative to: controller.overlay_rel_to
#Bubble tail direction: controller.overlay_tail_direction
#Bubble tail position: controller.overlay_tail_position
#Bubble maximum width (before wrapping): controller.overlay_width
#------------------------------------------------------------------------------------------------------------
import maya.cmds as cmds
from functools import partial

import sys, imp
import moverlay as mo
from PySide2.QtCore import QSize
from PySide2.QtGui import QColor

#Always reset back to a regular speech bubble
def reset():
	cmds.setAttr('controller.overlay_offset_x', 0)
	cmds.setAttr('controller.overlay_offset_y', 150)
	cmds.setAttr('controller.overlay_rel_to', "bottom", type="string")
	cmds.setAttr('controller.overlay_style', "speech", type="string")
	cmds.setAttr('controller.overlay_tail_direction', "top", type="string")
	cmds.setAttr('controller.overlay_tail_position', 0.5)

#destroy the dialog box when the X button is pushed
def pressClosed(dialog):
	dialog.theDialog().deleteLater()

#get/set offset position
x_offset = cmds.getAttr('controller.overlay_offset_x')
y_offset = cmds.getAttr('controller.overlay_offset_y')

manager = mo.maya.overlayManager()
dialog = mo.higDialog.HIGDialog(manager.getMainWindow())
hinDropShadow = mo.higDropShadow.HIGDropShadow(manager.getMainWindow(), dialog)

#Add the dialog to the global list of dialog boxes
mo.dialog_list.append(dialog)

tl = cmds.internalVar(mid=True)
tl = tl+"/resources/tutorial_resources/"

style = cmds.getAttr("controller.reference_html_style")
htmltext = ""

if cmds.getAttr("controller.use_dictionary"):
	#get the overlay text from the populateText dictionary
	cmds.setAttr('controller.text_query', 'bubbleText', type="string")
	cmds.scriptNode('populateText', executeBefore=True)
	html_text = cmds.getAttr('controller.overlay_text')

	#apply speech bubble style to text
	text="<span style = "+style+" >"+html_text+"</span>"
	cmds.setAttr('controller.overlay_text', text, type="string")

htmltext = cmds.getAttr('controller.overlay_text')

label = dialog.setAsLabel(htmltext)
#label.setMaximumWidth(mo.utils.DPIScale(100))
dialog.setCloseCallback(pressClosed)

#dialog.theDialog().setMaximumWidth(mo.utils.DPIScale(100))

#position the dialog box
if not (cmds.getAttr('controller.is_offset_absolute')):
	dialog.theDialog().moveToScreenPos(manager.getMainWindow().mapToGlobal(mo.coordinateFromPercentage(x_offset, y_offset)))
else:
	dialog.theDialog().moveToScreenPos(manager.getMainWindow().mapToGlobal(QPoint(mo.utils.DPIScale(x_offset), mo.utils.DPIScale(y_offset))))

dialog.showAndRaise()

reset()
    """
    
    populate_text = """#---------------------------------------------------------------------------------------------------------------------------------------

#Used in conjunction with loadTranscript to load text from a dictionary rather than from each individual script node.
#Main use is for supporting multiple languages.

#---------------------------------------------------------------------------------------------------------------------------------------

import base64
dpi_scale = int(mo.utils.DPIScale(100))

#grab the text at the specified dictionary entry and return it     
def getTextFor(stageName, textObject):

    #grab the current product language
    lang = mo.sys_lang

    #check if the dictionary term is a list object - if so, we need to grab the list items individually
    if (isinstance(mo.transcript[stageName][textObject][0], list)):
        delineated_list=""
        for x in mo.transcript[stageName][textObject][0]:
            #any language other than english needs to be run through a UTF decoder
            text_string = mo.transcript[stageName][textObject].pop(0)
            mo.transcript[stageName][textObject].append(text_string)

            if isinstance(text_string, list):
                for y in text_string:
                    if (lang!="en_US"):
                        delineated_list=delineated_list+base64.b64decode(y).decode("utf-8")+"//"
                    else:
                        delineated_list=delineated_list+y+"//"
            else:
                if (lang!="en_US"):
                    delineated_list=delineated_list+base64.b64decode(x).decode("utf-8")+"//"
                else:
                    delineated_list=delineated_list+x+"//"
            
        return delineated_list
    #if the dictionary term is just a string, return it
    else:
        #any language other than english needs to be run through a UTF decoder
        text_string = mo.transcript[stageName][textObject].pop(0)
        print(mo.transcript[stageName][textObject])
        mo.transcript[stageName][textObject].append(text_string)
        print(mo.transcript[stageName][textObject])
        if (lang!="en_US"):
            return base64.b64decode(text_string).decode("utf-8")
        else:
            return text_string
        

current = cmds.getAttr('controller.current_stage')
type = cmds.getAttr('controller.text_query')

#query the text for the current dictionary item
text = getTextFor(current, type)

#put the text in an attribute wher the overlayBubble / overlayDialog scripts can get them 
cmds.setAttr('controller.overlay_text', text, type="string")

"""
    
    refresh_controller = """#---------------------------------------------------------------------------------------------------------

#This script handles refreshing the controller.  

#You shouldn't execute this script directly.  Instead, use updateController (which then calls this script automatically)

#------------------------------------------------------------------------------------------------------------

import moverlay as mo


#check if dialog is being hidden, and if so, hide the controller
hide_controller = cmds.getAttr('controller.hide_controller')
if(hide_controller):
	mo.g_overlay_manager.controller.theDialog().hide()

#if not being hidden, perform other updates
else:
	#enable/disable Next button
	disable_next = cmds.getAttr('controller.disable_next')
	bn=mo.g_overlay_manager.controller.button(1)
	if(disable_next):
		bn.setEnabled(False)
	else:
		bn.setEnabled(True)

	#enable/disable Reset button
	disable_reset = cmds.getAttr('controller.disable_reset')
	br=mo.g_overlay_manager.controller.button(0)
	if(disable_reset):
		br.setEnabled(False)
		br.setVisible(False)
	else:
		br.setEnabled(True)
		br.setVisible(True)
	
	#update the controller text	
	style = cmds.getAttr("controller.instruct_html_style")
	html_text = cmds.getAttr('controller.overlay_text').split("//")
	title=""
	description=""
	#if there's title/body text to update
	if (html_text[0]):
		title = "<p style = "+style+" ><h3>"+html_text[0]+"</h3></p>"
		mo.g_overlay_manager.controller.setTitle(title)
	try:
		if (html_text[1]):	
			description = "<p style = "+style+" >"+html_text[1]+"</p>"
			mo.g_overlay_manager.controller.setBodyText(description)
	except:
		pass

	button0 = cmds.getAttr('controller.button0')
	button1 = cmds.getAttr('controller.button1')
	mo.g_overlay_manager.controller.button(0).setText(button0)
	mo.g_overlay_manager.controller.button(1).setText(button1)
	
	#refresh the controller
	mo.g_overlay_manager.controller.showAndRaise()
    
    """
    
    pin_ae = """global int $gAutoUpdateAttrEdFlag;
$gAutoUpdateAttrEdFlag = 0;
showEditorSetListType("auto");
$gAutoUpdateAttrEdFlag = 1;
showEditorSetListType("auto");"""
    
    shutdown_script = """#---------------------------------------------------------------------------------------------------------

#This script cleans up after the tutorial once you open a new file.

#------------------------------------------------------------------------------------------------------------

import moverlay as mo

#clear all leftover overlays
cmds.scriptNode("clearOverlays", executeBefore=True)

#destroy any dialog boxes
cmds.scriptNode("clearDialogs", eb=True)

#clear all active event listeners (except the controller)
cmds.scriptNode("clearListeners", eb=True)

#kill any scriptJobs from previous tutorials
for i in mo.protected_listener_list:
	cmds.scriptJob(kill=i)
del mo.protected_listener_list[:]

#destroy the controller
try:
	mo.g_overlay_manager.controller.theDialog().deleteLater()
except:
	print("controller already deleted")

cmds.modelEditor('modelPanel4', e=True, grid=True)
#end of script
    """
    
    start_script = """import moverlay as mo

#grab the current product language
mo.sys_lang = `about -uil`;
cmds.stage("stage0", e=True, a=True)

print("begin the tutorial");
"""

    unpin_ae = """global int $gAutoUpdateAttrEdFlag;
$gAutoUpdateAttrEdFlag = 0;
showEditorSetListType("auto");"""
    
    update_menu_mode = """updateMenuMode;
updateMenuModeUI;"""

    welcome_dialog = """#----------------------------------%NODETYPEID%update_controller%NODETYPEID%-----------------------------------------------------------------------

#This script contains all the functionality for the specialized "Welcome" controller with only 1 button and no progress bar.  

#When executed, it will display the welcome controller.

#------------------------------------------------------------------------------------------------------------

#-------------Customizable values------------------------------------------

#1. Replace "Step title" with the text for the controller's title bar.  HTML tags are supported for formatting.
#%INPUT%
title = """+'"""Welcome to my tutorial"""\n'+"""#%INPUT%

#2. Replace "Step body text" with the text for the controller's body.  HTML tags are supported for formatting.
#%INPUT%
description = """+'"""Click <b>Start</b> to begin."""\n'+"""#%INPUT%

#4. Replace "Restart Step" with the text for left button.
#%INPUT%
button0 = "Restart Step"
#%INPUT%

#5. Replace "Next" with the text for right button.
#%INPUT%
button1 = "Start"
#%INPUT%

#6. Set this to 'True' to hide the 'Reset' button
#%INPUT%
disable_reset = True
#%INPUT%

#7. Set this to 'True' to lock the 'Next' button
#%INPUT%
disable_next = False
#%INPUT%

#8. Set this to 'True' to increment the step counter
#%INPUT%
increment_step = True
#%INPUT%

#9. Set the x offset (in % of window size)
#%INPUT%
x_offset = 80
#%INPUT%

#10. Set the y offset (in % of window size)
#%INPUT%
y_offset = 60
#%INPUT%

#-------------Advanced section---------------------------------------------

from functools import partial
from PySide2.QtCore import QPoint
import moverlay as mo

#-------------------------Helper functions---------------------

#push to the next stage (based on the "current_stage" attribute)
#Because this is run as a scriptJob, it needs to contain all its own dependencies (including duplicate procedures) 
def pressNext(dialog, index):
	import moverlay as mo
	mo.g_overlay_manager.controller.theDialog().deleteLater()
	cmds.scriptNode("controller", eb=True)
	def nextStage(dialog, index):
		current = cmds.getAttr('controller.current_stage')
		cmds.stage(current, edit=True, next=True)
		
	nextStage(dialog, index)

#destroy the dialog box when the X button is pushed
def pressClosed(dialog):
    cmds.scriptNode('closeController', eb=True)

#-------------------------Main script-------------------------------------
        
#kill any scriptJobs from previous tutorials
for i in mo.protected_listener_list:
	cmds.scriptJob(kill=i)
del mo.protected_listener_list[:]

#set up controller and assign it to a global variable
mo.g_overlay_manager
mo.g_overlay_manager = mo.maya.overlayManager()
mo.g_overlay_manager.controller = mo.progressDialog.ProgressDialog(mo.g_overlay_manager.getMainWindow())
dropShadow = mo.higDropShadow.HIGDropShadow(mo.g_overlay_manager.getMainWindow(), mo.g_overlay_manager.controller)


#load controller text
style = cmds.getAttr("controller.instruct_html_style")
if cmds.getAttr("controller.use_dictionary"):
		#load controller text
		cmds.setAttr('controller.text_query', 'dialogTitle', type="string")
		cmds.scriptNode('populateText', executeBefore=True)
		html_text = cmds.getAttr('controller.overlay_text')
		title = "<p style = "+style+" ><h3>"+html_text+"</h3></p>"

		#load button text
		cmds.setAttr('controller.text_query', 'hintText', type="string")
		cmds.scriptNode('populateText', executeBefore=True)
		button_text = cmds.getAttr('controller.overlay_text').split("//")
		cmds.setAttr('controller.button0', button_text[0], type="string")
		cmds.setAttr('controller.button1', button_text[1], type="string")
		button1 = cmds.getAttr('controller.button1')
		mo.g_overlay_manager.controller.button(1).setText(button1)

		cmds.setAttr('controller.text_query', 'dialogBody', type="string")
		cmds.scriptNode('populateText', executeBefore=True)
		html_text = cmds.getAttr('controller.overlay_text')
		description = "<p style = "+style+" >"+html_text+"</p>"
		html_text = title+"//"+description
		cmds.setAttr('controller.overlay_text', html_text, type="string")

else:
	title = "<p style = "+style+" ><h3>"+title+"</h3></p>"
	description = "<p style = "+style+" >"+description+"</p>"
mo.g_overlay_manager.controller.setTitle(title)
mo.g_overlay_manager.controller.setBodyText(description)

#hide the reset button
br=mo.g_overlay_manager.controller.button(0)
br.setVisible(False)

#set up button functionality
mo.g_overlay_manager.controller.setupButton(1, button1, pressNext)
mo.g_overlay_manager.controller.setCloseCallback(pressClosed)

#size and position controller
mo.g_overlay_manager.controller.theDialog().resize(mo.utils.DPIScale(180), mo.utils.DPIScale(250))
mo.g_overlay_manager.controller.theDialog().moveToScreenPos(mo.g_overlay_manager.getMainWindow().mapToGlobal(mo.coordinateFromPercentage(x_offset, y_offset)))

mo.g_overlay_manager.controller.showAndRaise()
    
    """
    
    cmds.scriptNode(name="_template_stage_setup", beforeScript = template_stage_setup, sourceType="python")
    cmds.scriptNode(name="_template_text_overlay", beforeScript = template_text_overlay, sourceType="python")
    cmds.scriptNode(name="_template_trigger", beforeScript = template_trigger, sourceType="python")
    cmds.scriptNode(name="_template_update_controller", beforeScript = template_update_controller, sourceType="python")
    cmds.scriptNode(name="clearDialogs", beforeScript = clear_dialogs, sourceType="python")
    cmds.scriptNode(name="clearListeners", beforeScript = clear_listeners, sourceType="python")
    cmds.scriptNode(name="clearOverlays", beforeScript = clear_overlays, sourceType="python")
    cmds.scriptNode(name="closeController", beforeScript = close_controller, sourceType="python")
    cmds.scriptNode(name="deactivateStage", beforeScript = deactivate_stage, sourceType="python")
    cmds.scriptNode(name="initialize", beforeScript = initialize, sourceType="python")
    cmds.scriptNode(name="loadTranscript", beforeScript = load_transcript, sourceType="python")
    cmds.scriptNode(name="overlayBubble", beforeScript = overlay_bubble, sourceType="python")
    cmds.scriptNode(name="overlayDialog", beforeScript = overlay_dialog, sourceType="python")
    cmds.scriptNode(name="populateText", beforeScript = populate_text, sourceType="python")
    cmds.scriptNode(name="refreshController", beforeScript = refresh_controller, sourceType="python")
    cmds.scriptNode(name="shutdownScript", afterScript = shutdown_script, sourceType="python", st=1)
    cmds.scriptNode(name="startScript", beforeScript = start_script, sourceType="python", st=1)
    cmds.scriptNode(name="updateMenuMode", beforeScript = update_menu_mode, sourceType="mel")
    cmds.scriptNode(name="welcomeDialog", beforeScript = welcome_dialog, sourceType="python")

    
    cmds.scriptNode(name="controller", beforeScript = tutorial_controller, sourceType="python")
    cmds.select("controller")
    cmds.addAttr( longName='current_stage', dataType="string")
    cmds.addAttr( longName='overlay_text', dataType="string")
    cmds.addAttr( longName='overlay_rel_to', dataType="string")
    cmds.addAttr( longName='overlay_offset_x', at='short', dv=0)
    cmds.addAttr( longName='overlay_offset_y', at='short', dv=150)
    cmds.addAttr( longName='speech_html_style', dataType="string")  
    cmds.addAttr( longName='instruct_html_style', dataType="string")    
    cmds.addAttr( longName='reference_html_style', dataType="string")    
    cmds.addAttr( longName='push_next', at='bool')    
    cmds.addAttr( longName='overlay_style', dataType="string")    
    cmds.addAttr( longName='disable_next', at='bool')    
    cmds.addAttr( longName='overlay_tail_direction', dataType="string")  
    cmds.addAttr( longName='overlay_tail_position', at='float', dv=0.5)
    cmds.addAttr( longName='hide_controller', at='bool')  
    cmds.addAttr( longName='reset_step', at='bool')  
    cmds.addAttr( longName='disable_reset', at='bool') 
    cmds.addAttr( longName='text_query', dataType="string")   
    cmds.addAttr( longName='overlay_width', at='short', dv=700)
    cmds.addAttr( longName='button1', dataType="string")    
    cmds.addAttr( longName='button0', dataType="string")  
    cmds.addAttr( longName='is_offset_absolute', at='bool')  
    cmds.addAttr( longName='use_dictionary', at='bool')  
    cmds.select(clear=True)
    
    cmds.setAttr( "controller.current_stage", "stage0", type="string") 
    cmds.setAttr( "controller.overlay_rel_to", "bottom", type="string") 
    cmds.setAttr( "controller.speech_html_style", '"color: #3C3C3C; font-size: 16pt; font-weight: normal; font-style: normal; font-family: Artifakt Element"', type="string") 
    cmds.setAttr( "controller.instruct_html_style", '"color: white; font-size: 13pt; font-weight: normal; font-style: normal; font-family: Artifakt Element"', type="string") 
    cmds.setAttr( "controller.reference_html_style", '"color: white; font-size: 13pt; font-weight: normal; font-style: normal; font-family: Artifakt Element"', type="string") 
    cmds.setAttr( "controller.overlay_style", "speech", type="string") 
    cmds.setAttr( "controller.overlay_tail_direction", "top", type="string") 
    cmds.setAttr( "controller.text_query", "dialogBody", type="string") 
    cmds.setAttr( "controller.button1", "Next", type="string") 
    cmds.setAttr( "controller.button0", "Restart Step", type="string") 


    
    cmds.stage("stage0")
    cmds.stage("final_stage")
    cmds.connectAttr("initialize.before", "stage0.onActivateScript")
    cmds.connectAttr("welcomeDialog.before", "initialize.after")
    cmds.connectAttr("deactivateStage.before", "stage0.onDeactivateScript")
    cmds.connectAttr("stage0.nextState", "final_stage.previousState")
    cmds.connectAttr("closeController.before", "final_stage.onActivateScript")
    
    set_list = ["stage0", "_template_stage_setup", "_template_text_overlay", "_template_trigger", "_template_update_controller", "initialize", "deactivateStage", "welcomeDialog"]
    
    cmds.sets(set_list, name="GRAPH_MY_CHILDREN")
    
    set_list = ["clearDialogs", "clearListeners", "clearOverlays", "closeController", "controller", "deactivateStage", "loadTranscript", "overlayBubble", "overlayDialog", "populateText", "refreshController", "updateMenuMode", "shutdownScript", "updateMenuMode"]
    
    cmds.sets(set_list, name="tutorial_support_nodes")
    
    if not cmds.ls("shot1_cam"):
        camera_name = cmds.camera()[0]
        cmds.rename(camera_name, "shot1_cam")
        cmds.xform("shot1_cam", t=(0, 31.5, 35), ro=(-42, 0, 0), absolute=True)
        cmds.setAttr("shot1_cam.centerOfInterest", 47.385)
    
    cmds.menuItem("use_dictionary", e=True, enable=True, checkBox=cmds.getAttr("controller.use_dictionary"))
    
    cmds.evalDeferred('drawEditUI("tc_window")')

def openToolbox(*args):
    
    def listItems(list, num_per_row):
        count = 0
        items = ""
        for x in list:
            if count%num_per_row == 0 and count != 0:
                items = items+"\n"
            items = items+"["+str(count)+"] - "+x
            count = count+1        
        return items
    
    def getSelection(*args):
        selection = cmds.ls(sl=True)
        
        cmds.text("result_field", e=True, label = "The current selection is: \n"+listItems(selection, 1))

    def getContext(*args):
        cmds.text("result_field", e=True, label = "The current context is: \n"+cmds.currentCtx())

    def getAllContexts(*args):
        contexts = cmds.lsUI(contexts=True)
        
        cmds.text("result_field", e=True, label = "All possible contexts: \n"+listItems(contexts, 1))
    
    def getVisWSControls(*args):
        controls = cmds.lsUI(type="workspaceControl")
        
        vis_controls = []
        for x in controls:
            if cmds.workspaceControl(x, q=True, visible=True):
                vis_controls.append(x)
        
        cmds.text("result_field", e=True, label = "All workspace controls: \n"+listItems(vis_controls, 1))
    
    def getAllWSControls(*args):
        controls = cmds.lsUI(type="workspaceControl")
        
        cmds.text("result_field", e=True, label = "All workspace controls: \n"+listItems(controls, 1))
        
    #Convert all text defined by the app into a single dictionary entry.  Primarily used when a tutorial needs to be localized (the primary use-case for "Use Dictionary" mode).
    def convertToDictionary(*args):
        stage_list = ["stage0"]
        curr_stage = cmds.listConnections("stage0.nextState")
        
        try:
            while curr_stage:
                stage_list.append(curr_stage[0])
                curr_stage = cmds.listConnections(curr_stage[0]+".nextState")
            
            stage_list.remove("final_stage")
            
            transcript_EN = {
                'stage0': {
                'dialogTitle': "",
                'dialogBody': "",
                'bubbleText': "",
            	'hintText':"",
                }
            }
            
            for curr_stage in stage_list:
                selected_node = cmds.listConnections(curr_stage+".onActivateScript")
                transcript_EN.update({curr_stage:{
                'dialogTitle': [],
                'dialogBody': [],
                'bubbleText': [],
            	'hintText':[],}})
                while selected_node:
            
                    selected_type = cmds.getAttr(selected_node[0]+".before").split("%NODETYPEID%")[1]
                    parsed_input_list = cmds.getAttr(selected_node[0]+".before").split('#%INPUT%')
                    
                    if selected_type == "text_overlay":
                        step_text = parsed_input_list[1].split('\nhtml_text = """')[1][:-4]
                        transcript_EN[curr_stage]['bubbleText'].append(step_text)
            
                    elif selected_type == "update_controller":
                        instruct_title = parsed_input_list[1].split('\ntitle = """')[1][:-4]
                        transcript_EN[curr_stage]['dialogTitle'].append(instruct_title)
                        instruct_description = parsed_input_list[3].split('\ndescription = """')[1][:-4]
                        transcript_EN[curr_stage]['dialogBody'].append(instruct_description)
                        left_button_text = parsed_input_list[5].split('\nbutton0 = "')[1][:-2]
                        right_button_text = parsed_input_list[7].split('\nbutton1 = "')[1][:-2]
                        transcript_EN[curr_stage]['hintText'].append([left_button_text, right_button_text])
                        
                    
                    selected_node = cmds.listConnections(selected_node[0]+".after")
                          
            pop_string = cmds.getAttr("loadTranscript.before").split("#%EN")
            pop_string2 = pop_string[0]+"#%EN\ntranscript_EN = "+str(transcript_EN)+"\n#%EN"+pop_string[2]
            cmds.setAttr("loadTranscript.before", pop_string2, type="string")     
            cmds.scriptNode("loadTranscript", eb=True)
            cmds.text("result_field", e=True, label = '"loadTranscript" node was successfully updated!')
        except:
            cmds.text("result_field", e=True, label = 'There was an error.  "loadTranscript" node has not been updated!')
    
    #Export the contents of the english transcript in "loadTranscript" to a json file 
    def exportDictionary(*args):
        import json
        
        def dumpJSON():
            filename = cmds.fileDialog2(fm=0, ds=2, ff=".json")
            try:
                with open(filename[0], 'w', encoding='utf-8') as f:
                    json.dump(mo.transcript, f, indent=4)
            except:
                pass
                
        def mergeChanges(*args):
            closeEXWarning()
            convertToDictionary()
            dumpJSON()
        
        def closeEXWarning(*args):
            if cmds.window("ex_window", exists=True):
                cmds.deleteUI("ex_window")  
                
            dumpJSON()
        
        if cmds.window("ex_window", exists=True):
            cmds.deleteUI("ex_window")    

        ex_window = cmds.window ("ex_window", title="Warning", sizeable=True, widthHeight=(100, 100))
        cmds.columnLayout("ex_main", columnAlign = "left", rs=5, parent=ex_window)
        cmds.text("override_lang_text", label = "\nWould you like to merge your current text changes to the dictionary before exporting?\n", parent="ex_main")
        cmds.rowLayout("ex_buttons", parent="ex_main", numberOfColumns=2)
        cmds.button ("ex_yes", label = "Yes", parent="ex_buttons", width=50, command=mergeChanges)
        cmds.button ("ex_no", label = "No", parent="ex_buttons", width=50, command=closeEXWarning)
        cmds.text("ex_spacer", label="", parent="ex_main")
        cmds.showWindow( ex_window )
               
        
    #Import a specific language transcript to the loadTranscript dictionary
    def importDictionary(*args):
        import json
        import base64
        
        def chooseLangWindow():
            if cmds.window("lang_window", exists=True):
                cmds.deleteUI("lang_window")    
                
            lw_window = cmds.window ("lang_window", title="Choose a language", sizeable=True, widthHeight=(300, 200))
            cmds.columnLayout("lw_main", columnAlign = "center", rs=1, parent=lw_window)
            cmds.text (align="center", parent = "lw_main", label="\nWhat language are you importing?")
            cmds.text ("lw_spacer", label="", parent="lw_main")
            
            button_width = 225
            
            cmds.optionMenu("lw_lang", parent = "lw_main")  
            cmds.menuItem("Chinese (CN)")
            cmds.menuItem("Japanese (JP)")
            
            cmds.text("lw_button_spacer", label = "", parent="lw_main")
            cmds.button ("lw_open_file", label = "Import", parent="lw_main", command=openLanguageFile, width = button_width, height=35)
            
            cmds.showWindow( lw_window )
            
        def openLanguageFile(*args):
            lang = cmds.optionMenu("lw_lang", q=True, v=True)
            lang_short = lang.split("(")[1][:-1]
            
            try:
                filename = cmds.fileDialog2(fm=1, ds=2)
        
                with open(filename[0], 'r', encoding='utf-8') as f:
                  data = json.load(f)
                #transcript = stringToDictionary(data)
                
                createDictionary(data, lang_short)
                cmds.text("result_field", e=True, label = lang+" was successfully updated!")
            
            except:
                cmds.text("result_field", e=True, label = "There was an error.  "+lang+" was not updated!")
                
            if cmds.window("lang_window", exists=True):
                cmds.deleteUI("lang_window")  
        
        #Convert a string representation of the transcript dictionary to an actual dictionary construct
        def stringToDictionary(transcript):
            import ast
            import re
            
            transcript_partition = re.split('(stage\d+)', transcript)
            main_dict ={}
            
            count = 1
            while count < len(transcript_partition):
                print(count)
                temp_string = transcript_partition[count+1][3:].split("}")
                temp_dict = ast.literal_eval(temp_string[0]+"}")
                temp_index = transcript_partition[count]
                main_dict[temp_index] = temp_dict
                count = count+2
            return (main_dict)
               
        
        def createDictionary(transcript, lang):
            import base64
        
            key = ""
            encoded_dict = {}
            for x, y in transcript.items():
                key = x
                
                temp_dict = {}
                for a, b in y.items():
                    hint_list = []
                    if (isinstance(b, list)):
                        hint_list.clear()   
                        for i in b:
                            if isinstance(i, list):
                                temp_list = []
                                for j in i:
                                    try:
                                        temp_list.append(base64.b64encode(j.encode()))
                                    except:
                                        pass
                                hint_list.append(temp_list)
                            else:
                                try:
                                    hint_list.append(base64.b64encode(i.encode()))
                                except:
                                    pass
                        
                        temp_dict[a] = []
                        temp_dict[a] = hint_list
                        
                    else:
                        temp_dict[a] = base64.b64encode(b.encode())
                        
                encoded_dict[x]=temp_dict
            
            output_text = ""
        
            for x, y in encoded_dict.items():
                output_text = output_text+('"')+str(x)+('":\n')+str(y)+"\n,\n"
        
            
            transcript_node_partition = cmds.getAttr("loadTranscript.before").split("#%"+lang)
            transcript_node_partition[1] = "#%"+lang+"\ntranscript_"+lang+" = {"+output_text.replace("\n", "")+"}\n#%"+lang
            cmds.setAttr("loadTranscript.before", transcript_node_partition[0]+transcript_node_partition[1]+transcript_node_partition[2], type="string")
        
        chooseLangWindow()        

    
    def overrideLanguageWindow(*args):
        def overrideLanguage(*args):
            override_value = cmds.optionMenu("override_lang", q=True, sl=True)
            try:
                if override_value == 1:
                    #grab the current product language
                    mo.sys_lang = cmds.about(uil=True)
                elif override_value == 2:
                    mo.sys_lang = "en_US"
                elif override_value == 3:
                    mo.sys_lang = "zh_CN"
                elif override_value == 4:
                    mo.sys_lang = "ja_JP"   
                    
                if cmds.window("override_lang_window", exists=True):
                    cmds.deleteUI("override_lang_window")
                    
                cmds.scriptNode("loadTranscript", eb=True)  
                cmds.text("result_field", e=True, label = "Tutorial display language successfully changed to "+mo.sys_lang+"!")

            except:
                cmds.text("result_field", e=True, label = "There was an error.  Tutorial display language has defaulted to "+mo.sys_lang)

            
        if cmds.window("override_lang_window", exists=True):
            cmds.deleteUI("override_lang_window")    
    
        ol_window = cmds.window ("override_lang_window", title="Language override settings", sizeable=True, widthHeight=(200, 100))
        cmds.columnLayout("ol_main", columnAlign = "center", rs=5, parent=ol_window)
        cmds.text("override_lang_text", label = "Force tutorial language:", parent="ol_main")
        cmds.optionMenu("override_lang", parent = "ol_main")  
        cmds.menuItem("None")
        cmds.menuItem("English (EN)")
        cmds.menuItem("Chinese (CN)")
        cmds.menuItem("Japanese (JP)")  
        
        if (mo.sys_lang == "en_US"):
            cmds.optionMenu("override_lang", e=True, sl=2)
        elif (mo.sys_lang == "zh_CN"):
            cmds.optionMenu("override_lang", e=True, sl=3)
        elif (mo.sys_lang == "ja_JP"):
            cmds.optionMenu("override_lang", e=True, sl=4)
        
        cmds.button("override_button", label="Override", parent="ol_main", command = overrideLanguage)
        
        cmds.showWindow( ol_window )    
        
    if cmds.window("toolbox_window", exists=True):
        cmds.deleteUI("toolbox_window")    
    
    tb_window = cmds.window ("toolbox_window", title="Utilities", sizeable=True, widthHeight=(600, 300))
    cmds.columnLayout("tb_main", columnAlign = "center", rs=2, parent=tb_window)
    cmds.text (align="center", parent = "tb_main", label="\nHere is a collection of useful utilities to use when building tutorials.")
    cmds.text ("tb_spacer", label="", parent="tb_main")
    
    button_width = 225
    
    cmds.rowColumnLayout("tb_button_layout", parent="tb_main", numberOfColumns=2, rs=(1,3), cs=(2,3))
    cmds.button ("select_check", label = "What's my current selection?", parent="tb_button_layout", command=getSelection, width = button_width, height=35)
    cmds.text("tb_button_spacer1", label = "", parent="tb_button_layout")
    cmds.button ("context_check", label = "What's my current context?", parent="tb_button_layout", command=getContext, width = button_width, height=35)
    cmds.button ("context_all", label = "List of all possible contexts", parent="tb_button_layout", command=getAllContexts, width = button_width, height=35)
    cmds.button ("merge_to_dict", label = "Merge text to dictionary", parent="tb_button_layout", command=convertToDictionary, width = button_width, height=35, statusBarMessage="Injects all text from text_overlay and update_controller nodes into the loadTranscript dictionary.")    
    cmds.text ("tb_spacer2", label="", parent="tb_button_layout")
    cmds.button ("export_dict", label = "Export dictionary to json", parent="tb_button_layout", command=exportDictionary, width = button_width, height=35, statusBarMessage="Export the current loadTranscript english dictionary to a JSON file.")    
    cmds.button ("import_dict", label = "Import dictionary from json", parent="tb_button_layout", command=importDictionary, width = button_width, height=35, statusBarMessage="Import a JSON dictionary to the loadTranscript node.")  
    cmds.button ("override_lang_button", label = "Override tutorial language", parent="tb_button_layout", command=overrideLanguageWindow, width = button_width, height=35, statusBarMessage="Override the OS language to display the tutorial in a different language.")

    #cmds.button ("ws_control_vis", label = "What workspace controls are visible?", parent="tb_button_layout", command=getVisWSControls, width = button_width, height=35)    
    #cmds.button ("ws_control_all", label = "List of all workspace controls", parent="tb_button_layout", command=getAllWSControls, width = button_width, height=35)


    cmds.text ("tb_spacer3", label="", parent="tb_main")
    cmds.scrollLayout("tb_result_layout", parent="tb_main", height=400, width=600)
    cmds.text("result_field", align = "left", label = "Click a button and the result will appear here", parent="tb_result_layout")

    cmds.showWindow( tb_window )

def toggleDictionary(*args):
    if cmds.getAttr("controller.use_dictionary"):
        cmds.setAttr("controller.use_dictionary", False)
    else:
        cmds.setAttr("controller.use_dictionary", True)

#-------------------------Helper functions-------------------------------------

#adapts a point to the current DPI of the OS
def getCoordinate(x_percentage, y_percentage):
	import moverlay as mo
	from PySide2.QtCore import QPoint
	mainWindow = mo.maya.getMainMayaWindow()
	width = mainWindow.frameGeometry().width()
	height = mainWindow.frameGeometry().height()
	x_pos = (width/100) *x_percentage
	y_pos = (height/100) *y_percentage
	return QPoint(x_pos, y_pos)

#find the exact position of a UI element
def getUIPosition(uiName):
	import moverlay as mo
	from PySide2 import QtWidgets, QtCore
	import maya.OpenMayaUI as omui
	import shiboken2

	def getMainMayaWindow():		
		""" returns the main maya window """
		ptr = omui.MQtUtil.mainWindow()
		return shiboken2.wrapInstance(int(ptr), QtWidgets.QMainWindow)

	mainWindow = getMainMayaWindow()
	parentTopLeft = mainWindow.frameGeometry().topLeft()
	widgetptr = omui.MQtUtil.findControl(uiName)
	widget = shiboken2.wrapInstance(int(widgetptr), QtWidgets.QWidget)
	rect = widget.rect()
	screenRect = QtCore.QRect()
	screenRect.setTopLeft(widget.mapToGlobal(rect.topLeft()))
	screenRect.setSize(rect.size())
	screenRect.translate(-parentTopLeft.x(), -parentTopLeft.y())
	return QtCore.QPoint(screenRect.x()/mo.utils.DPIScale(1), screenRect.y()/mo.utils.DPIScale(1))

#assign these helper functions to moverlay so we can access them in other scriptNodes
mo.coordinateFromPercentage = getCoordinate
mo.getUIPosition = getUIPosition
#---------------------------------------------------------------------------------------------------------------------

def closeTCWindow(*args):
    
    clearAllPreviews()

    try:
        cmds.evalDeferred('cmds.scriptNode("shutdownScript", ea=True)')
    except:
        pass

def clearTCWindow():
    current_window_contents = cmds.columnLayout("main", q=True, ca=True)
    
    if current_window_contents:
        for x in current_window_contents:
            cmds.deleteUI(x)

#UI to draw if existing state machine ("stage0") is detected
def drawEditUI(tc_window):
    clearTCWindow()
    
    cmds.text (align= "center", parent = "main", label="  \nAdd or insert a new step\n")
    cmds.rowColumnLayout("section_create", numberOfColumns=2, cs = (1, 5), rs = (1, 5), cal = (1, "left"), parent="main")
    cmds.button( label='+New Step', parent="section_create", height = 50, width = 100, command = partial(addStepNodesWindow, True) )
    cmds.rowColumnLayout("section_play", parent = "section_create", numberOfColumns=4, cs = (1, 15), rs = (1, 5), cal = (1, "left"))
    cmds.text( "play_spacer", label="\t\t\t", parent = "section_play")
    cmds.button( "play_beginning", label='Play from \nbeginning', height = 50, width = 100, command = playFromStart)
    cmds.text( "play_spacer2", label=" ", parent = "section_play")
    cmds.button( "play_current", label='Play from \nselected', height=50, width = 100, command = playFromCurrent)
    cmds.separator(horizontal=True, style="out", visible=True, height=20, parent="main")
    
    cmds.text (align= "center", parent="tc_window|main", label="  \nEdit an existing step\n")
    cmds.separator(horizontal=True, parent="tc_window|main")
    cmds.rowColumnLayout("section_edit", numberOfColumns=2, cs=(2,5), rs = (2, 5), parent="tc_window|main", columnWidth=(1, 200))
    cmds.textScrollList( "node_list", parent="section_edit", sc=buildEditPane )
    
    cmds.scrollLayout("UI_edit_pane_main", parent="section_edit", height=600, width=800)
    cmds.rowColumnLayout("UI_edit_pane", numberOfColumns=2, cs = (2, 5), rs = (2, 5), rat = (2, "both", 2), parent="UI_edit_pane_main", cal = (1, "right"), width=650)
    cmds.text ("UI_edit_pane_empty_txt", parent="UI_edit_pane", label="\n\n\n\n\n\n\n\n\n\n\n <-- Select a node to edit it.")
    
    cmds.rowColumnLayout("mod_node_list_layout", parent="section_edit", cs = (2, 5), rs = (2, 5), numberOfColumns=2)
    cmds.button("rename_node_button", label="Rename", parent="mod_node_list_layout", enable = False, command=renameWindow)
    cmds.button("delete_node_button", label="Delete", enable = False, parent="mod_node_list_layout", command=deleteNode)    
    
    populateNodeList()
    
    cmds.setParent( '..' )
    cmds.showWindow( tc_window )
    
    
    
#UI to draw if no state machine ("stage0") is detected
def drawStartUI(tc_window):
    clearTCWindow()
    cmds.gridLayout("new_tutorial_layout", parent = "main", numberOfRowsColumns=(3, 3), pos=("new_tutorial_button", 5), cw=233, ch = 206, width = 700, height=640)
    cmds.text("new_tutorial_spacer1", label="", parent="new_tutorial_layout")
    cmds.text("new_tutorial_spacer2", label="", parent="new_tutorial_layout")
    cmds.text("new_tutorial_spacer3", label="", parent="new_tutorial_layout")
    cmds.text("new_tutorial_spacer4", label="", parent="new_tutorial_layout")
    cmds.button( "new_tutorial_button", label='Create new tutorial', parent = "new_tutorial_layout", height=20, width = 150, command = createBaseTutorial)
    cmds.setParent( '..' )
    cmds.showWindow( tc_window )

#run the tutorial creator app
def runTutorialCreator():

    #grab the current product language
    mo.sys_lang = cmds.about(uil=True)
    
    if not cmds.pluginInfo('stage.py', q=True, loaded=True):
        cmds.loadPlugin('stage.py')
    
    if not cmds.pluginInfo('timeSliderBookmark.mll', q=True, loaded=True):    
        cmds.loadPlugin('timeSliderBookmark.mll')
   
    if cmds.window("tc_window", exists=True):
        cmds.deleteUI("tc_window")
    
    #Main tutorial window creation
    tc_window = cmds.window ("tc_window", title="Tutorial Creator", widthHeight=(800, 800), menuBar=True, closeCommand=closeTCWindow)
    cmds.menu(label="File")
    cmds.menuItem(label="New Tutorial", command=createNewTutorial)
    cmds.menu(label="Options")
    cmds.menuItem("jump_to_stage", label="Jump to selected stage time", checkBox=True)
    cmds.menuItem("jump_to_camera", label="Jump to selected stage camera", checkBox=True)
    cmds.menuItem("use_dictionary", label="Source text from dictionary", checkBox=False, enable=True, command=toggleDictionary)
    cmds.menuItem("show_node_network", label="Show in Node Editor", command=openNodeNetwork)
    cmds.menuItem("show_expression_editor", label="Show in Expression Editor", command=openInExpressionEditor)
    cmds.menuItem("open_utilities", label="Utilities", command=openToolbox)
    cmds.columnLayout("main", parent=tc_window)
    
    stage0_exist = cmds.ls("stage0")
    stage_list = cmds.ls(type="stage")
    
    if stage0_exist:
        drawEditUI(tc_window)
    elif stage_list:
        clearTCWindow()
        cmds.text (align= "center", parent="main", label="  \nSorry, but this tutorial is not compatible with the Tutorial Creator App\n")
        cmds.setParent( '..' )
        cmds.showWindow( tc_window )
    else:
        cmds.menuItem("use_dictionary", e=True, enable=False)
        drawStartUI(tc_window)
    
    #setup global event listener lists for later use
    mo.g_overlay_manager=""
    mo.listener_list=[]
    mo.protected_listener_list=[]
    mo.dialog_list=[]
