"""
Blender Character and Weapon Animation Rendering Script
======================================================

This script automates the rendering of character and weapon animations for sprite sheets.
It's designed to handle two separate rendering pipelines that can be used independently.

FEATURES:
- Character animations: Full set of character animations with multiple character variants
- Weapon animations: Weapon-specific animations that can be reused across characters
- Dynamic camera switching: Automatically uses appropriate camera for each animation type
- Mining axe visibility control: Shows/hides mining tool based on animation context
- Flexible character selection: Easy switching between character variants (mc1-mc5)

PIPELINES:
1. Character Pipeline: Renders all character animations for a selected character variant
2. Weapon Pipeline: Renders weapon animations independently (no character selection needed)

USAGE:
1. Set render_character_animations = True for character rendering
2. Set render_weapon_animations = True for weapon rendering
3. For character rendering, also set the desired character in character_config
4. Run the script in Blender

OUTPUT DIRECTORIES:
- Character animations: C:\tmp\{character_name}\ (e.g., C:\tmp\mc5\)
- Weapon animations: C:\tmp\weapon_animations\

REQUIREMENTS:
- Armature named "Armature" must exist in the scene
- Camera.Ortho (for character animations) and Camera.Ortho.Weapons (for weapon animations)
- All animation actions must be present in the Blender file
- mining_axe object (optional, for mining animation)

CAMERA MAPPING:
- Weapon animations automatically map to specific camera actions
- Character animations use default camera behavior
- Camera visibility is automatically controlled based on animation type
"""

import bpy
import os

# Animation pipeline selection
# Set only ONE of these to True
render_character_animations = True   # Set to True to render character animations
render_weapon_animations = False     # Set to True to render weapon animations

# Validate pipeline selection
if render_character_animations and render_weapon_animations:
    raise Exception("Error: You can only select ONE animation pipeline at a time. Please set either render_character_animations OR render_weapon_animations to True, not both.")
elif not render_character_animations and not render_weapon_animations:
    raise Exception("Error: You must select ONE animation pipeline. Please set either render_character_animations OR render_weapon_animations to True.")

# List of character animation names and their corresponding export names
character_animations = [
    # ["01_wield_attack_1_still", "1h_melee_atk_1_sc"],
    # ["02_wield_attack_2", "1h_melee_atk_2_sc"],
    # ["03_wield_attack_3", "1h_melee_atk_3_sc"],
    # ["04_air_attack_1", "air_atk_1_sc"],
    # ["05_air_attack_2", "air_atk_2_sc"],
    # ["06_air_attack_3", "air_atk_3_sc"],
    # ["07_air_south_atk_1", "a_south_atk_sc"],
    # ["08_attack_launcher", "up_atk_1_sc"],
    # ["09_frontdash", "dash_sc"],
    # ["10_block_fail", "block_fail"],
    # ["11_block_success", "block_success"],
    # ["12_dashattack", "dash_atk_sc"],
    # ["13_ready_battle", "idle_battle"],
    # ["14_float", "float_sc"],
    # ["15_panch", "g_atk_1_sc"],
    # ["16_panchhook", "hook_sc"],
    # ["17_kick", "g_atk_2_sc"],
    # ["18_endcombo", "g_atk_3_sc"],
    # ["19_g_d_atk_1", "g_d_atk_1"],
    # ["20_back_kick", "gf_back_kick"],
    # ["21_hit_1", "hit_1"],
    # ["22_hit_2", "hit_2"],
    # ["23_hit_3", "hit_3"],
    # ["24_jump", "jump_sc"],
    # ["25_mining", "mining_sc"],
    # ["26_ready", "idle_sc"],
    # ["27_ready_new", "idle_2"],
    # ["28_shot", "range_atk"],
    # ["29_run", "run_sc"],
    # ["30_pre_run", "pre_run"],
    # ["31_super_punch", "super_punch_sc"],
    # ["32_supermove", "supermove"],
    # ["33_victory_pose", "victory_pose"],
    # ["34_dragonpunch","dragonpunch"],
    # ["35_dragonpunch","dragonpunch_2"],
    # ["36_dragonpunch","dragonpunch_3"],
    # ["37_die","die"],
    # ["39_panch_2","g_atk_12_sc"],
    # ["40_kick_2","g_atk_22_sc"],
    # ["41_kick_two","kick_two"],
    # ["42_boost","boost"],
    # ["43_wield_attack_4", "1h_melee_atk_4_sc"],
    # ["44_wield_attack_1_air", "1h_melee_atk_1_air_sc"],
    # ["45_wield_attack_2_air", "1h_melee_atk_2_air_sc"],
]

# Dynamic character animations that need action reset after each render
dynamic_character_animations = [
    ["44_2h_gatk","axe_wide_swing"]
    ["38_dive_kick","dive_kick"],
]

# Weapon animations 
weapon_animations = [
    # ["01_wield_attack_1_still", "1h_melee_atk_1_sc"],
    # ["02_wield_attack_2", "1h_melee_atk_2_sc"],
    # ["03_wield_attack_3", "1h_melee_atk_3_sc"],
    # ["43_wield_attack_4", "1h_melee_atk_4_sc"],
    # ["44_wield_attack_1_air", "1h_melee_atk_1_air_sc"],
    # ["45_wield_attack_2_air", "1h_melee_atk_2_air_sc"],
    ["44_2h_gatk","axe_wide_swing"]
]

# Output directory for weapon animations
weapon_animations_output_dir = r"C:\tmp\weapon_animations"

# Character configuration - set exactly ONE to True for character animations
# (This is ignored when rendering weapon animations)
character_config = {
    # "mc1": True,  # Red character variant
    # "mc2": True,  # Blue character variant  
    # "mc3": True,  # Green character variant
    # "mc4": True,  # Yellow character variant
    # "mc5": True,   # Grey character variant,
    "mc6": True     # Swordsman
}

# Validate character configuration for character animations
def validate_character_config():
    if not render_character_animations:
        return  # No validation needed for weapon animations
    
    active_characters = [char for char, is_active in character_config.items() if is_active]
    
    if len(active_characters) == 0:
        raise Exception("Error: No character selected for character animation rendering. Please set exactly one character in character_config to True.")
    elif len(active_characters) > 1:
        raise Exception(f"Error: Multiple characters selected ({', '.join(active_characters)}). Please set exactly one character in character_config to True.")
    
    return active_characters[0]

# Get the character output directory based on active character (only needed for character animations)
character_output_dir = None
if render_character_animations:
    selected_character = validate_character_config()
    character_output_dir = fr"C:\tmp\{selected_character}"

# Ensure the appropriate output directory exists
if render_character_animations:
    os.makedirs(character_output_dir, exist_ok=True)
    print(f"Character animations will be saved to: {character_output_dir}")
elif render_weapon_animations:
    os.makedirs(weapon_animations_output_dir, exist_ok=True)
    print(f"Weapon animations will be saved to: {weapon_animations_output_dir}")

# Name of the armature to animate
armature_name = "Armature"

# Names of the cameras
character_camera_name = "Camera.Ortho"       # Camera for character animations
weapon_camera_name = "Camera.Ortho.Weapons"  # Camera for weapon animations

# Get the current scene
scene = bpy.context.scene

# Get the camera objects
character_camera = bpy.data.objects.get(character_camera_name)
if not character_camera:
    print(f"Warning: Camera '{character_camera_name}' not found. Character camera animations will not be applied.")

weapon_camera = bpy.data.objects.get(weapon_camera_name)
if not weapon_camera:
    print(f"Warning: Camera '{weapon_camera_name}' not found. Weapon camera animations will not be applied.")

# Get the mining axe object
mining_axe = bpy.data.objects.get("mining_axe")

# Get collections for visibility control
gundama_collection = bpy.data.collections.get("Gundama")
weapons_collection = bpy.data.collections.get("Weapons")

# Function to control collection visibility for rendering
def set_collection_visibility(is_weapon_render):
    """
    Controls collection visibility based on render type:
    - Weapon renders: Hide "Gundama" collection, show "Weapons" collection
    - Character renders: Show "Gundama" collection, hide "Weapons" collection
    """
    if gundama_collection:
        gundama_collection.hide_render = is_weapon_render
        print(f"{'Hiding' if is_weapon_render else 'Showing'} Gundama collection for rendering")
    else:
        print("Warning: 'Gundama' collection not found")
    
    if weapons_collection:
        weapons_collection.hide_render = not is_weapon_render
        print(f"{'Showing' if is_weapon_render else 'Hiding'} Weapons collection for rendering")
    else:
        print("Warning: 'Weapons' collection not found")

# Function to set camera animation based on armature action
def set_camera_animation(armature_action_name, is_weapon_animation=False):
    # Select the appropriate camera based on animation type
    camera = weapon_camera if is_weapon_animation else character_camera
    
    if not camera or not camera.animation_data:
        return
    
    # Map specific armature actions to camera actions
    camera_action_map = {
        "01_wield_attack_1_still": "wield_attack_1",
        "02_wield_attack_2": "wield_attack_2",
        "03_wield_attack_3": "wield_attack_3",
        "43_wield_attack_4": "wield_attack_3",
        "44_wield_attack_1_air": "wield_attack_3",
        "45_wield_attack_2_air": "wield_attack_3",
    }
    
    # Get the corresponding camera action or default to t_pose.idle
    camera_action_name = camera_action_map.get(armature_action_name, "t_pose.idle")
    
    # Try to get the camera action
    camera_action = bpy.data.actions.get(camera_action_name)
    if camera_action:
        camera.animation_data.action = camera_action
        print(f"Set {camera.name} animation to: {camera_action_name}")
    else:
        print(f"Warning: Camera action '{camera_action_name}' not found for {camera.name}.")

# Function to render a set of animations
def render_animation_set(animation_set, is_dynamic=False, is_weapon=False, output_dir=None):
    # Set collection visibility based on animation type
    set_collection_visibility(is_weapon)
    
    # Set up camera visibility and active camera based on animation type
    if character_camera and weapon_camera:
        if is_weapon:
            character_camera.hide_render = True
            weapon_camera.hide_render = False
            scene.camera = weapon_camera
            print("Using weapon camera for rendering")
        else:
            character_camera.hide_render = False
            weapon_camera.hide_render = True
            scene.camera = character_camera
            print("Using character camera for rendering")
    
    for animation_name, export_name in animation_set:
        action = bpy.data.actions.get(animation_name)
        if action:
            # Set the active animation for the armature
            armature = bpy.data.objects.get(armature_name)
            if armature:
                if armature.animation_data is None:
                    armature.animation_data_create()
                armature.animation_data.action = action
                
                # Set camera animation based on current armature action
                set_camera_animation(animation_name, is_weapon)
                
                # Update the dependency graph
                bpy.context.view_layer.update()
                
                # Set the first frame of the animation to refresh the state
                scene.frame_set(int(action.frame_range[0]))
                
                # Force additional updates for addons like Auto Trail
                bpy.context.view_layer.update()
                scene.frame_set(scene.frame_current)  # Force frame update for addons
                
                # Pre-process all frames to ensure addon updates (like Auto Trail)
                start_frame = int(action.frame_range[0])
                end_frame = int(action.frame_range[1])
                print(f"Pre-processing frames {start_frame} to {end_frame} for addon updates...")
                
                for frame in range(start_frame, end_frame + 1):
                    scene.frame_set(frame)
                    bpy.context.view_layer.update()
                
                # Return to start frame
                scene.frame_set(start_frame)
                bpy.context.view_layer.update()
                
                # Control the visibility of the mining axe (only for "mining" action)
                if animation_name == "25_mining":
                    if mining_axe:
                        mining_axe.hide_render = False
                        mining_axe.hide_viewport = False
                else:
                    if mining_axe:
                        mining_axe.hide_render = True
                        mining_axe.hide_viewport = True
                
                # Set output path using the appropriate directory
                scene.render.filepath = os.path.join(output_dir, f"{export_name}_")
                
                # Render animation
                bpy.ops.render.render(animation=True)
                
                print(f"Rendered {'weapon ' if is_weapon else ''}{'dynamic ' if is_dynamic else ''}animation: {animation_name} as {export_name} in {output_dir}")
                
                # Reset action for dynamic animations
                if is_dynamic:
                    armature.animation_data.action = None
                    print(f"Action reset after rendering {animation_name}")
        else:
            print(f"Animation not found: {animation_name}")

# Execute the selected pipeline
if render_character_animations:
    print("=== CHARACTER ANIMATIONS PIPELINE ===")
    print("Rendering regular character animations...")
    render_animation_set(character_animations, output_dir=character_output_dir)
    
    print("Rendering dynamic character animations...")
    render_animation_set(dynamic_character_animations, is_dynamic=True, output_dir=character_output_dir)
else:  # render_weapon_animations
    print("=== WEAPON ANIMATIONS PIPELINE ===")
    print("Rendering weapon animations...")
    render_animation_set(weapon_animations, is_weapon=True, output_dir=weapon_animations_output_dir)

print("All animations in the selected pipeline have been rendered!")

# Reset collection visibility - show both collections
if gundama_collection:
    gundama_collection.hide_render = False
if weapons_collection:
    weapons_collection.hide_render = False
print("Collection visibility reset - both collections now visible for rendering")

# Reset armature action at the end
armature = bpy.data.objects.get(armature_name)
if armature and armature.animation_data:
    reset_action = bpy.data.actions.get("RESET")
    if reset_action:
        armature.animation_data.action = reset_action
        print("Armature action set to RESET at the end of the script")
    else:
        armature.animation_data.action = None
        print("RESET action not found, armature action cleared at the end of the script")