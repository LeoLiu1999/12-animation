import mdl
from display import *
from matrix import *
from draw import *
    
"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):
    vary_found = False
    frames_found = False
    basename_found = False
    frames = 1
    for command in commands:
        op = command['op']
        args = command['args']
        if op == "vary":
            vary_found = True
        if op == "basename":
            if basename_found:
                raise Exception("Multiple basename found!")
            else:
                basename = args[0]
                basename_found = True
            
        if op == "frames":
            if frames_found:
                raise Exception("Multiple frames found!")
            elif args[0] < 1:
                raise Exception("Negative/zero frames count!")
            else:
                frames = args[0]
                frames_found = True
    if vary_found and not frames_found:
        raise Exception("vary used without specifying frames!")
    if frames_found and not basename_found:
        basename = "image"
        raise UserWarning("No basename found, output named image")
    return [basename, frames]

"""======== second_pass( commands ) ==========
x
  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    knobs = [{} for i in range(int(num_frames))]
    for command in commands:
        if command['op'] == 'vary':
            args = command['args']
            knob_name = command['knob']

            if not knob_name in knobs[0]: #init knob values if needed
                for frame in knobs:
                    print frame
                    frame[knob_name] = 0

            val = args[2]
            d = (args[3] - args[2]) / (args[1] - args[0])
            print d
            for frame in range( int(args[0]),  int(args[1]) + 1):
                knobs[frame][knob_name] = val
                val += d
    print "printing knobs"
    print knobs
    return knobs
                
def run(filename):
    """
    This function runs an mdl script
    """
    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [0,
              255,
              255]]
    areflect = [0.1,
                0.1,
                0.1]
    dreflect = [0.5,
                0.5,
                0.5]
    sreflect = [0.5,
                0.5,
                0.5]

    color = [0, 0, 0]
    consts = ''
    coords = []
    coords1 = []

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    (basename, frames) = first_pass(commands)
    frames = int(frames)
    
    if frames > 1:
        knobs = second_pass(commands, frames)

    frame = 0
    while frame < frames:
        print frame
        
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 20
        
        for command in commands:
            print command
            c = command['op']
            args = command['args']

            
            for knob in knobs[frame]:
                print "symbols: " + str(symbols)
                symbols[knob][1] = knobs[frame][knob]

            if args != None and "knob" in command and command["knob"] != None and c in ["move", "scale", "rotate"]:
                knob = command["knob"]
                for i in range(len(args)):
                    if not isinstance(args[i], basestring):
                        args[i] = args[i] * symbols[knob][1]
            
            if c == 'box':
                if isinstance(args[0], str):
                    consts = args[0]
                    args = args[1:]
                if isinstance(args[-1], str):
                    coords = args[-1]
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
                tmp = []
            elif c == 'line':
                if isinstance(args[0], str):
                    consts = args[0]
                    args = args[1:]
                if isinstance(args[3], str):
                    coords = args[3]
                    args = args[:3] + args[4:]
                if isinstance(args[-1], str):
                    coords1 = args[-1]
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        if frames > 1:
            save_extension(screen, ("./anim/" + basename + ("%03d" % int(frame)) + ".png"))

        #reset and update
        tmp = new_matrix()
        ident( tmp )
        
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 20
        
        print frame
        frame += 1


    if frames > 1:
        make_animation(basename)
