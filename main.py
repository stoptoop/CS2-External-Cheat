import pymem
import pymem.process
import win32gui, win32con, win32api
import time, os
import imgui
from imgui.integrations.glfw import GlfwRenderer
from pynput.mouse import Controller, Button
import glfw
import OpenGL.GL as gl
import requests
from random import uniform
import keyboard
import math

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()

dwEntityList = offsets['client.dll']['dwEntityList']
dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
dwLocalPlayerController = offsets['client.dll']['dwLocalPlayerController']
dwViewMatrix = offsets['client.dll']['dwViewMatrix']
m_flFlashMaxAlpha = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_flFlashMaxAlpha']
m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
m_ArmorValue = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_ArmorValue']
m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
m_pInventoryServices = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_pInventoryServices']
m_hActiveWeapon = client_dll['client.dll']['classes']['CPlayer_WeaponServices']['fields']['m_hActiveWeapon']
m_szWeaponName = client_dll['client.dll']['classes']['CCSWeaponBaseVData']['fields']['m_szName']
m_iDesiredFOV = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iDesiredFOV']
m_bDidSmokeEffect = client_dll['client.dll']['classes']['C_SmokeGrenadeProjectile']['fields']['m_bDidSmokeEffect']



show_hp_bar = True
show_armor_bar = True
custom_font = None  
aim_targets = [] 
aim_key = 0x05
show_health_text = True
show_armor_text = True
fov_color = [1.0, 1.0, 1.0]
tracer_color = [1.0, 1.0, 1.0]
skeleton_color = [1.0, 1.0, 1.0]
esp_box_color = [1.0, 1.0, 1.0]
show_tracer = False
show_skeleton = True
show_esp = True
show_menu = True
anti_flash = False
custom_fov = False
custom_fov_resolution = 90
show_logo = True
show_aimbot = True
aimbot_smooth = 2.0 
aimbot_fov = 190 

while True:
    time.sleep(1)
    try:
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        break
    except:
        pass
    
    
    
def version_control():
    url = "https://api.github.com/repos/stoptoop/CS2-External-Cheat/releases"
    response = requests.get(url)
    if response.status_code == 200:
        releases = response.json()
        if releases:
            latest = releases[0]
            return latest["tag_name"]
version = version_control()    
time.sleep(1)
os.system("cls")
pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

def w2s(mtx, posx, posy, posz, width, height):
    screenW = mtx[12]*posx + mtx[13]*posy + mtx[14]*posz + mtx[15]
    if screenW > 0.001:
        screenX = mtx[0]*posx + mtx[1]*posy + mtx[2]*posz + mtx[3]
        screenY = mtx[4]*posx + mtx[5]*posy + mtx[6]*posz + mtx[7]
        camX = width / 2
        camY = height / 2
        x = camX + (camX * screenX / screenW) // 1
        y = camY - (camY * screenY / screenW) // 1
        return [x, y]
    return [-999, -999]

def esp(draw_list):
    global aim_targets
    aim_targets.clear()
    global custom_font, logo_font
    view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
    screen_center_x = WINDOW_WIDTH // 2
    screen_center_y = WINDOW_HEIGHT // 2
    screen_top_x = WINDOW_WIDTH // 2
    screen_top_y = 0
    screen_bottom_x = WINDOW_WIDTH // 2
    screen_bottom_y = WINDOW_HEIGHT
    for i in range(64):
        local_player = pm.read_longlong(client + dwLocalPlayerPawn)
        try:
            local_team = pm.read_int(local_player + m_iTeamNum)
            local_pos_x = pm.read_float(local_player + m_vecAbsOrigin)
            local_pos_y = pm.read_float(local_player + m_vecAbsOrigin + 0x4)
            local_pos_z = pm.read_float(local_player + m_vecAbsOrigin + 0x8)

        except:
            return
        entity = pm.read_longlong(client + dwEntityList)
        if not entity:
            continue

        list_entry = pm.read_longlong(entity + ((8 * (i & 0x7FFF) >> 9) + 16))
        if not list_entry:
            continue

        entity_controller = pm.read_longlong(list_entry + (120) * (i & 0x1FF))
        if not entity_controller:
            continue

        entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
        if not entity_controller_pawn:
            continue

        list_entry = pm.read_longlong(entity + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
        if not list_entry:
            continue

        entity_pawn = pm.read_longlong(list_entry + (120) * (entity_controller_pawn & 0x1FF))
        if not entity_pawn or entity_pawn == local_player:
            continue

        if pm.read_int(entity_pawn + m_lifeState) != 256:
            continue

        if pm.read_int(entity_pawn + m_iTeamNum) == local_team:
            continue
        game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
        bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
        try:
            headX = pm.read_float(bone_matrix + 6 * 0x20)
            headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
            headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8)
            head_pos = w2s(view_matrix, headX, headY, headZ + 8, WINDOW_WIDTH, WINDOW_HEIGHT)
            head_pos_aimbot = w2s(view_matrix, headX, headY, headZ, WINDOW_WIDTH, WINDOW_HEIGHT)
            
            if -999 not in head_pos:
                aim_targets.append({
                "pos": head_pos_aimbot,
                "entity_pawn": entity_pawn,
                "head_world": (headX, headY, headZ),
            })
                
            legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
            leg_pos = w2s(view_matrix, headX, headY, legZ, WINDOW_WIDTH, WINDOW_HEIGHT)
            bodyX = pm.read_float(bone_matrix + 3 * 0x20)
            bodyY = pm.read_float(bone_matrix + 3 * 0x20 + 0x4)
            bodyZ = pm.read_float(bone_matrix + 3 * 0x20 + 0x8)
            body_pos = w2s(view_matrix, bodyX, bodyY, bodyZ, WINDOW_WIDTH, WINDOW_HEIGHT)
            entity_hp = pm.read_int(entity_pawn + m_iHealth)
            if entity_hp <= 0:
                continue
            box_color = imgui.get_color_u32_rgba(*esp_box_color, 1.0)
            hp_percent = entity_hp / 100.0
            hp_bar_color = imgui.get_color_u32_rgba(
                2.0 * (1 - hp_percent),
                2.0 * hp_percent,
                0,
                1
            )
            tracer_color = imgui.get_color_u32_rgba(
                2.0 * (1 - hp_percent),
                2.0 * hp_percent,
                0,
                0.7  
            )
            if show_tracer and -999 not in body_pos:
                draw_list.add_line(
                    screen_bottom_x, screen_bottom_y,
                    body_pos[0], body_pos[1],
                    tracer_color, 0.3
                )
                
            delta = abs(head_pos[1] - leg_pos[1])
            leftX = head_pos[0] - delta // 3
            rightX = head_pos[0] + delta // 3
            if show_esp:
                draw_list.add_line(leftX,  leg_pos[1],  rightX, leg_pos[1],  box_color, 1.0)
                draw_list.add_line(leftX,  leg_pos[1],  leftX,  head_pos[1], box_color, 1.0)
                draw_list.add_line(rightX, leg_pos[1],  rightX, head_pos[1], box_color, 1.0)
                draw_list.add_line(leftX,  head_pos[1], rightX, head_pos[1], box_color, 1.0)
            try:
                bar_width = 3  
                bar_height = delta
                bar_x = leftX - 2 - bar_width 
                bar_y = head_pos[1] 
                if show_hp_bar:
                    draw_list.add_rect_filled(
                        bar_x, bar_y,
                        bar_x + bar_width, bar_y + bar_height,
                        imgui.get_color_u32_rgba(0.3, 0.3, 0.3, 0.7)
                    )
                    filled_height = bar_height * hp_percent
                    draw_list.add_rect_filled(
                        bar_x, bar_y + (bar_height - filled_height),
                        bar_x + bar_width, bar_y + bar_height,
                        hp_bar_color
                    )
                    draw_list.add_rect(
                        bar_x, bar_y,
                        bar_x + bar_width, bar_y + bar_height,
                        imgui.get_color_u32_rgba(1, 1, 1, 0.5),
                        0, 1
                    )
                if custom_font is not None:
                    imgui.push_font(custom_font) 
                if show_health_text:
                    draw_list.add_text(leftX - 35, body_pos[1] - 15, hp_bar_color, str(entity_hp))
                if custom_font is not None:
                    imgui.pop_font()
            except Exception as e:
                print(f"Error drawing HP bar: {e}")
                pass
            try:
                entity_armor = pm.read_int(entity_pawn + m_ArmorValue)
                armor_percent = entity_armor / 100.0
                armor_bar_width = 3
                armor_bar_height = delta
                armor_bar_x = bar_x - 2 - armor_bar_width 
                armor_bar_y = head_pos[1]
                armor_bar_color = imgui.get_color_u32_rgba(0.2, 0.4, 1.0, 1.0)
                if show_armor_bar:
                    draw_list.add_rect_filled(
                        armor_bar_x, armor_bar_y,
                        armor_bar_x + armor_bar_width, armor_bar_y + armor_bar_height,
                        imgui.get_color_u32_rgba(0.3, 0.3, 0.3, 0.7)
                    )
                    filled_armor_height = armor_bar_height * armor_percent
                    draw_list.add_rect_filled(
                        armor_bar_x, armor_bar_y + (armor_bar_height - filled_armor_height),
                        armor_bar_x + armor_bar_width, armor_bar_y + armor_bar_height,
                        armor_bar_color
                    )
                    draw_list.add_rect(
                        armor_bar_x, armor_bar_y,
                        armor_bar_x + armor_bar_width, armor_bar_y + armor_bar_height,
                        imgui.get_color_u32_rgba(1, 1, 1, 0.5),
                        0, 1
                    )
                if custom_font is not None:
                    imgui.push_font(custom_font)
                if show_armor_text:
                    draw_list.add_text(leftX - 35, body_pos[1] - 35, armor_bar_color, str(entity_armor))
                if custom_font is not None:
                    imgui.pop_font()
            except Exception as e:
                print(f"Error drawing armor bar: {e}")
                pass
            try:
                player_name_bytes = pm.read_bytes(entity_controller + 0x660, 128)
                player_name = player_name_bytes.split(b'\x00', 1)[0].decode('utf-8', errors='ignore')
                text_size = imgui.calc_text_size(player_name)
                text_x = leg_pos[0] - (text_size[0] / 2)
                if custom_font is not None:
                    imgui.push_font(custom_font)
                draw_list.add_text(
                    text_x, leg_pos[1] + 5, 
                    imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0),
                    player_name
                )
                if custom_font is not None:
                    imgui.pop_font()
            except:
                pass
            try:
                weapon_pointer = pm.read_longlong(entity_pawn + m_pClippingWeapon)
                weapon_index = pm.read_int(weapon_pointer + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
                weapon_name = get_weapon_name_by_index(weapon_index)
                text_size = imgui.calc_text_size(weapon_name)
                weapon_name_x = head_pos[0] - text_size[0] / 2
                weapon_name_y = head_pos[1] - 18 
                if custom_font is not None:
                    imgui.push_font(custom_font)
                draw_list.add_text(
                    weapon_name_x,
                    weapon_name_y,
                    imgui.get_color_u32_rgba(1, 1, 1, 1), 
                    weapon_name
                )
                if custom_font is not None:
                    imgui.pop_font()
            except Exception as e:
                print(f"Error reading weapon: {e}")
                pass
            if show_skeleton:
                draw_skeleton(draw_list, view_matrix, entity_pawn)
        except Exception as e:
            continue


def logo(draw_list):
    try:
        if logo_font is not None:
            imgui.push_font(logo_font)  
        logo_text = f"Lensor | {version} | {imgui.get_io().framerate:.1f} FPS"
        text_size = imgui.calc_text_size(logo_text)
        draw_list.add_rect_filled(8, 8, 8 + text_size[0] + 4, 8 + text_size[1] + 4, imgui.get_color_u32_rgba(0, 0, 0, 0.4), 4)
        draw_list.add_text(10, 10, imgui.get_color_u32_rgba(1, 1, 1, 0.9), logo_text)
        if logo_font is not None:
            imgui.pop_font()
    except Exception as e:
        print(f"Error drawing logo: {e}")
        pass


def aimbot(draw_list):
    screen_center_x = WINDOW_WIDTH / 2
    screen_center_y = WINDOW_HEIGHT / 2
    draw_list.add_circle(
        screen_center_x,
        screen_center_y,
        aimbot_fov,  
        imgui.get_color_u32_rgba(*fov_color, 1.0),
        64, 1.0
    )
    if not win32api.GetAsyncKeyState(aim_key):
        return
    if not aim_targets:
        return
    best_target = None
    best_dist = float('inf')

    for target in aim_targets:
        pos = target["pos"]
        dx = pos[0] - screen_center_x
        dy = pos[1] - screen_center_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < aimbot_fov and dist < best_dist:
            best_dist = dist
            best_target = target

    if best_target is not None:
        target_x, target_y = best_target["pos"]
        dx = int(target_x - screen_center_x)
        dy = int(target_y - screen_center_y)
        smooth_dx = int(dx / aimbot_smooth)
        smooth_dy = int(dy / aimbot_smooth)
        if abs(smooth_dx) < 1 and abs(smooth_dy) < 1:
            smooth_dx = int(math.copysign(1, dx)) if dx != 0 else 0
            smooth_dy = int(math.copysign(1, dy)) if dy != 0 else 0
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, smooth_dx, smooth_dy, 0, 0)

def draw_skeleton(draw_list, view_matrix, entity_pawn):
    game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
    bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
    SKELETON_COLOR = imgui.get_color_u32_rgba(*skeleton_color, 1.0)
    bones = {
        'head': 6,
        'neck': 5,
        'torso': 3,
        'left_shoulder': 8,
        'left_elbow': 9,
        'left_hand': 10,
        'right_shoulder': 13,
        'right_elbow': 14,
        'right_hand': 15,
        'left_hip': 22,
        'left_knee': 23,
        'left_foot': 24,
        'right_hip': 25,
        'right_knee': 26,
        'right_foot': 27
    }
    bone_positions = {}
    for name, idx in bones.items():
        try:
            bone_x = pm.read_float(bone_matrix + idx * 0x20)
            bone_y = pm.read_float(bone_matrix + idx * 0x20 + 0x4)
            bone_z = pm.read_float(bone_matrix + idx * 0x20 + 0x8)
            bone_positions[name] = w2s(view_matrix, bone_x, bone_y, bone_z, WINDOW_WIDTH, WINDOW_HEIGHT)
        except:
            bone_positions[name] = (-999, -999)
    if -999 not in bone_positions['head'] and -999 not in bone_positions['neck']:
        draw_list.add_line(
            bone_positions['head'][0], bone_positions['head'][1],
            bone_positions['neck'][0], bone_positions['neck'][1],
            SKELETON_COLOR, 1.5
        )
    if -999 not in bone_positions['neck'] and -999 not in bone_positions['torso']:
        draw_list.add_line(
            bone_positions['neck'][0], bone_positions['neck'][1],
            bone_positions['torso'][0], bone_positions['torso'][1],
            SKELETON_COLOR, 1.5
        )
    if all(-999 not in bone_positions[x] for x in ['torso', 'left_shoulder', 'left_elbow', 'left_hand']):
        draw_list.add_line(
            bone_positions['torso'][0], bone_positions['torso'][1],
            bone_positions['left_shoulder'][0], bone_positions['left_shoulder'][1],
            SKELETON_COLOR, 1.5
        )
        draw_list.add_line(
            bone_positions['left_shoulder'][0], bone_positions['left_shoulder'][1],
            bone_positions['left_elbow'][0], bone_positions['left_elbow'][1],
            SKELETON_COLOR, 1.5
        )
        draw_list.add_line(
            bone_positions['left_elbow'][0], bone_positions['left_elbow'][1],
            bone_positions['left_hand'][0], bone_positions['left_hand'][1],
            SKELETON_COLOR, 1.5
        )
    if all(-999 not in bone_positions[x] for x in ['torso', 'right_shoulder', 'right_elbow', 'right_hand']):
        draw_list.add_line(
            bone_positions['torso'][0], bone_positions['torso'][1],
            bone_positions['right_shoulder'][0], bone_positions['right_shoulder'][1],
            SKELETON_COLOR, 1.5
        )
        draw_list.add_line(
            bone_positions['right_shoulder'][0], bone_positions['right_shoulder'][1],
            bone_positions['right_elbow'][0], bone_positions['right_elbow'][1],
            SKELETON_COLOR, 1.5
        )
        draw_list.add_line(
            bone_positions['right_elbow'][0], bone_positions['right_elbow'][1],
            bone_positions['right_hand'][0], bone_positions['right_hand'][1],
            SKELETON_COLOR, 1.5
        )
    if all(-999 not in bone_positions[x] for x in ['torso', 'left_hip', 'left_knee', 'left_foot']):
        draw_list.add_line(
            bone_positions['torso'][0], bone_positions['torso'][1],
            bone_positions['left_hip'][0], bone_positions['left_hip'][1],
            SKELETON_COLOR, 1.5
        )
        draw_list.add_line(
            bone_positions['left_hip'][0], bone_positions['left_hip'][1],
            bone_positions['left_knee'][0], bone_positions['left_knee'][1],
            SKELETON_COLOR, 1.5
        )
        draw_list.add_line(
            bone_positions['left_knee'][0], bone_positions['left_knee'][1],
            bone_positions['left_foot'][0], bone_positions['left_foot'][1],
            SKELETON_COLOR, 1.5
        )
    if all(-999 not in bone_positions[x] for x in ['torso', 'right_hip', 'right_knee', 'right_foot']):
        draw_list.add_line(
            bone_positions['torso'][0], bone_positions['torso'][1],
            bone_positions['right_hip'][0], bone_positions['right_hip'][1],
            SKELETON_COLOR, 1.5
        )
        draw_list.add_line(
            bone_positions['right_hip'][0], bone_positions['right_hip'][1],
            bone_positions['right_knee'][0], bone_positions['right_knee'][1],
            SKELETON_COLOR, 1.5
        )
        draw_list.add_line(
            bone_positions['right_knee'][0], bone_positions['right_knee'][1],
            bone_positions['right_foot'][0], bone_positions['right_foot'][1],
            SKELETON_COLOR, 1.5
        )

def flash():
    local_player = pm.read_longlong(client + dwLocalPlayerPawn)
    pm.write_float(local_player + m_flFlashMaxAlpha,0.0)





def fov(custom_fov_resolution):
    try:
        local_player_controller = pm.read_longlong(client + dwLocalPlayerController)
        pm.write_int(local_player_controller + m_iDesiredFOV, custom_fov_resolution)
    except Exception as e:
        pass




def draw_menu():
    global show_esp, show_aimbot, aimbot_fov, custom_font, esp_box_color, aimbot_smooth, show_hp_bar
    global anti_flash, custom_fov, show_logo, custom_fov_resolution, show_skeleton, fov_color
    global show_tracer, skeleton_color, show_armor_text, show_health_text, tracer_color, aim_key, show_armor_bar

    if menu_font is not None:
        imgui.push_font(menu_font)
        
                         #      w    h
    imgui.set_next_window_size(410, 465)
    imgui.set_next_window_position(10, 10)
    imgui.begin("Lensor External", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE)


    if imgui.begin_tab_bar("MainTabs", imgui.TAB_BAR_NONE):
        if imgui.begin_tab_item("ESP")[0]:
            _, show_esp = imgui.checkbox("ESP", show_esp)
            imgui.indent(11)
            imgui.text("Esp Box Color")
            _, esp_box_color = imgui.color_edit3("##esp_box_color", *esp_box_color)
            _, show_hp_bar = imgui.checkbox("Show HP bar", show_hp_bar)
            _, show_armor_bar = imgui.checkbox("Show armor bar", show_armor_bar)
            imgui.unindent(11)
            imgui.separator()
            _, show_tracer = imgui.checkbox("Tracer", show_tracer)
            imgui.indent(11)
            imgui.text("Tracer Color")
            _, tracer_color = imgui.color_edit3("##tracer_color", *tracer_color)
            imgui.unindent(11)
            imgui.separator()
            
            
            _, show_skeleton = imgui.checkbox("Skeleton", show_skeleton)
            imgui.indent(11)
            imgui.text("Skeleton Color")
            _, skeleton_color = imgui.color_edit3("##skeleton_color", *skeleton_color)
            imgui.unindent(11)
            imgui.separator()
            _, show_logo = imgui.checkbox("Show Logo", show_logo)
            _, show_health_text = imgui.checkbox("Health Text", show_health_text)
            _, show_armor_text = imgui.checkbox("Armor Text", show_armor_text)
            imgui.end_tab_item()

        if imgui.begin_tab_item("COMBAT")[0]:
            _, show_aimbot = imgui.checkbox("Aimbot", show_aimbot)
            imgui.indent(11)
            if imgui.begin_combo("Aimbot Key", key_names.get(aim_key, f"VK_{aim_key:02X}")):
                for code, name in key_names.items():
                    is_selected = (aim_key == code)
                    if imgui.selectable(name, is_selected)[0]:
                        aim_key = code
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()
            _, aimbot_fov = imgui.slider_int("Aimbot FOV", aimbot_fov, 50, 400)
            _, aimbot_smooth = imgui.slider_int("Aimbot Smooth", aimbot_smooth, 1, 7)
            imgui.text("Aimbot fov color")
            _, fov_color = imgui.color_edit3("##aim_bot_fov_color", *fov_color)
            imgui.unindent(11)
            imgui.separator()
            _, anti_flash = imgui.checkbox("Anti Flash", anti_flash)
            _, custom_fov = imgui.checkbox("Custom Fov", custom_fov)
            imgui.indent(11)
            imgui.text("Custom Fov Resolution")
            _, custom_fov_resolution = imgui.slider_int("##custom_fov_slider", custom_fov_resolution, 90, 160)
            imgui.unindent(11)
            imgui.end_tab_item()

        imgui.end_tab_bar()

    imgui.end()
    if menu_font is not None:
        imgui.pop_font()






def main():
    global custom_font, logo_font, menu_font
    glfw.init()
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "overlay", None, None)
    hwnd = glfw.get_win32_window(window)
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    ex_style = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, -2, -2, 0, 0,
                          win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
    glfw.make_context_current(window)
    imgui.create_context()
    impl = GlfwRenderer(window)
    io = imgui.get_io()
    logo_font = io.fonts.add_font_from_file_ttf("cuyabra-Regular.ttf", 22)
    menu_font = io.fonts.add_font_from_file_ttf("Firasanslight.ttf", 18)
    custom_font = io.fonts.add_font_from_file_ttf("Firasanslight.ttf", 16)
    impl.refresh_font_texture()
    show_menu = False
    last_state = 0
    
    style1 = imgui.get_style()
    colors = imgui.get_style().colors


    style1.window_rounding = 8.0
    style1.frame_rounding = 6.0
    style1.grab_rounding = 3.0
    style1.popup_rounding = 6.0
    style1.child_rounding = 6.0
    style1.scrollbar_rounding = 6.0
    style1.tab_rounding = 6.0
    colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.0, 0.0, 0.0, 0.8)
    colors[imgui.COLOR_TEXT] = (0.6, 0.0, 0.8, 1.0)
    colors[imgui.COLOR_BUTTON] = (0.3, 0.0, 0.5, 1.0)
    colors[imgui.COLOR_BUTTON_HOVERED] = (0.4, 0.0, 0.6, 1.0)
    colors[imgui.COLOR_BUTTON_ACTIVE] = (0.5, 0.0, 0.7, 1.0)
    colors[imgui.COLOR_TITLE_BACKGROUND] = (0.2, 0.0, 0.4, 1.0)
    colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.3, 0.0, 0.5, 1.0)
    colors[imgui.COLOR_TITLE_BACKGROUND_COLLAPSED] = (0.1, 0.0, 0.2, 1.0)
    element_alpha = 1
    black = (0.0, 0.0, 0.0, element_alpha)
    colors[imgui.COLOR_FRAME_BACKGROUND] = black
    colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.1, 0.0, 0.1, element_alpha)
    colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = (0.2, 0.0, 0.3, element_alpha)
    colors[imgui.COLOR_SLIDER_GRAB] = (0.5, 0.0, 0.8, 1.0)
    colors[imgui.COLOR_SLIDER_GRAB_ACTIVE] = (0.7, 0.0, 1.0, 1.0)
    colors[imgui.COLOR_CHECK_MARK] = (0.7, 0.2, 1.0, 1.0)
    
    colors[imgui.COLOR_SEPARATOR] = (0.0, 0.0, 0.0, 0.8)
    
    colors[imgui.COLOR_TAB] = (0.0, 0.0, 0.0, 0.9)
    colors[imgui.COLOR_TAB_ACTIVE] = (0.1, 0.1, 0.1, 1.0)
    colors[imgui.COLOR_TAB] = (0.0, 0.0, 0.0, 0.9)
    colors[imgui.COLOR_TAB_HOVERED] = (0.0, 0.0, 0.0, 1.0)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        current_state = win32api.GetAsyncKeyState(win32con.VK_INSERT)
        if current_state & 1 and last_state & 1 == 0:
            show_menu = not show_menu
            if show_menu:
                ex_style = win32con.WS_EX_LAYERED 
            else:
                ex_style = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT 
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, -2, -2, 0, 0,
                                  win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        last_state = current_state
        imgui.new_frame()
        imgui.set_next_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        imgui.set_next_window_position(0, 0)
        imgui.begin("overlay",
                    flags=imgui.WINDOW_NO_TITLE_BAR |
                          imgui.WINDOW_NO_RESIZE |
                          imgui.WINDOW_NO_SCROLLBAR |
                          imgui.WINDOW_NO_COLLAPSE |
                          imgui.WINDOW_NO_BACKGROUND)
        draw_list = imgui.get_window_draw_list()
        if show_menu:
            draw_menu()
        if show_aimbot:
            aimbot(draw_list)
        if anti_flash:
            flash()
        if custom_fov:
            fov(custom_fov_resolution)
        if show_logo:
            logo(draw_list)
            
        esp(draw_list)
        imgui.end()
        imgui.end_frame()
        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
    impl.shutdown()
    glfw.terminate()

def get_weapon_name_by_index(index):
    weapon_names = {
    32: "P2000",
    61: "USP-S",
    4: "Glock",
    2: "Dual Berettas",
    36: "P250",
    30: "Tec-9",
    63: "CZ75-Auto",
    1: "Desert Eagle",
    3: "Five-SeveN",
    64: "R8",
    35: "Nova",
    25: "XM1014",
    27: "MAG-7",
    29: "Sawed-Off",
    14: "M249",
    28: "Negev",
    17: "MAC-10",
    23: "MP5-SD",
    24: "UMP-45",
    19: "P90",
    26: "Bizon",
    34: "MP9",
    33: "MP7",
    10: "FAMAS",
    16: "M4A4",
    60: "M4A1-S",
    8: "AUG",
    43: "Galil",
    7: "AK-47",
    39: "SG 553",
    40: "SSG 08",
    9: "AWP",
    38: "SCAR-20",
    11: "G3SG1",
    43: "Flashbang",
    44: "Hegrenade",
    45: "Smoke",
    46: "Molotov",
    47: "Decoy",
    48: "Incgrenage",
    49: "C4",
    31: "Taser",
    42: "Knife",
    41: "Knife Gold",
    59: "Knife",
    80: "Knife Ghost",
    500: "Knife Bayonet",
    505: "Knife Flip",
    506: "Knife Gut",
    507: "Knife Karambit",
    508: "Knife M9",
    509: "Knife Tactica",
    512: "Knife Falchion",
    514: "Knife Survival Bowie",
    515: "Knife Butterfly",
    516: "Knife Rush",
    519: "Knife Ursus",
    520: "Knife Gypsy Jackknife",
    522: "Knife Stiletto",
    523: "Knife Widowmaker"
}
    return weapon_names.get(index, 'Unknown')


key_names = {
    0x05: "Mouse4",
    0x06: "Mouse5",
    0x10: "Shift",
    0x11: "Ctrl",
    0x12: "Alt",
    0x09: "Tab",
    0x04: "Middle mouse"
}



if __name__ == '__main__':
    main()