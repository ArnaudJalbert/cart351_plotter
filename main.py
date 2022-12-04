import cairo
import sqlite3
import requests
import time
from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces

IMAGE_WIDTH = 1086
IMAGE_HEIGHT = 876

DATA = [[0,0],[327, 0],[543, 405],[IMAGE_WIDTH, IMAGE_HEIGHT],[1,2]]

GET_URL = "http://localhost:3000/get_undrawn_entry.php"

def fetch_elements_in_db():

    response = requests.get(url = GET_URL, params = dict(get_undrawn_entry="get_undrawn_entry"))
    
    return response.text.strip()

def stringify_list(list_string):
    string_list = ""
    for entry in list_string:
        string_list = string_list + "[" + str(entry[0]) + "," + str(entry[1]) + "]"
        if entry != list_string[-1]:
            string_list = string_list + ","

    return string_list

def listify_string(string_list):
    sub_list = string_list.split('|')

    for i in range(len(sub_list)):
        sub_list[i] = sub_list[i].split(';')
        for el in sub_list[i]:
            el = int(el)

    return sub_list

def create_svg_file(point_array):
    # creating a SVG surface
    # here geek is file name & 700, 700 is dimension
    with cairo.SVGSurface("map.svg", IMAGE_WIDTH, IMAGE_HEIGHT) as surface:

        # creating a cairo context object
        context = cairo.Context(surface)

        # setting scale of the context
        context.scale(IMAGE_WIDTH, IMAGE_HEIGHT)

        context.new_path()

        context.set_line_width(0.001)

        for i in range(len(point_array)):

            context.move_to(int(point_array[i][0])/IMAGE_WIDTH, int(point_array[i][1])/IMAGE_HEIGHT)

            if(i+1<len(point_array)):
                context.line_to(int(point_array[i+1][0])/IMAGE_WIDTH, int(point_array[i+1][1])/IMAGE_HEIGHT)

        # setting color of the context
        context.set_source_rgba(0,0,0)

        # stroke out the color and width property
        context.stroke()
        
        context.close_path()

def create_gcode_file(path):
    # Instantiate a compiler, specifying the interface type and the speed at which the tool should move. pass_depth controls
    # how far down the tool moves after every pass. Set it to 0 if your machine does not support Z axis movement.
    gcode_compiler = Compiler(interfaces.Gcode, movement_speed=1000, cutting_speed=300, pass_depth=5)

    curves = parse_file(path) # Parse an svg file into geometric curves

    gcode_compiler.append_curves(curves) 
    gcode_compiler.compile_to_file("map.gcode", passes=2)

def plot_map_data(path):
    pass

if __name__ == "__main__":

    while True:
        
        response = fetch_elements_in_db()

        if response == 'empty':
            time.sleep(5)
            print("No Request!")
            continue
        
        map_data = listify_string(response)

        print(map_data)

        create_svg_file(map_data)

        create_gcode_file('map.svg')

        plot_map_data(path)

        time.sleep(5)
