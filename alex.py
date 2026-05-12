from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import sys

# -------------------- Data & Settings --------------------
table_positions = [0.35, 0.75, 1.15]  # Three tables
tables = []
students = []
queue = []
counter_occupied = False
game_active = True
walk_anim = 0.0 

entry_door_angle = 0.0
exit_door_angle = 0.0

start_time = 0
spawning_allowed = True

HUMAN_HEIGHT = 0.6
HEAD_SIZE = 0.045
STUDENT_SPEED = 0.007       
EAT_TIME_DURATION = 300  
WAIT_TO_EAT_DURATION = 180 
SERVICE_TIME_DURATION = 120
CLEANING_DELAY = 120        
HITBOX_SENSITIVITY = 0.02  

CLOTH_COLORS = [(0.0, 0.8, 0.0), (0.9, 0.1, 0.1), (1.0, 0.9, 0.0), (0.0, 0.9, 0.9), (0.8, 0.0, 0.8), (1.0, 0.5, 0.0)]

# Ticket system
TICKET_BOOTH_X = -1.05
TICKET_CHECK_DURATION = 30
ticket_officer = {'x': TICKET_BOOTH_X, 'y': -0.2, 'shirt_color': (0.2, 0.4, 0.8), 'pant_color': (0.1, 0.1, 0.3), 'hair_color': (0.1, 0.1, 0.1), 'is_walking': False}

def reset_simulation():
    global students, queue, counter_occupied, tables, game_active, start_time, spawning_allowed
    game_active = True
    counter_occupied = False
    queue = []
    tables = [{'x': tx, 'status': 'clean', 'clean_timer': 0} for tx in table_positions]
    students = []
    for i in range(4):
        spawn_student(i)
    if len(students) > 0:
        students[0]['hair_color'] = (1.0, 0.8, 0.2)
    start_time = glutGet(GLUT_ELAPSED_TIME)
    spawning_allowed = True

def spawn_student(i):
    h_colors = [(0.1, 0.1, 0.1), (0.3, 0.2, 0.1)]
    students.append({
        'id': i, 'x': -1.6 - (i * 0.4), 'y': -0.2,
        'shirt_color': random.choice(CLOTH_COLORS),
        'pant_color': (0.1, 0.1, 0.2),
        'hair_color': random.choice(h_colors),
        'has_food': False, 'state': 'going_to_ticket',
        'table_idx': -1, 
        'eat_timer': 0, 'wait_timer': 0, 'service_timer': 0,
        'is_walking': False,
        'ticket_timer': 0
    })

waiter_pos = -0.15
waiter = {'x': waiter_pos, 'y': -0.2, 'shirt_color': (0.9, 0.9, 0.9), 'pant_color': (0.1, 0.1, 0.1), 'hair_color': (0.2, 0.1, 0.0), 'is_walking': False}

RETURN_CONTAINER_X = 1.32
EXIT_DOOR_X = 1.52
DINING_HALL_RIGHT = 1.62

# -------------------- Drawing Helpers -----------------
def rectangle(x1, y1, x2, y2, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(x1, y1); glVertex2f(x2, y1)
    glVertex2f(x2, y2); glVertex2f(x1, y2)
    glEnd()

def circle(cx, cy, radius, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_POLYGON)
    for i in range(20):
        angle = 2*math.pi*i/20
        glVertex2f(cx + radius*math.cos(angle), cy + radius*math.sin(angle))
    glEnd()

def draw_animated_door(x, y, angle, r, g, b):
    rectangle(x - 0.01, y, x + 0.09, y + 0.35, 0.2, 0.1, 0.0) 
    swing_width = 0.08 * math.cos(math.radians(angle))
    rectangle(x, y + 0.01, x + swing_width, y + 0.34, r, g, b)
    circle(x + swing_width - 0.01, y + 0.17, 0.008, 0.8, 0.8, 0.0)

def draw_ethiopian_meal(x, y, is_empty=False):
    rectangle(x-0.08, y, x+0.08, y+0.015, 0.3, 0.3, 0.3) 
    circle(x, y+0.01, 0.07, 0.9, 0.9, 0.9) 
    if not is_empty:
        circle(x, y+0.01, 0.065, 0.8, 0.7, 0.6) 
        circle(x-0.02, y+0.02, 0.012, 0.6, 0.1, 0.0) 
        rectangle(x+0.04, y+0.01, x+0.06, y+0.05, 0.0, 0.5, 0.8) 
    else:
        circle(x, y+0.01, 0.065, 0.85, 0.85, 0.85)

def draw_text(x, y, text, r, g, b):
    glColor3f(r, g, b)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

# -------------------- Style Elements --------------------
def draw_window(x, y, width, height):
    rectangle(x, y, x+width, y+height, 0.4, 0.4, 0.4)
    rectangle(x+0.02, y+0.02, x+width-0.02, y+height-0.02, 0.7, 0.9, 1.0)
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_LINES)
    glVertex2f(x + width/2, y+0.02); glVertex2f(x + width/2, y+height-0.02)
    glVertex2f(x+0.02, y + height/2); glVertex2f(x+width-0.02, y + height/2)
    glEnd()

def draw_plant(x, y):
    rectangle(x-0.03, y, x+0.03, y+0.05, 0.6, 0.3, 0.1)
    circle(x, y+0.07, 0.04, 0.0, 0.8, 0.0)
    circle(x-0.02, y+0.1, 0.03, 0.0, 0.9, 0.0)
    circle(x+0.02, y+0.1, 0.03, 0.0, 0.9, 0.0)
    circle(x, y+0.12, 0.02, 0.2, 0.8, 0.1)

def draw_path_pattern():
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    for i in range(-12, 13):
        x = i * 0.2
        if -1.2 < x < 1.7:
            glVertex2f(x, -0.25); glVertex2f(x, -0.15)
    glEnd()

def draw_roof(x1, x2, y_base, color):
    glColor3f(*color)
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y_base)
    glVertex2f(x2, y_base)
    glVertex2f((x1+x2)/2, y_base + 0.2)
    glEnd()

def draw_building_details():
    draw_window(-0.8, 0.1, 0.15, 0.15)
    draw_window(-0.5, 0.1, 0.15, 0.15)
    draw_window(-0.2, 0.1, 0.15, 0.15)
    draw_window(0.3, 0.1, 0.15, 0.15)
    draw_window(0.7, 0.1, 0.15, 0.15)
    draw_window(1.1, 0.1, 0.15, 0.15)
    draw_window(1.4, 0.1, 0.15, 0.15)
    draw_roof(-0.95, -0.05, 0.6, (0.5, 0.2, 0.1))
    draw_roof(0.05, DINING_HALL_RIGHT, 0.6, (0.4, 0.1, 0.1))

def draw_floor_pattern():
    glColor3f(0.8, 0.7, 0.2)
    glBegin(GL_LINES)
    for x in [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]:
        glVertex2f(x, -0.2); glVertex2f(x, 0.0)
    for y in [-0.15, -0.1, -0.05]:
        glVertex2f(0.05, y); glVertex2f(DINING_HALL_RIGHT - 0.07, y)
    glEnd()

def draw_floor_inside():
    rectangle(0.05, -0.22, DINING_HALL_RIGHT - 0.07, 0.02, 1.0, 0.9, 0.2)
    rectangle(0.05, -0.18, DINING_HALL_RIGHT - 0.07, -0.05, 1.0, 0.95, 0.3)

def draw_sign():
    rectangle(-0.7, 0.5, -0.3, 0.6, 0.8, 0.6, 0.2)
    glColor3f(0,0,0)
    glBegin(GL_LINES)
    glVertex2f(-0.65, 0.53); glVertex2f(-0.35, 0.53)
    glVertex2f(-0.65, 0.57); glVertex2f(-0.35, 0.57)
    glEnd()

def draw_ticket_booth():
    x = TICKET_BOOTH_X - 0.05
    y = -0.25
    rectangle(x, y, x+0.12, y+0.3, 0.6, 0.4, 0.2)
    rectangle(x-0.02, y+0.3, x+0.14, y+0.33, 0.8, 0.2, 0.2)
    rectangle(x+0.02, y+0.1, x+0.10, y+0.25, 0.9, 0.9, 0.8)
    draw_text(x+0.01, y+0.28, "TICKET", 1.0, 1.0, 0.0)

def draw_tree(x, y):
    rectangle(x-0.04, y, x+0.04, y+0.45, 0.5, 0.3, 0.1)
    glColor3f(0.4, 0.2, 0.0)
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex2f(x, y+0.25); glVertex2f(x-0.12, y+0.35)
    glVertex2f(x, y+0.25); glVertex2f(x-0.10, y+0.45)
    glVertex2f(x, y+0.35); glVertex2f(x-0.15, y+0.50)
    glVertex2f(x, y+0.40); glVertex2f(x-0.18, y+0.55)
    glVertex2f(x, y+0.45); glVertex2f(x-0.12, y+0.60)
    glVertex2f(x, y+0.25); glVertex2f(x+0.12, y+0.35)
    glVertex2f(x, y+0.25); glVertex2f(x+0.10, y+0.45)
    glVertex2f(x, y+0.35); glVertex2f(x+0.15, y+0.50)
    glVertex2f(x, y+0.40); glVertex2f(x+0.18, y+0.55)
    glVertex2f(x, y+0.45); glVertex2f(x+0.12, y+0.60)
    glVertex2f(x, y+0.50); glVertex2f(x-0.08, y+0.65)
    glVertex2f(x, y+0.50); glVertex2f(x+0.08, y+0.65)
    glVertex2f(x, y+0.55); glVertex2f(x-0.05, y+0.70)
    glVertex2f(x, y+0.55); glVertex2f(x+0.05, y+0.70)
    glEnd()
    circle(x-0.12, y+0.35, 0.05, 0.0, 0.7, 0.0)
    circle(x-0.10, y+0.45, 0.05, 0.1, 0.8, 0.1)
    circle(x-0.15, y+0.50, 0.06, 0.0, 0.7, 0.0)
    circle(x-0.18, y+0.55, 0.05, 0.2, 0.9, 0.2)
    circle(x-0.12, y+0.60, 0.05, 0.0, 0.8, 0.0)
    circle(x+0.12, y+0.35, 0.05, 0.0, 0.7, 0.0)
    circle(x+0.10, y+0.45, 0.05, 0.1, 0.8, 0.1)
    circle(x+0.15, y+0.50, 0.06, 0.0, 0.7, 0.0)
    circle(x+0.18, y+0.55, 0.05, 0.2, 0.9, 0.2)
    circle(x+0.12, y+0.60, 0.05, 0.0, 0.8, 0.0)
    circle(x-0.08, y+0.65, 0.05, 0.1, 0.8, 0.1)
    circle(x+0.08, y+0.65, 0.05, 0.1, 0.8, 0.1)
    circle(x-0.05, y+0.70, 0.05, 0.0, 0.9, 0.0)
    circle(x+0.05, y+0.70, 0.05, 0.0, 0.9, 0.0)
    circle(x, y+0.72, 0.07, 0.0, 0.8, 0.0)
    circle(x-0.03, y+0.75, 0.04, 0.2, 0.9, 0.2)
    circle(x+0.03, y+0.75, 0.04, 0.2, 0.9, 0.2)
    glLineWidth(1)

# -------------------- Character Rendering --------------------
def draw_realistic_human(s_data):
    x, y = s_data['x'], s_data['y']
    is_walking = s_data.get('is_walking', False)
    state = s_data.get('state', '')
    swing = math.sin(walk_anim * 8) * 0.04 if is_walking else 0
    is_sitting = state in ['waiting_to_eat', 'eating', 'waiting_for_service']
    
    if not is_sitting:
        rectangle(x-0.025 + swing, y, x-0.005 + swing, y + 0.27, *s_data['pant_color'])
        rectangle(x+0.005 - swing, y, x+0.025 - swing, y + 0.27, *s_data['pant_color'])
    torso_y = y + (0.08 if is_sitting else 0.27)
    rectangle(x-0.035, torso_y, x+0.035, torso_y + 0.21, *s_data['shirt_color'])
    
    head_y = torso_y + 0.26
    circle(x, head_y, HEAD_SIZE, 1.0, 0.8, 0.6)
    circle(x, head_y + 0.01, HEAD_SIZE, *s_data['hair_color'])

    if state == 'giving_ticket':
        rectangle(x+0.04, torso_y+0.12, x+0.08, torso_y+0.18, 1.0, 1.0, 0.8)
        draw_text(x+0.045, torso_y+0.13, "MC", 0,0,0)

    if state == 'walking_to_dining':
        draw_ethiopian_meal(x, torso_y + 0.1, is_empty=False)
    elif state == 'returning_dishes':
        draw_ethiopian_meal(x, torso_y + 0.1, is_empty=True)

    if state == 'eating':
        hand_reach = abs(math.sin(walk_anim * 3))
        hand_y = -0.02 + (hand_reach * (head_y - (-0.02) - 0.05))
        rectangle(x + 0.03, torso_y + 0.1, x + 0.05, hand_y, *s_data['shirt_color'])
    elif state == 'waiting_to_eat' and 40 < s_data['wait_timer'] < 140:
        drink_reach = abs(math.sin(walk_anim * 2))
        hand_y = -0.02 + (drink_reach * (head_y - (-0.02) - 0.06))
        rectangle(x + 0.05, hand_y, x + 0.07, hand_y + 0.04, 0.0, 0.5, 0.8)

# -------------------- Logic --------------------
def update(value):
    global walk_anim, counter_occupied, entry_door_angle, exit_door_angle, spawning_allowed
    if not game_active: return
    walk_anim += 0.02 

    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - start_time > 30000:
        spawning_allowed = False

    student_near_entry = any(s['x'] > -1.15 and s['x'] < -0.8 for s in students)
    student_near_exit = any(s['x'] > EXIT_DOOR_X - 0.15 and s['x'] < EXIT_DOOR_X + 0.1 for s in students)
    entry_door_angle = min(90, entry_door_angle + 5) if student_near_entry else max(0, entry_door_angle - 5)
    exit_door_angle = min(90, exit_door_angle + 5) if student_near_exit else max(0, exit_door_angle - 5)

    to_remove = []

    for s in students:
        s['is_walking'] = False

        if s['state'] == 'going_to_ticket':
            s['is_walking'] = True
            if s['x'] < TICKET_BOOTH_X - 0.03:
                s['x'] += STUDENT_SPEED
            else:
                s['state'] = 'giving_ticket'
                s['ticket_timer'] = TICKET_CHECK_DURATION

        elif s['state'] == 'giving_ticket':
            s['ticket_timer'] -= 1
            if s['ticket_timer'] <= 0:
                s['state'] = 'walking_to_serving'

        elif s['state'] == 'walking_to_serving':
            s['x'] += STUDENT_SPEED; s['is_walking'] = True
            if s['x'] >= -0.35:
                if s['id'] not in queue: queue.append(s['id']); s['state'] = 'in_queue'

        elif s['state'] == 'moving_to_counter':
            s['is_walking'] = True
            if abs(s['x'] - (waiter_pos - 0.08)) < HITBOX_SENSITIVITY:
                s['has_food'] = True; s['state'] = 'walking_to_dining'; queue.pop(0); counter_occupied = False
            else: s['x'] += STUDENT_SPEED

        elif s['state'] == 'walking_to_dining':
            s['x'] += STUDENT_SPEED; s['is_walking'] = True
            if s['x'] >= 0.05: s['state'] = 'finding_table'

        elif s['state'] == 'finding_table':
            for idx, t in enumerate(tables):
                if t['status'] == 'clean':
                    s['table_idx'] = idx; t['status'] = 'occupied'; s['state'] = 'moving_to_table'; break

        elif s['state'] == 'moving_to_table':
            s['is_walking'] = True
            target = tables[s['table_idx']]['x'] - 0.04
            if abs(s['x'] - target) < HITBOX_SENSITIVITY:
                s['state'] = 'waiting_to_eat'
                s['wait_timer'] = WAIT_TO_EAT_DURATION
                s['x'] = tables[s['table_idx']]['x'] - 0.15
                s['y'] = -0.1
            else: s['x'] += STUDENT_SPEED

        elif s['state'] == 'waiting_to_eat':
            s['wait_timer'] -= 1
            if s['wait_timer'] <= 0: s['state'] = 'eating'; s['eat_timer'] = EAT_TIME_DURATION

        elif s['state'] == 'eating':
            s['eat_timer'] -= 1
            if s['eat_timer'] <= 0:
                s['state'] = 'waiting_for_service'
                s['service_timer'] = SERVICE_TIME_DURATION

        elif s['state'] == 'waiting_for_service':
            s['service_timer'] -= 1
            if s['service_timer'] <= 0:
                s['state'] = 'returning_dishes'

        elif s['state'] == 'returning_dishes':
            s['is_walking'] = True
            if s['x'] < RETURN_CONTAINER_X - 0.05:
                s['x'] += STUDENT_SPEED 
            else: 
                tables[s['table_idx']]['status'] = 'dirty'
                s['state'] = 'walking_to_exit' 

        elif s['state'] == 'walking_to_exit':
            s['is_walking'] = True
            s['x'] += STUDENT_SPEED
            if s['x'] > EXIT_DOOR_X + 0.15:
                if spawning_allowed:
                    s['x'] = -1.8
                    s['state'] = 'going_to_ticket'
                    s['table_idx'] = -1
                    s['y'] = -0.2
                else:
                    to_remove.append(s)

    for s in to_remove:
        students.remove(s)

    for t in tables:
        if t['status'] == 'dirty':
            t['clean_timer'] += 1
            if t['clean_timer'] > CLEANING_DELAY: t['status'] = 'clean'; t['clean_timer'] = 0

    if not counter_occupied and queue:
        counter_occupied = True
        for s in students:
            if s['id'] == queue[0]: s['state'] = 'moving_to_counter'

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def keyboard(key, x, y):
    global entry_door_angle, exit_door_angle, walk_anim
    if key == b'r' or key == b'R':
        reset_simulation()
        entry_door_angle = 0.0
        exit_door_angle = 0.0
        walk_anim = 0.0
        glutPostRedisplay()
    elif key == b'q' or key == b'Q' or key == b'\x1b':
        sys.exit(0)

def display():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.3, 1.75, -0.8, 0.8, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClear(GL_COLOR_BUFFER_BIT)
    
    rectangle(-1.3, -1, 1.75, 1, 0.2, 0.4, 0.2)
    rectangle(-1.3, -0.25, 1.75, -0.15, 0.3, 0.3, 0.3)
    draw_path_pattern()
    draw_tree(-1.25, -0.2)
    draw_tree(1.68, -0.2)
    
    rectangle(-0.95, -0.2, -0.05, 0.6, 0.7, 0.7, 0.7)
    rectangle(-0.25, -0.2, -0.05, 0.05, 0.4, 0.2, 0.1)
    rectangle(0.05, -0.2, DINING_HALL_RIGHT, 0.6, 0.6, 0.7, 0.8)
    
    draw_floor_inside()
    draw_floor_pattern()
    
    draw_ticket_booth()
    
    draw_animated_door(-0.93, -0.2, entry_door_angle, 0.5, 0.3, 0.1)
    draw_animated_door(EXIT_DOOR_X, -0.2, exit_door_angle, 0.5, 0.3, 0.1)
    
    rectangle(RETURN_CONTAINER_X - 0.08, -0.2, RETURN_CONTAINER_X, 0.2, 0.4, 0.4, 0.4)
    rectangle(RETURN_CONTAINER_X - 0.07, 0.0, RETURN_CONTAINER_X - 0.01, 0.12, 0.1, 0.1, 0.1)
    
    for t in tables:
        rectangle(t['x']-0.1, -0.2, t['x']-0.08, -0.05, 0.3, 0.15, 0.05)
        rectangle(t['x']-0.02, -0.2, t['x']+0.0, -0.05, 0.3, 0.15, 0.05)
        rectangle(t['x']+0.0, -0.2, t['x']+0.02, -0.05, 0.3, 0.15, 0.05)
        rectangle(t['x']+0.08, -0.2, t['x']+0.1, -0.05, 0.3, 0.15, 0.05)
        rectangle(t['x']-0.1, -0.05, t['x']+0.1, 0.0, 0.5, 0.3, 0.1)
        
        for s in students:
            if s['table_idx'] == tables.index(t) and s['state'] in ['waiting_to_eat', 'eating', 'waiting_for_service']:
                draw_ethiopian_meal(t['x'], -0.03, is_empty=False)
                break
    
    draw_building_details()
    draw_sign()
    draw_plant(-1.1, -0.2)
    draw_plant(1.6, -0.2)
    
    draw_realistic_human(ticket_officer)
    draw_realistic_human(waiter)
    for s in students:
        draw_realistic_human(s)
    
    glutSwapBuffers()

# -------------------- Run --------------------
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(1300, 600)
glutCreateWindow(b"Mekdela Amba University Student Cafe Simulation")
reset_simulation()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutTimerFunc(0, update, 0)
glutMainLoop()   # <-- Corrected function name (capital L)
