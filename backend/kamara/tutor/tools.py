


# mapping to function declaration

WHITEBOARD_TOOL_MAP = {
    "async_draw": draw_on_board,
    "clear_whiteboard": clear_board,
    "write_board": write_on_board,
    "delete_item" : delete_item
}



tools = {"function_declarations" : [
        # Tool 1: The Drawing Tool
        {
            "name": "async_draw",
            "description": draw_tool_desc ,
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "shape_id" : {"type" : "STRING"},
                    "shape": {"type": "STRING"},
                    "x": {"type": "INTEGER"},
                    "y": {"type": "INTEGER"},
                    "width" : {"type" : "INTEGER"},
                    "height" : {"type" : "INTEGER"}
                    },
                    "required": ["shape_id","shape", "x", "y"]
                    },
             
            "behavior": "NON_BLOCKING"
        },


        # Tool 2: The Clear Tool 

        {
            "name": "clear_whiteboard",
            "description": clear_tool_desc,
            "parameters": {
                "type": "OBJECT",
                "properties": {}, # No arguments needed for clearing
            },
            "behavior": "NON_BLOCKING"
        },


        # Tool 3: The write tool

        {
            "name" : "write_board",
            "description" : write_tool_desc,
            "parameters" : {
                "type" : "OBJECT",
                "properties" : {
                    "text_id" : {"type" : "STRING"},
                    "text" : {"type" : "STRING"},
                    "x" : {"type" : "INTEGER"},
                    "y" : {"type" : "INTEGER"},
                    "text_size" : {"type" : "INTEGER"}
                }, 
                "required" : ["text_id","text","x","y","text_size"]
            },
            
            "behavior" : "NON_BLOCKING"
        },

        # tool 4: the delete tool

        {
            "name" : "delete_item",
            "description" : delete_tool_desc,
            "parameters" : {
                "type" : "OBJECT",
                "properties" : {
                    "item_id" : {"type" : "STRING" }
                },
                "required" : ["item_id"]
            },
            "behavior" : "NON_BLOCKING"
        },

        # tool 5: the move item on screen tool
        {
            "name" : "move_item",
            "description" : move_item_desc,
            "parameters" : {
                "type" : "OBJECT",
                "properties" : {
                    "item_id" : {"type" : "STRING"},
                    "x" : {"type" : "INTEGER"},
                    "y" : {"type" : "INTEGER"}
                },
                "required" : ["item_id","x","y"]
            }
        },

        # adjust item,shape or text size,

        {
            "name" : "adjust_item_size",
            "description" : adjust_item_size_desc,
            "parameters" : {
                "type" : "OBJECT",
                "properties" : {
                    "item_id" : {"type" : "STRING"},
                    "width" : {"type" : "INTEGER"},
                    "height" : {"type" : "INTEGER"}
                },
                "required" : ["item_id", "width", "height"]
            }
        }




    ]
}


# tools handler
async def tools_handler(client_id,session, tool_call):

    # 1. This list holds ALL your results for this turn
    all_responses = []

    # 2. Loop through every action requested (Parallel Processing)
    result = "tool not found"
    for fc in tool_call.function_calls:
        #print(f"AI requested tool: {fc.name} with args: {fc.args}")

        # 3. Look up the actual function in your map
        func = WHITEBOARD_TOOL_MAP.get(fc.name)

        
        if fc.name == "async_draw":
            # Unpack Gemini's args and run your Python code
            result = await draw_on_board(client_id,**fc.args)
        
        elif fc.name == "write_board":
            result = await write_on_board(client_id,**fc.args)
            
        elif fc.name == "clear_whiteboard":
            result = await clear_board(client_id)
        elif fc.name == "delete_item":
            result = await delete_item(client_id,**fc.args)
        elif fc.name == "move_item":
            result = await move_item_on_screen(client_id,**fc.args)
        elif fc.name == "adjust_item_size":
            result = await adjust_item_size(client_id,**fc.args)
        
        # 3. Add this specific 'Receipt' to our batch list
        all_responses.append({
            "name": fc.name,
            "id": fc.id,           # Critical: Match the ID Gemini gave us
            "response": {"result" : result}    # The data from our Python function
        })

    # 4. SEND EVERYTHING BACK AT ONCE
    # This is the 'Batched' approach that Gemini prefers
    await session.send_tool_response(function_responses=all_responses)
    #await session.send_tool_response(  function_responses=all_responses)
