extends Node2D

const CG := preload("res://scripts/cg_math.gd")
const ORIGIN := Vector2(60.0, 60.0)
const WALL_THICKNESS := 5.0
const PLAYER_RADIUS := 15.0
const ENEMY_RADIUS := 20.0
const PURSUIT_SECONDS := 3.5
const MELEE_RANGE := 68.0
const PLAYER_MELEE_DAMAGE := 100.0
const LEVEL3_DURATION := 60.0
const MOMMY_RESTART_DELAY := 1.5
const DEVIL_LEVEL_INDEX := 2
const MOMMY_LEVEL_INDEX := 3
const BOSS_MAX_HITS := 3
const BOSS_RENDER_SCALE := 1.5
const LEVEL3_CAMERA_ZOOM := Vector2(1.5, 1.5)
const MIC_ALERT_THRESHOLD := 3.0
const MIC_LEVEL_GAIN := 400.0
const HIDE_LIMIT_SECONDS := 10.0
const GLASS_NOISE_INTENSITY := 100.0
const GLASS_NOISE_RADIUS := 1400.0

# Operative & Combat Parity Constants (imp.md & HunterAssassinUnity)
const PLAYER_MAX_HEALTH := 100.0
const BOLT_DAMAGE := 20.0
const BOLT_COOLDOWN := 0.28
const BOLT_SPEED := 720.0
const BOLT_RADIUS := 7.0
const BOLT_MAX_LIFETIME := 1.4
const FLASHLIGHT_RANGE := 175.0
const FLASHLIGHT_FOV := 1.2217 # 70 degrees
const SPRINT_NOISE_RADIUS := 160.0
const JUMP_HOP_HEIGHT := 12.0
const ENFORCER_SHIELD_ARC_RADIUS := 31.45
const ENFORCER_SHIELD_HALF_ANGLE := 1.1 # ~63 deg each side, 126 deg total arc
const ENFORCER_SHOVE_SPEED := 220.0
const GUARD_PATROL_SPEED := 75.0
const GUARD_CONE_RANGE := 165.0
const GUARD_CONE_FOV := 1.5708 # 90 degrees
const ENFORCER_PATROL_SPEED := 70.0
const ENFORCER_CONE_RANGE := 140.0
const ENFORCER_CONE_FOV := 1.5708 # 90 degrees

var world_size := Vector2.ZERO
var level_index := 0
var level_name := ""
var alarm_seconds := 10.0
var game_state := "menu"
var level3_time_left := LEVEL3_DURATION
var transition_time_left := 0.0
var mommy_restart_time_left := 0.0
var hidden_time := 0.0
var mommy_knows_hidden_spot := false
var mommy_known_hide_position := Vector2.ZERO
var voice_level_percent := 0.0
var microphone_enabled := false
var suspense_alert_active := false
var alarm_active := false
var alarm_timer := 0.0
var extract_ready := false
var level2_unlocked := false
var score := 0
var carried_score := 0
var session_kills := 0
var session_coins := 0
var career_score := 0
var career_coins := 0
var career_kills := 0
var debug_overlay := false
var elapsed := 0.0

var walls: Array[Rect2] = []
var boxes: Array[Rect2] = []
var doors: Array[Dictionary] = []
var exit_rect := Rect2()
var player_position := Vector2.ZERO
var player_health := 100.0
var player_angle := 0.0
var player_facing_left := false
var player_speed := 180.0
var sprint_noise := false
var noise_events: Array[Dictionary] = []
var glass_debris: Array[Dictionary] = []
var footstep_noise_timer := 0.0
var furniture_noise_timer := 0.0
var mic_was_loud := false
var mic_voice_cooldown := 0.0
var player_is_jumping := false
var jump_timer := 0.0
var jump_cooldown := 0.0
var melee_cooldown := 0.0
var player_anim := "idle"
var player_anim_time := 0.0
var player_attack_time := 0.0
var player_dead := false
var player_hidden := false
var hidden_spot_index := -1
var melee_flash := 0.0
var enemies: Array[Dictionary] = []
var hide_spots: Array[Dictionary] = []
var house_furniture: Array[Dictionary] = []
var cameras: Array[Dictionary] = []
var collectibles: Array[Dictionary] = []
var enemy_bullets: Array[Dictionary] = []
var player_bolts: Array[Dictionary] = []
var active_lasers: Array[Dictionary] = []
var fire_cooldown := 0.0
var player_damage_flash := 0.0

var art_frames: Dictionary = {}
var textures: Dictionary = {}
var sound_streams: Dictionary = {}
var audio_players: Array[AudioStreamPlayer] = []
var audio_cursor := 0
var alarm_player: AudioStreamPlayer
var mommy_music_player: AudioStreamPlayer
var mommy_voice_player: AudioStreamPlayer
var mommy_heartbeat_player: AudioStreamPlayer
var suspense_alert_player: AudioStreamPlayer
var microphone_player: AudioStreamPlayer
var microphone_capture: AudioEffectCapture
var mommy_voice_streams: Dictionary = {}
var mommy_voice_stage := -1
var mommy_voice_time_left := 0.0

var ui_layer: CanvasLayer
var menu_overlay: ColorRect
var hud_panel: PanelContainer
var hud_values: Dictionary = {}
var menu_panel: PanelContainer
var menu_stats: Label
var result_panel: PanelContainer
var result_title: Label
var result_summary: Label
var result_next_button: Button
var footer_label: Label
var health_bar: ProgressBar
var alarm_overlay: ColorRect
var alarm_warning: Label
var level3_timer_label: Label
var boss_status_label: Label
var microphone_toggle: CheckButton
var microphone_meter: ProgressBar
var microphone_status_label: Label
var transition_overlay: ColorRect


func _ready() -> void:
	_configure_inputs()
	_load_art()
	_setup_audio()
	_load_career()
	_build_ui()
	_build_level(0)
	_run_math_checks()
	_update_ui()
	queue_redraw()


func _process(delta: float) -> void:
	elapsed += delta
	if game_state == "playing":
		if level_index == MOMMY_LEVEL_INDEX:
			_tick_level3_audio(delta)
			_update_microphone(delta)
		_tick_game(delta)
	elif game_state == "transition":
		transition_time_left = maxf(0.0, transition_time_left - delta)
		if transition_time_left <= 0.0:
			_start_level(MOMMY_LEVEL_INDEX, false)
	elif game_state == "game_over" and level_index == MOMMY_LEVEL_INDEX:
		mommy_restart_time_left = maxf(0.0, mommy_restart_time_left - delta)
		if mommy_restart_time_left <= 0.0:
			_retry_level()
	_update_ui()
	queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if game_state == "playing":
			_toggle_hide_spot(get_global_mouse_position())
			get_viewport().set_input_as_handled()
	elif event.is_action_pressed("interact") and game_state == "playing":
		_interact_with_glass_door()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("debug_overlay"):
		debug_overlay = not debug_overlay
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("restart") and game_state in ["playing", "victory", "game_over"]:
		_retry_level()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("ui_cancel"):
		if game_state == "menu":
			get_tree().quit()
		else:
			_show_menu()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("continue_level") and game_state == "victory" and level_index < 2:
		_continue_level()
		get_viewport().set_input_as_handled()


func _configure_inputs() -> void:
	_add_key_action("move_up", [KEY_W, KEY_UP])
	_add_key_action("move_down", [KEY_S, KEY_DOWN])
	_add_key_action("move_left", [KEY_A, KEY_LEFT])
	_add_key_action("move_right", [KEY_D, KEY_RIGHT])
	_add_key_action("sprint", [KEY_SHIFT])
	_add_key_action("jump", [KEY_CTRL, KEY_J])
	_add_key_action("attack", [KEY_SPACE])
	_add_key_action("interact", [KEY_E])
	_add_key_action("debug_overlay", [KEY_H])
	_add_key_action("restart", [KEY_R])
	_add_key_action("continue_level", [KEY_ENTER, KEY_KP_ENTER])


func _add_key_action(action_name: String, keycodes: Array[int]) -> void:
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)
	for code in keycodes:
		var key_event := InputEventKey.new()
		key_event.physical_keycode = code
		InputMap.action_add_event(action_name, key_event)


func _load_art() -> void:
	var categories := {
		"player": ["Player", ["idle", "walk", "run", "jump", "attack", "death"]],
		"guard": ["Guard", ["idle", "walk", "alert", "death", "shoot"]],
		"enforcer": ["Enforcer", ["idle", "walk", "alert", "death", "shoot"]]
	}
	for kind in categories:
		var category: Array = categories[kind]
		for state in category[1]:
			var frames: Array[Texture2D] = []
			for index in range(12):
				var path := "res://assets/Characters/%s/%s_%d.png" % [category[0], state, index]
				if ResourceLoader.exists(path):
					frames.append(load(path) as Texture2D)
			art_frames["%s/%s" % [kind, state]] = frames

	# Unity Boss character
	var boss_path := "res://assets/Characters/Boss/boss.png"
	if ResourceLoader.exists(boss_path):
		var boss_tex: Texture2D = load(boss_path) as Texture2D
		art_frames["boss/idle"] = [boss_tex]
		art_frames["boss/walk"] = [boss_tex]
		art_frames["boss/alert"] = [boss_tex]
		art_frames["boss/attack"] = [boss_tex]
		art_frames["boss/death"] = [boss_tex]

	# Nightmare stage (Mommy)
	_load_wraith_frames()
	if not art_frames.has("mommy/idle"):
		var mommy_path := "res://assets/Characters/Mommy_cutout.png"
		if not ResourceLoader.exists(mommy_path):
			mommy_path = "res://assets/Characters/Mommy.png"
		if ResourceLoader.exists(mommy_path):
			var mommy_tex: Texture2D = load(mommy_path) as Texture2D
			art_frames["mommy/idle"] = [mommy_tex]
			art_frames["mommy/walk"] = [mommy_tex]
			art_frames["mommy/attack"] = [mommy_tex]
			art_frames["mommy/death"] = [mommy_tex]
	for path in [
		"Environment/security_camera.png",
		"Environment/crate_0.png",
		"Environment/crate_1.png",
		"Environment/crate_unique_0.png",
		"Environment/crate_unique_1.png",
		"Environment/crate_unique_2.png",
		"Environment/crate_unique_3.png",
		"Environment/crate_unique_4.png",
		"Environment/crate_unique_5.png",
		"Environment/barrel.png",
		"Environment/plant.png",
		"Environment/console.png",
		"Environment/wall_light.png",
		"Environment/door_post.png",
		"Items/medkit.png",
		"Tiles/floor.png",
		"Tiles/floor_surface_full.png",
		"Tiles/wall.png",
		"Tiles/hazard.png",
		"Tiles/door.png",
		"Tiles/door_stripe.png",
		"Environment/exit_pad.png",
		"FX/glow.png",
		"FX/shadow_blob.png"
	]:
		var resource_path := "res://assets/%s" % path
		if ResourceLoader.exists(resource_path):
			textures[path] = load(resource_path) as Texture2D
	var shield_path := "res://assets/Characters/dragonbones/library/Shield.png"
	if ResourceLoader.exists(shield_path):
		textures["Characters/Shield.png"] = load(shield_path) as Texture2D
	for index in range(6):
		var coin_path := "Items/coin_%d.png" % index
		var resource_path := "res://assets/%s" % coin_path
		if ResourceLoader.exists(resource_path):
			textures[coin_path] = load(resource_path) as Texture2D


func _setup_audio() -> void:
	for index in range(8):
		var player := AudioStreamPlayer.new()
		player.volume_db = -10.0
		add_child(player)
		audio_players.append(player)
	alarm_player = AudioStreamPlayer.new()
	alarm_player.volume_db = -9.0
	add_child(alarm_player)
	mommy_music_player = AudioStreamPlayer.new()
	mommy_music_player.volume_db = -25.0
	add_child(mommy_music_player)
	mommy_voice_player = AudioStreamPlayer.new()
	mommy_voice_player.volume_db = -8.0
	add_child(mommy_voice_player)
	mommy_heartbeat_player = AudioStreamPlayer.new()
	mommy_heartbeat_player.volume_db = -12.0
	add_child(mommy_heartbeat_player)
	suspense_alert_player = AudioStreamPlayer.new()
	suspense_alert_player.volume_db = -10.0
	add_child(suspense_alert_player)
	var suspense_path := "res://assets/audio for mom/alexis_gaming_cam-the-suspenseful-braam-334309.mp3"
	if ResourceLoader.exists(suspense_path):
		suspense_alert_player.stream = load(suspense_path) as AudioStream
	else:
		push_warning("Missing supplied suspense track: %s" % suspense_path)
	microphone_player = AudioStreamPlayer.new()
	microphone_player.bus = "Master"
	add_child(microphone_player)
	var voice_paths := {
		"sweet": "sweet_trimmed.wav",
		"irritated": "little_angry_trimmed.wav",
		"angry": "angry_trimmed.wav"
	}
	for voice_variant in voice_paths:
		var voice := String(voice_variant)
		var voice_path := "res://assets/audio for mom/processed/%s" % String(voice_paths[voice])
		if ResourceLoader.exists(voice_path):
			mommy_voice_streams[voice] = load(voice_path) as AudioStream
		else:
			push_warning("Missing Mommy voice clip: %s" % voice_path)
	sound_streams["coin"] = _make_tone(988.0, 1319.0, 0.16)
	sound_streams["heal"] = _make_tone(523.0, 659.0, 0.22)
	sound_streams["impact"] = _make_tone(105.0, 70.0, 0.20, true)
	sound_streams["door"] = _make_tone(170.0, 85.0, 0.30, true)
	sound_streams["glass_shatter"] = _make_tone(2250.0, 180.0, 0.62, true)
	sound_streams["glass_crunch"] = _make_tone(1250.0, 420.0, 0.28, true)
	sound_streams["shield"] = _make_tone(1760.0, 1175.0, 0.10)
	sound_streams["victory"] = _make_tone(523.0, 1047.0, 0.72)
	sound_streams["failure"] = _make_tone(220.0, 55.0, 0.80, true)
	sound_streams["laser"] = _make_tone(1400.0, 350.0, 0.18, true)
	sound_streams["jump"] = _make_tone(140.0, 80.0, 0.14, true)
	var alarm_stream := _make_tone(390.0, 780.0, 0.72, false, true)
	alarm_stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	alarm_stream.loop_end = int(alarm_stream.data.size() / 2)
	sound_streams["alarm"] = alarm_stream



func _load_wraith_frames() -> void:
	var animations := {
		"idle": ["Idle", "Wraith_03_Idle", 12],
		"walk": ["Walking", "Wraith_03_Moving Forward", 12],
		"attack": ["Attacking", "Wraith_03_Attack", 12],
		"hurt": ["Hurt", "Wraith_03_Hurt", 12]
	}
	for state in animations:
		var animation: Array = animations[state]
		var frames: Array[Texture2D] = []
		var directory := "res://assets/Characters/Wraith_03/PNG Sequences/%s" % animation[0]
		for index in range(int(animation[2])):
			var path := "%s/%s_%03d.png" % [directory, animation[1], index]
			if ResourceLoader.exists(path):
				frames.append(load(path) as Texture2D)
		if not frames.is_empty():
			art_frames["mommy/%s" % state] = frames

func _make_heartbeat_stream() -> AudioStreamWAV:
	const SAMPLE_RATE := 22050
	const DURATION := 1.15
	var sample_count := int(SAMPLE_RATE * DURATION)
	var data := PackedByteArray()
	data.resize(sample_count * 2)
	for index in range(sample_count):
		var t := float(index) / SAMPLE_RATE
		var beat_a := maxf(0.0, sin(TAU * 48.0 * t)) * exp(-maxf(0.0, t) * 18.0)
		var second_t := t - 0.2
		var beat_b := (
			maxf(0.0, sin(TAU * 43.0 * second_t)) * exp(-maxf(0.0, second_t) * 22.0)
			if second_t >= 0.0
			else 0.0
		)
		var packed := int(clampf((beat_a + beat_b) * 0.72, -1.0, 1.0) * 24000.0)
		data[index * 2] = packed & 0xff
		data[index * 2 + 1] = (packed >> 8) & 0xff
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = SAMPLE_RATE
	stream.stereo = false
	stream.data = data
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	stream.loop_end = sample_count
	return stream


func _start_level3_audio() -> void:
	mommy_voice_stage = -1
	mommy_voice_time_left = 0.0
	mommy_music_player.stream = suspense_alert_player.stream
	if mommy_music_player.stream != null:
		mommy_music_player.play()
	mommy_heartbeat_player.stream = _make_heartbeat_stream()
	_tick_level3_audio(0.0)
	_set_microphone_enabled(true)


func _tick_level3_audio(delta: float) -> void:
	if not mommy_music_player.playing and mommy_music_player.stream != null:
		mommy_music_player.play()
	mommy_voice_time_left = maxf(0.0, mommy_voice_time_left - delta)
	if mommy_voice_time_left == 0.0 and mommy_voice_player.playing:
		mommy_voice_player.stop()
	var desired_stage := 0 if level3_time_left > 40.0 else (1 if level3_time_left > 20.0 else 2)
	if desired_stage != mommy_voice_stage:
		mommy_voice_stage = desired_stage
		var voice_name: String = ["sweet", "irritated", "angry"][desired_stage]
		var voice := mommy_voice_streams.get(voice_name) as AudioStream
		if voice == null:
			push_warning("Mommy voice clip is unavailable: %s" % voice_name)
		else:
			mommy_voice_player.stop()
			mommy_voice_player.stream = voice
			mommy_voice_player.play()
			mommy_voice_time_left = voice.get_length()
	if level3_time_left <= 10.0 and level3_time_left > 0.0:
		if not mommy_heartbeat_player.playing:
			mommy_heartbeat_player.play()
	elif mommy_heartbeat_player.playing:
		mommy_heartbeat_player.stop()


func _stop_level3_audio() -> void:
	mommy_music_player.stop()
	mommy_voice_player.stop()
	mommy_heartbeat_player.stop()
	suspense_alert_player.stop()
	mommy_voice_time_left = 0.0
	suspense_alert_active = false
	_set_microphone_enabled(false)


func _set_microphone_enabled(enabled: bool) -> void:
	if enabled == microphone_enabled:
		if is_instance_valid(microphone_toggle):
			microphone_toggle.set_pressed_no_signal(enabled)
		return
	if not enabled:
		microphone_enabled = false
		voice_level_percent = 0.0
		suspense_alert_active = false
		mic_was_loud = false
		mic_voice_cooldown = 0.0
		if is_instance_valid(suspense_alert_player):
			suspense_alert_player.stop()
		if is_instance_valid(microphone_player):
			microphone_player.stop()
		var bus_index := AudioServer.get_bus_index("MicrophoneCapture")
		if bus_index >= 0 and microphone_capture != null:
			for effect_index in range(AudioServer.get_bus_effect_count(bus_index)):
				if AudioServer.get_bus_effect(bus_index, effect_index) == microphone_capture:
					AudioServer.remove_bus_effect(bus_index, effect_index)
					break
			microphone_capture = null
		if is_instance_valid(microphone_toggle):
			microphone_toggle.set_pressed_no_signal(false)
		return
	if AudioServer.get_input_device_list().is_empty():
		push_warning("Microphone monitoring is unavailable: no input device was found.")
		if is_instance_valid(microphone_toggle):
			microphone_toggle.set_pressed_no_signal(false)
		return
	var bus_index := AudioServer.get_bus_index("MicrophoneCapture")
	if bus_index < 0:
		bus_index = AudioServer.bus_count
		AudioServer.add_bus(bus_index)
		AudioServer.set_bus_name(bus_index, "MicrophoneCapture")
		AudioServer.set_bus_send(bus_index, "Master")
		AudioServer.set_bus_volume_db(bus_index, -80.0)
	else:
		for effect_index in range(AudioServer.get_bus_effect_count(bus_index) - 1, -1, -1):
			AudioServer.remove_bus_effect(bus_index, effect_index)
	microphone_capture = AudioEffectCapture.new()
	microphone_capture.buffer_length = 0.5
	AudioServer.add_bus_effect(bus_index, microphone_capture)
	microphone_player.bus = "MicrophoneCapture"
	microphone_player.stream = AudioStreamMicrophone.new()
	microphone_player.play()
	microphone_enabled = true
	if is_instance_valid(microphone_toggle):
		microphone_toggle.set_pressed_no_signal(true)


func _update_microphone(delta: float = 0.016) -> void:
	if not microphone_enabled or microphone_capture == null:
		voice_level_percent = 0.0
		_update_voice_detection(delta)
		return
	var frame_count := microphone_capture.get_frames_available()
	if frame_count <= 0:
		voice_level_percent = maxf(0.0, voice_level_percent - delta * 12.0)
		_update_voice_detection(delta)
		return
	var samples := microphone_capture.get_buffer(frame_count)
	var raw_level := _measure_voice_level(samples)
	var peak := 0.0
	for sample in samples:
		peak = maxf(peak, maxf(absf(sample.x), absf(sample.y)))
	var measured_level := clampf(maxf(raw_level * 3.5, peak * MIC_LEVEL_GAIN * 1.5), 0.0, 100.0)
	if measured_level > voice_level_percent:
		voice_level_percent = measured_level
	else:
		voice_level_percent = maxf(measured_level, voice_level_percent - delta * 15.0)
	_update_voice_detection(delta)


func _measure_voice_level(samples: PackedVector2Array) -> float:
	if samples.is_empty():
		return 0.0
	var squared_total := 0.0
	for sample in samples:
		squared_total += sample.length_squared() * 0.5
	return clampf(sqrt(squared_total / float(samples.size())) * MIC_LEVEL_GAIN, 0.0, 100.0)


func _update_voice_detection(delta: float = 0.016) -> void:
	var is_loud := voice_level_percent >= MIC_ALERT_THRESHOLD
	suspense_alert_active = is_loud
	if is_instance_valid(suspense_alert_player):
		if is_loud and not suspense_alert_player.playing and suspense_alert_player.stream != null:
			suspense_alert_player.play()
		elif not is_loud and suspense_alert_player.playing:
			suspense_alert_player.stop()
	mic_voice_cooldown = maxf(0.0, mic_voice_cooldown - delta)
	if not is_loud:
		mic_was_loud = false
		mic_voice_cooldown = 0.0
		return
	if not mic_was_loud or mic_voice_cooldown <= 0.0:
		_emit_noise("MICROPHONE", player_position, voice_level_percent, GLASS_NOISE_RADIUS)
		mic_voice_cooldown = 0.35
	mic_was_loud = true


func _make_tone(
	start_frequency: float,
	end_frequency: float,
	duration: float,
	rough: bool = false,
	sustain: bool = false
) -> AudioStreamWAV:
	const SAMPLE_RATE := 22050
	var sample_count := int(SAMPLE_RATE * duration)
	var data := PackedByteArray()
	data.resize(sample_count * 2)
	for index in range(sample_count):
		var t := float(index) / SAMPLE_RATE
		var progress := float(index) / maxf(1.0, float(sample_count - 1))
		var frequency := lerpf(start_frequency, end_frequency, progress * progress)
		var envelope := 1.0 if sustain else exp(-t * 10.0)
		var sample := sin(TAU * frequency * t) * envelope
		if rough:
			sample = (
				(0.72 * sample + 0.28 * sin(TAU * frequency * 0.47 * t)) * (1.0 - progress * 0.55)
			)
		var packed := int(clampf(sample, -1.0, 1.0) * 25000.0)
		data[index * 2] = packed & 0xff
		data[index * 2 + 1] = (packed >> 8) & 0xff
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = SAMPLE_RATE
	stream.stereo = false
	stream.data = data
	return stream


func _play_sfx(name: String) -> void:
	if not sound_streams.has(name) or audio_players.is_empty():
		return
	var player := audio_players[audio_cursor]
	audio_cursor = (audio_cursor + 1) % audio_players.size()
	player.stream = sound_streams[name]
	player.play()


func _build_level(index: int) -> void:
	level_index = clampi(index, 0, MOMMY_LEVEL_INDEX)
	if level_index == DEVIL_LEVEL_INDEX:
		_build_level(1)
		level_index = DEVIL_LEVEL_INDEX
		walls.resize(4)
		level_name = "The Final Hunt"
		alarm_seconds = 45.0
		exit_rect = Rect2()
		enemies.resize(3)
		var boss_position := _random_walkable_position(28.0, player_position, 180.0)
		enemies.append(
			{
				"name": "Boss",
				"mommy": false,
				"boss": true,
				"shielded": false,
				"speed": 92.0,
				"pos": boss_position,
				"path": [],
				"waypoint": 0,
				"direction": 1,
				"angle": randf_range(-PI, PI),
				"health": float(BOSS_MAX_HITS),
				"hp": 300.0,
				"boss_phase": 1,
				"windup": 0.64,
				"telegraph_timer": 0.0,
				"is_slam": false,
				"alive": true,
				"alert": false,
				"investigate": 0.0,
				"investigate_point": boss_position,
				"attack_timer": 0.0,
				"shot_timer": 0.0,
				"pursuit_timer": 0.0,
				"mom_was_seen": false,
				"mom_searching": false,
				"mom_waiting": false,
				"mom_search_timer": 0.0,
				"last_seen": boss_position,
				"shield_timer": 0.0,
				"flash": 0.0,
				"anim": "run",
				"anim_time": 0.0,
				"boss_relocate_timer": 0.0,
				"boss_hit_cooldown": 0.0,
				"boss_run_timer": 1.5,
				"boss_roam_target": _random_walkable_position(28.0, boss_position, 180.0),
				"boss_stuck_timer": 0.0,
				"boss_last_position": boss_position,
				"boss_relocating": false
			}
		)
		var camera := get_node_or_null("Camera2D") as Camera2D
		if camera != null:
			camera.zoom = LEVEL3_CAMERA_ZOOM
		_update_camera(true)
		return
	var columns := 3
	var rows := 2
	var passage := 100.0
	var box_size := 120.0
	var spawns: Array = []
	var extra_walls: Array = []
	var door_specs: Array = []
	var camera_mounts: Array = []
	var enemy_specs: Array = []
	var item_specs: Array = []
	var furniture_specs: Array[Dictionary] = []
	var house_hide_specs: Array[Dictionary] = []
	var exit_min := Vector2.ZERO
	var exit_max := Vector2.ZERO
	if level_index == 0:
		level_name = "Facility Infiltration"
		alarm_seconds = 10.0
		spawns.append(Vector2(50, 50))
		var col_x_l1 := [105.0, 325.0, 545.0]
		var row_y_l1 := [105.0, 325.0]
		door_specs = [
			{
				"a": Vector2(col_x_l1[0] + box_size, row_y_l1[0] + box_size * 0.5),
				"b": Vector2(col_x_l1[1], row_y_l1[0] + box_size * 0.5),
				"color": Color(0.0, 0.9, 1.0),
				"trigger": 75.0
			},
			{
				"a": Vector2(col_x_l1[1] + box_size, row_y_l1[1] + box_size * 0.5),
				"b": Vector2(col_x_l1[2], row_y_l1[1] + box_size * 0.5),
				"color": Color(1.0, 0.57, 0.0),
				"trigger": 75.0
			},
			{
				"a": Vector2(col_x_l1[1] + box_size * 0.5, row_y_l1[0] + box_size),
				"b": Vector2(col_x_l1[1] + box_size * 0.5, row_y_l1[1]),
				"color": Color(0.66, 0.33, 0.97),
				"trigger": 75.0
			}
		]
		exit_min = Vector2(770.0 - WALL_THICKNESS - passage + 12.0, 550.0 - WALL_THICKNESS - 36.0)
		exit_max = Vector2(770.0 - WALL_THICKNESS - 12.0, 550.0 - WALL_THICKNESS)
		camera_mounts = [{"position": Vector2(770.0 - 18.0, 18.0), "angle": 2.45}]
		var patrol_bottom := WALL_THICKNESS + passage + box_size + passage + box_size + 50.0
		var patrol_middle := WALL_THICKNESS + passage + box_size + 50.0
		enemy_specs.append(
			{
				"name": "Guard",
				"shielded": false,
				"speed": 80.0,
				"path": [Vector2(160, patrol_bottom), Vector2(610, patrol_bottom)]
			}
		)
		enemy_specs.append(
			{
				"name": "Enforcer",
				"shielded": true,
				"speed": 70.0,
				"path": [Vector2(220, patrol_middle), Vector2(550, patrol_middle)]
			}
		)
		for pos in [
			Vector2(160, 80),
			Vector2(380, 80),
			Vector2(600, 80),
			Vector2(160, 320),
			Vector2(600, 320),
			Vector2(270, 470),
			Vector2(490, 470)
		]:
			item_specs.append({"pos": pos, "medkit": false, "value": 100.0})
		for pos in [Vector2(80, 260), Vector2(690, 260), Vector2(385, 260)]:
			item_specs.append({"pos": pos, "medkit": true, "value": 35.0})
	elif level_index == 1:
		columns = 4
		rows = 3
		passage = 88.0
		box_size = 110.0
		level_name = "Deep Vault Sweep"
		alarm_seconds = 12.0
		spawns.append(Vector2(44, 44))
		var col_x_l2: Array[float] = []
		var row_y_l2: Array[float] = []
		for column in range(columns):
			col_x_l2.append(WALL_THICKNESS + passage + column * (box_size + passage))
		for row in range(rows):
			row_y_l2.append(WALL_THICKNESS + passage + row * (box_size + passage))
		extra_walls = [
			Rect2(
				Vector2(col_x_l2[0] + box_size * 0.25, row_y_l2[0] - passage * 0.35),
				Vector2(box_size * 0.5, WALL_THICKNESS)
			),
			Rect2(
				Vector2(col_x_l2[2] - passage * 0.4, row_y_l2[1] + box_size * 0.15),
				Vector2(WALL_THICKNESS, box_size * 0.7)
			),
			Rect2(
				Vector2(
					WALL_THICKNESS + passage * 0.15,
					row_y_l2[2] + box_size * 0.5 - WALL_THICKNESS * 0.5
				),
				Vector2(passage * 0.4, WALL_THICKNESS)
			),
			Rect2(
				Vector2(col_x_l2[3] + box_size * 0.1, row_y_l2[0] - passage * 0.45),
				Vector2(box_size * 0.8, WALL_THICKNESS)
			)
		]
		door_specs = [
			{
				"a": Vector2(col_x_l2[0] + box_size, row_y_l2[0] + box_size * 0.5),
				"b": Vector2(col_x_l2[1], row_y_l2[0] + box_size * 0.5),
				"color": Color(0.0, 0.9, 1.0),
				"trigger": 70.0
			},
			{
				"a": Vector2(col_x_l2[1] + box_size, row_y_l2[1] + box_size * 0.5),
				"b": Vector2(col_x_l2[2], row_y_l2[1] + box_size * 0.5),
				"color": Color(1.0, 0.57, 0.0),
				"trigger": 70.0
			},
			{
				"a": Vector2(col_x_l2[2] + box_size, row_y_l2[2] + box_size * 0.5),
				"b": Vector2(col_x_l2[3], row_y_l2[2] + box_size * 0.5),
				"color": Color(0.66, 0.33, 0.97),
				"trigger": 70.0
			},
			{
				"a": Vector2(col_x_l2[1] + box_size * 0.5, row_y_l2[0] + box_size),
				"b": Vector2(col_x_l2[1] + box_size * 0.5, row_y_l2[1]),
				"color": Color(0.2, 1.0, 0.45),
				"trigger": 65.0
			},
			{
				"a": Vector2(col_x_l2[3] + box_size * 0.5, row_y_l2[1] + box_size),
				"b": Vector2(col_x_l2[3] + box_size * 0.5, row_y_l2[2]),
				"color": Color(1.0, 0.3, 0.45),
				"trigger": 65.0
			}
		]
		var room_width := 2.0 * WALL_THICKNESS + 5.0 * passage + 4.0 * box_size
		var room_height := 2.0 * WALL_THICKNESS + 4.0 * passage + 3.0 * box_size
		exit_min = Vector2(
			room_width - WALL_THICKNESS - passage + 10.0, room_height - WALL_THICKNESS - 40.0
		)
		exit_max = Vector2(room_width - WALL_THICKNESS - 10.0, room_height - WALL_THICKNESS)
		camera_mounts = [
			{"position": Vector2(room_width - 18, 18), "angle": 2.45},
			{"position": Vector2(18, room_height - 18), "angle": -0.75}
		]
		var lanes_x: Array[float] = []
		var lanes_y: Array[float] = []
		for lane in range(5):
			lanes_x.append(WALL_THICKNESS + passage * 0.5 + lane * (box_size + passage))
		for lane in range(4):
			lanes_y.append(WALL_THICKNESS + passage * 0.5 + lane * (box_size + passage))
		enemy_specs = [
			{
				"name": "Guard South",
				"shielded": false,
				"speed": 78.0,
				"path":
				[
					Vector2(lanes_x[0], lanes_y[0]),
					Vector2(lanes_x[2], lanes_y[0]),
					Vector2(lanes_x[2], lanes_y[1])
				]
			},
			{
				"name": "Guard Mid",
				"shielded": false,
				"speed": 82.0,
				"path":
				[
					Vector2(lanes_x[4], lanes_y[1]),
					Vector2(lanes_x[1], lanes_y[1]),
					Vector2(lanes_x[1], lanes_y[2])
				]
			},
			{
				"name": "Guard North",
				"shielded": false,
				"speed": 76.0,
				"path":
				[
					Vector2(lanes_x[0], lanes_y[3]),
					Vector2(lanes_x[3], lanes_y[3]),
					Vector2(lanes_x[3], lanes_y[2])
				]
			},
			{
				"name": "Guard East",
				"shielded": false,
				"speed": 80.0,
				"path":
				[
					Vector2(lanes_x[4], lanes_y[0]),
					Vector2(lanes_x[4], lanes_y[2]),
					Vector2(lanes_x[2], lanes_y[2])
				]
			},
			{
				"name": "Enforcer",
				"shielded": true,
				"speed": 62.0,
				"path":
				[
					Vector2(lanes_x[2], lanes_y[1]),
					Vector2(lanes_x[3], lanes_y[1]),
					Vector2(lanes_x[3], lanes_y[2])
				]
			}
		]
		for pos in [
			Vector2(lanes_x[0] + 16, lanes_y[0]),
			Vector2(lanes_x[2], lanes_y[0]),
			Vector2(lanes_x[4] - 16, lanes_y[0]),
			Vector2(lanes_x[1], lanes_y[1]),
			Vector2(lanes_x[3], lanes_y[1]),
			Vector2(lanes_x[0] + 12, lanes_y[2]),
			Vector2(lanes_x[2], lanes_y[2]),
			Vector2(lanes_x[4] - 12, lanes_y[2]),
			Vector2(lanes_x[1], lanes_y[3]),
			Vector2(lanes_x[3], lanes_y[3])
		]:
			item_specs.append({"pos": pos, "medkit": false, "value": 100.0})
		for pos in [
			Vector2(lanes_x[0], lanes_y[1]),
			Vector2(lanes_x[2], lanes_y[1]),
			Vector2(lanes_x[4], lanes_y[3] - 12),
			Vector2(lanes_x[3], lanes_y[0])
		]:
			item_specs.append({"pos": pos, "medkit": true, "value": 35.0})

	else:
		columns = 0
		rows = 0
		passage = 0.0
		box_size = 0.0
		level_name = "The House: Mother's Nightmare"
		alarm_seconds = 0.0
		spawns.append(Vector2(530.0, 480.0))
		extra_walls = [
			Rect2(Vector2(408, 0), Vector2(10, 45)),
			Rect2(Vector2(408, 105), Vector2(10, 55)),
			Rect2(Vector2(408, 160), Vector2(10, 60)),
			Rect2(Vector2(408, 280), Vector2(10, 160)),
			Rect2(Vector2(408, 510), Vector2(10, 190)),
			Rect2(Vector2(638, 0), Vector2(10, 45)),
			Rect2(Vector2(638, 105), Vector2(10, 60)),
			Rect2(Vector2(638, 235), Vector2(10, 190)),
			Rect2(Vector2(638, 495), Vector2(10, 205)),
			Rect2(Vector2(0, 118), Vector2(135, 10)),
			Rect2(Vector2(195, 0), Vector2(10, 35)),
			Rect2(Vector2(195, 95), Vector2(10, 23)),
			Rect2(Vector2(195, 128), Vector2(10, 32)),
			Rect2(Vector2(195, 220), Vector2(10, 50)),
			Rect2(Vector2(195, 118), Vector2(105, 10)),
			Rect2(Vector2(360, 118), Vector2(50, 10)),
			Rect2(Vector2(0, 268), Vector2(140, 10)),
			Rect2(Vector2(205, 268), Vector2(80, 10)),
			Rect2(Vector2(350, 268), Vector2(60, 10)),
			Rect2(Vector2(408, 118), Vector2(80, 10)),
			Rect2(Vector2(570, 118), Vector2(70, 10)),
			Rect2(Vector2(648, 148), Vector2(132, 10)),
			Rect2(Vector2(850, 148), Vector2(150, 10)),
			Rect2(Vector2(648, 268), Vector2(48, 10)),
			Rect2(Vector2(766, 268), Vector2(234, 10))
		]
		door_specs = [
			{
				"a": Vector2(408, 45),
				"b": Vector2(408, 105),
				"color": Color("#caa77a"),
				"trigger": 48.0,
				"room_a": 1,
				"room_b": 4
			},
			{
				"a": Vector2(195, 160),
				"b": Vector2(195, 220),
				"color": Color("#caa77a"),
				"trigger": 48.0,
				"room_a": 2,
				"room_b": 3
			},
			{
				"a": Vector2(408, 220),
				"b": Vector2(408, 280),
				"color": Color("#caa77a"),
				"trigger": 48.0,
				"room_a": 3,
				"room_b": 8
			},
			{
				"a": Vector2(408, 440),
				"b": Vector2(408, 510),
				"color": Color("#caa77a"),
				"trigger": 52.0,
				"room_a": 7,
				"room_b": 8
			},
			{
				"a": Vector2(140, 268),
				"b": Vector2(205, 268),
				"color": Color("#caa77a"),
				"trigger": 48.0,
				"room_a": 2,
				"room_b": 7
			},
			{
				"a": Vector2(285, 268),
				"b": Vector2(350, 268),
				"color": Color("#caa77a"),
				"trigger": 48.0,
				"room_a": 3,
				"room_b": 7
			},
			{
				"a": Vector2(195, 35),
				"b": Vector2(195, 95),
				"color": Color("#caa77a"),
				"trigger": 48.0,
				"room_a": 0,
				"room_b": 1
			},
			{
				"a": Vector2(135, 118),
				"b": Vector2(195, 118),
				"color": Color("#caa77a"),
				"trigger": 48.0,
				"room_a": 0,
				"room_b": 2
			},
			{
				"a": Vector2(300, 118),
				"b": Vector2(360, 118),
				"color": Color("#caa77a"),
				"trigger": 48.0,
				"room_a": 1,
				"room_b": 3
			},
			{
				"a": Vector2(488, 118),
				"b": Vector2(570, 118),
				"color": Color("#8adfff"),
				"trigger": 48.0,
				"glass": true,
				"room_a": 4,
				"room_b": 8
			},
			{
				"a": Vector2(638, 45),
				"b": Vector2(638, 105),
				"color": Color("#8adfff"),
				"trigger": 48.0,
				"glass": true,
				"room_a": 4,
				"room_b": 5
			},
			{
				"a": Vector2(638, 165),
				"b": Vector2(638, 235),
				"color": Color("#8adfff"),
				"trigger": 48.0,
				"glass": true,
				"room_a": 6,
				"room_b": 8
			},
			{
				"a": Vector2(638, 425),
				"b": Vector2(638, 495),
				"color": Color("#8adfff"),
				"trigger": 48.0,
				"glass": true,
				"room_a": 9,
				"room_b": 8
			},
			{
				"a": Vector2(780, 148),
				"b": Vector2(850, 148),
				"color": Color("#8adfff"),
				"trigger": 48.0,
				"glass": true,
				"room_a": 5,
				"room_b": 6
			},
			{
				"a": Vector2(696, 268),
				"b": Vector2(766, 268),
				"color": Color("#8adfff"),
				"trigger": 48.0,
				"glass": true,
				"room_a": 6,
				"room_b": 9
			},
			{
				"a": Vector2(455, 695),
				"b": Vector2(545, 695),
				"color": Color("#8adfff"),
				"trigger": 52.0,
				"glass": true,
				"room_a": 8,
				"room_b": 8
			}
		]
		furniture_specs = [
			{"name": "BED", "rect": Rect2(Vector2(38, 28), Vector2(105, 78))},
			{"name": "BED", "rect": Rect2(Vector2(270, 28), Vector2(105, 78))},
			{"name": "BED", "rect": Rect2(Vector2(28, 160), Vector2(110, 85))},
			{"name": "BED", "rect": Rect2(Vector2(270, 160), Vector2(110, 85))},
			{"name": "DESK", "rect": Rect2(Vector2(145, 35), Vector2(42, 32))},
			{"name": "DESK", "rect": Rect2(Vector2(213, 180), Vector2(42, 34))},
			{"name": "WARDROBE", "rect": Rect2(Vector2(8, 35), Vector2(42, 72))},
			{"name": "WARDROBE", "rect": Rect2(Vector2(215, 35), Vector2(42, 72))},
			{"name": "WARDROBE", "rect": Rect2(Vector2(150, 174), Vector2(42, 76))},
			{"name": "WARDROBE", "rect": Rect2(Vector2(215, 174), Vector2(42, 76))},
			{"name": "CLUTTER", "rect": Rect2(Vector2(435, 26), Vector2(170, 78))},
			{"name": "TUB", "rect": Rect2(Vector2(682, 28), Vector2(130, 60))},
			{"name": "TOILET", "rect": Rect2(Vector2(835, 26), Vector2(48, 60))},
			{"name": "SINK", "rect": Rect2(Vector2(910, 92), Vector2(55, 42))},
			{"name": "WASHING MACHINE", "rect": Rect2(Vector2(875, 176), Vector2(65, 62))},
			{"name": "SINK", "rect": Rect2(Vector2(730, 181), Vector2(55, 42))},
			{"name": "FIREPLACE", "rect": Rect2(Vector2(140, 296), Vector2(155, 40))},
			{"name": "CLOCK", "rect": Rect2(Vector2(346, 310), Vector2(32, 46))},
			{"name": "SOFA", "rect": Rect2(Vector2(100, 570), Vector2(185, 62))},
			{"name": "FRIDGE", "rect": Rect2(Vector2(910, 360), Vector2(62, 116))},
			{"name": "DINING TABLE", "rect": Rect2(Vector2(730, 430), Vector2(112, 66))},
			{"name": "COUNTER", "rect": Rect2(Vector2(670, 300), Vector2(225, 40))},
			{"name": "COUNTER", "rect": Rect2(Vector2(670, 540), Vector2(225, 40))}
		]
		house_hide_specs = [
			{"pos": Vector2(40, 70), "label": "WARDROBE"},
			{"pos": Vector2(236, 70), "label": "WARDROBE"},
			{"pos": Vector2(171, 210), "label": "WARDROBE"},
			{"pos": Vector2(236, 210), "label": "WARDROBE"},
			{"pos": Vector2(908, 207), "label": "LAUNDRY"},
			{"pos": Vector2(940, 410), "label": "FRIDGE"},
			{"pos": Vector2(100, 602), "label": "SOFA"}
		]
		enemy_specs = [
			{
				"name": "Mommy",
				"mommy": true,
				"shielded": false,
				"speed": 145.0,
				"path": [Vector2(200, 500)]
			}
		]

	var width := (
		1000.0
		if level_index >= DEVIL_LEVEL_INDEX
		else 2.0 * WALL_THICKNESS + float(columns + 1) * passage + float(columns) * box_size
	)
	var height := (
		700.0
		if level_index >= DEVIL_LEVEL_INDEX
		else 2.0 * WALL_THICKNESS + float(rows + 1) * passage + float(rows) * box_size
	)
	world_size = Vector2(width, height)
	walls.clear()
	boxes.clear()
	house_furniture.clear()
	doors.clear()
	enemies.clear()
	cameras.clear()
	collectibles.clear()
	enemy_bullets.clear()
	player_bolts.clear()
	active_lasers.clear()
	fire_cooldown = 0.0
	player_damage_flash = 0.0
	noise_events.clear()
	glass_debris.clear()
	footstep_noise_timer = 0.0
	furniture_noise_timer = 0.0
	mic_was_loud = false
	mic_voice_cooldown = 0.0
	walls.append(Rect2(ORIGIN, Vector2(width, WALL_THICKNESS)))
	if level_index == MOMMY_LEVEL_INDEX:
		walls.append(
			Rect2(ORIGIN + Vector2(0, height - WALL_THICKNESS), Vector2(455, WALL_THICKNESS))
		)
		walls.append(
			Rect2(
				ORIGIN + Vector2(545, height - WALL_THICKNESS), Vector2(width - 545, WALL_THICKNESS)
			)
		)
	else:
		walls.append(
			Rect2(ORIGIN + Vector2(0, height - WALL_THICKNESS), Vector2(width, WALL_THICKNESS))
		)
	walls.append(Rect2(ORIGIN, Vector2(WALL_THICKNESS, height)))
	walls.append(
		Rect2(ORIGIN + Vector2(width - WALL_THICKNESS, 0), Vector2(WALL_THICKNESS, height))
	)
	for rect in extra_walls:
		walls.append(Rect2(ORIGIN + rect.position, rect.size))
	if level_index == MOMMY_LEVEL_INDEX:
		for furniture in furniture_specs:
			var furniture_rect: Rect2 = furniture.rect
			var world_rect := Rect2(ORIGIN + furniture_rect.position, furniture_rect.size)
			house_furniture.append({"name": furniture.name, "rect": world_rect})
	else:
		for column in range(columns):
			for row in range(rows):
				var position := (
					ORIGIN
					+ Vector2(
						WALL_THICKNESS + passage + column * (box_size + passage),
						WALL_THICKNESS + passage + row * (box_size + passage)
					)
				)
				boxes.append(Rect2(position, Vector2(box_size, box_size)))
	hide_spots.clear()
	if level_index == MOMMY_LEVEL_INDEX:
		for hide_spec in house_hide_specs:
			hide_spots.append({"pos": ORIGIN + hide_spec.pos, "label": hide_spec.label})
	elif level_index < DEVIL_LEVEL_INDEX:
		var hide_positions := [
			Vector2(
				ORIGIN.x + WALL_THICKNESS + passage * 0.5,
				ORIGIN.y + WALL_THICKNESS + passage * 0.5 + box_size + passage
			),
			Vector2(
				ORIGIN.x + WALL_THICKNESS + passage * 0.5 + 2.0 * (box_size + passage),
				ORIGIN.y + WALL_THICKNESS + passage * 0.5
			),
			Vector2(
				(
					ORIGIN.x
					+ WALL_THICKNESS
					+ passage * 0.5
					+ float(maxi(columns - 2, 0)) * (box_size + passage)
				),
				ORIGIN.y + WALL_THICKNESS + passage * 0.5 + float(rows - 1) * (box_size + passage)
			)
		]
		for position in hide_positions:
			hide_spots.append({"pos": position})
	for spec in door_specs:
		doors.append(
			{
				"a": ORIGIN + spec.a,
				"b": ORIGIN + spec.b,
				"color": spec.color,
				"trigger": spec.trigger,
				"glass": bool(spec.get("glass", false)),
				"broken": false,
				"quiet_opening": false,
				"room_a": int(spec.get("room_a", -1)),
				"room_b": int(spec.get("room_b", -1)),
				"progress": 0.0,
				"open": false
			}
		)
	if level_index == MOMMY_LEVEL_INDEX:
		exit_rect = Rect2(ORIGIN + Vector2(462, 648), Vector2(76, 38))
	else:
		exit_rect = (
			Rect2()
			if level_index >= DEVIL_LEVEL_INDEX
			else Rect2(ORIGIN + exit_min, exit_max - exit_min)
		)
	if level_index < DEVIL_LEVEL_INDEX:
		for spot in hide_spots:
			assert(
				not exit_rect.grow(35.0).has_point(spot.pos),
				"Hiding spots must not overlap the extraction area"
			)
	player_position = ORIGIN + Vector2(WALL_THICKNESS, WALL_THICKNESS) + spawns[0]
	level3_time_left = LEVEL3_DURATION
	mommy_voice_stage = -1
	mommy_voice_time_left = 0.0
	player_health = 100.0
	player_angle = 0.0
	player_facing_left = false
	player_is_jumping = false
	jump_timer = 0.0
	jump_cooldown = 0.0
	melee_cooldown = 0.0
	player_dead = false
	player_hidden = false
	hidden_spot_index = -1
	hidden_time = 0.0
	mommy_knows_hidden_spot = false
	mommy_known_hide_position = Vector2.ZERO
	player_anim = "idle"
	player_anim_time = 0.0
	player_attack_time = 0.0
	sprint_noise = false
	alarm_active = false
	alarm_timer = alarm_seconds
	extract_ready = false
	for spec in enemy_specs:
		var path: Array[Vector2] = []
		for point in spec.path:
			path.append(ORIGIN + point)
		var start_angle := (path[1] - path[0]).angle() if path.size() > 1 else 0.0
		var mommy_patrol_order: Array = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
		mommy_patrol_order.shuffle()
		(
			enemies
			. append(
				{
					"name": spec.name,
					"mommy": bool(spec.get("mommy", false)),
					"boss": bool(spec.get("boss", false)),
					"shielded": spec.shielded,
					"speed": spec.speed,
					"pos": path[0],
					"path": path,
					"waypoint": 1 if path.size() > 1 else 0,
					"direction": 1,
					"angle": start_angle,
					"health": float(BOSS_MAX_HITS) if bool(spec.get("boss", false)) else 100.0,
					"alive": true,
					"alert": false,
					"investigate": 0.0,
					"investigate_point": path[0],
					"attack_timer": 0.0,
					"shot_timer": 0.0,
					"pursuit_timer": 0.0,
					"mom_was_seen": false,
					"mom_pursuing": false,
					"mom_voice_tracking": false,
					"mom_searching": false,
					"mom_waiting": false,
					"mom_search_timer": 0.0,
					"mom_patrol_index": 0,
					"mom_patrol_order": mommy_patrol_order,
					"mom_search_index": 0,
					"mom_stuck_timer": 0.0,
					"mom_last_position": path[0],
					"last_seen": path[0],
					"shield_timer": 0.0,
					"flash": 0.0,
					"anim": "idle",
					"anim_time": 0.0,
				}
			)
		)
	for spec in camera_mounts:
		cameras.append(
			{
				"pos": ORIGIN + spec.position,
				"base_angle": spec.angle,
				"angle": spec.angle,
				"phase": 0.0,
				"triggered": false
			}
		)
	for spec in item_specs:
		collectibles.append(
			{
				"pos": ORIGIN + spec.pos,
				"medkit": spec.medkit,
				"diamond": false,
				"value": spec.value,
				"collected": false,
				"phase": randf() * TAU
			}
		)
	var camera: Camera2D
	if has_node("Camera2D"):
		camera = get_node("Camera2D") as Camera2D
	else:
		camera = Camera2D.new()
		camera.name = "Camera2D"
		add_child(camera)
	camera.make_current()
	camera.position = ORIGIN + world_size * 0.5
	camera.zoom = (LEVEL3_CAMERA_ZOOM if level_index >= DEVIL_LEVEL_INDEX else Vector2(1.8, 1.8))
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 4.0
	camera.position = ORIGIN + world_size * 0.5
	_update_camera(true)


func _tick_game(delta: float) -> void:
	melee_cooldown = maxf(0.0, melee_cooldown - delta)
	fire_cooldown = maxf(0.0, fire_cooldown - delta)
	player_damage_flash = maxf(0.0, player_damage_flash - delta)
	jump_cooldown = maxf(0.0, jump_cooldown - delta)
	player_attack_time = maxf(0.0, player_attack_time - delta)
	melee_flash = maxf(0.0, melee_flash - delta)
	if player_is_jumping:
		jump_timer -= delta
		if jump_timer <= 0.0:
			player_is_jumping = false
	var movement := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if player_hidden and movement.length_squared() > 0.0:
		player_hidden = false
		hidden_spot_index = -1
		hidden_time = 0.0
		mommy_knows_hidden_spot = false
	if player_hidden:
		hidden_time += delta
		if hidden_time >= HIDE_LIMIT_SECONDS and not mommy_knows_hidden_spot:
			_mommy_discovers_hide_spot()
	var previous_anim := player_anim
	var sprinting := Input.is_action_pressed("sprint") and movement.length_squared() > 0.0
	sprint_noise = false
	if movement.length_squared() > 0.0:
		player_angle = movement.angle()
		if absf(movement.x) > 0.01:
			player_facing_left = movement.x < 0.0
		var speed := (
			player_speed * 0.3
			if Input.is_action_pressed("interact")
			else player_speed * (1.6 if sprinting else 1.0)
		)
		var before := player_position
		_move_player(movement.normalized() * speed * delta)
		var moved := player_position.distance_to(before) > 0.05
		sprint_noise = sprinting and moved
		if moved:
			footstep_noise_timer -= delta
			if footstep_noise_timer <= 0.0:
				var is_interacting := Input.is_action_pressed("interact")
				var noise_kind := "FLOORBOARD_CREAK" if not sprinting else "RUNNING"
				var noise_intensity := 18.0 if is_interacting else (34.0 if not sprinting else SPRINT_NOISE_RADIUS)
				_emit_noise(noise_kind, player_position, noise_intensity)
				footstep_noise_timer = 0.5 if not sprinting else 0.28
			if level_index == MOMMY_LEVEL_INDEX:
				furniture_noise_timer = maxf(0.0, furniture_noise_timer - delta)
				if furniture_noise_timer <= 0.0:
					for furniture in house_furniture:
						if _circle_rect(player_position, PLAYER_RADIUS + 4.0, furniture.rect):
							_emit_noise("BUMPED_FURNITURE", player_position, 42.0)
							furniture_noise_timer = 0.8
							break
		if player_attack_time <= 0.0:
			player_anim = "run" if sprint_noise else ("walk" if moved else "idle")
	else:
		if player_attack_time <= 0.0 and not player_is_jumping:
			player_anim = "idle"
	if player_is_jumping:
		player_anim = "jump"
	if Input.is_action_just_pressed("jump") and jump_cooldown <= 0.0 and not player_is_jumping:
		player_is_jumping = true
		jump_timer = 0.38
		jump_cooldown = 0.55
		_play_sfx("jump")
	if Input.is_action_just_pressed("attack") and not player_hidden:
		_handle_player_attack()
	if player_attack_time > 0.0:
		player_anim = "attack"
	if player_anim == previous_anim:
		player_anim_time += delta
	else:
		player_anim_time = 0.0
	_update_doors(delta)
	_update_glass_debris(delta)
	_propagate_noise(delta)
	_update_enemies(delta)
	if game_state != "playing":
		return
	_update_player_bolts(delta)
	_update_active_lasers(delta)
	_update_enemy_bullets(delta)
	if game_state != "playing":
		return
	_update_cameras(delta)
	if game_state != "playing":
		return
	_update_collectibles(delta)
	_update_camera()
	if alarm_active:
		alarm_timer = maxf(0.0, alarm_timer - delta)
		if alarm_timer <= 0.0:
			_end_game(false, "FACILITY LOCKDOWN TIMEOUT - OPERATIVE COMPROMISED")
			return
	if level_index == MOMMY_LEVEL_INDEX:
		level3_time_left = maxf(0.0, level3_time_left - delta)
		if level3_time_left <= 0.0:
			_end_game(false, "NIGHTMARE TIME EXPIRED BEFORE REACHING THE EXIT")
			return
	if level_index < DEVIL_LEVEL_INDEX and _exit_reached():
		var living := _alive_enemy_count()
		_win(living == 0, living)
	elif level_index == MOMMY_LEVEL_INDEX and _exit_reached():
		_win(true, 0)


func _move_player(delta_position: Vector2) -> void:
	if player_hidden:
		return
	var target_x := player_position + Vector2(delta_position.x, 0)
	if not _position_blocked(target_x, PLAYER_RADIUS):
		player_position.x = target_x.x
	var target_y := player_position + Vector2(0, delta_position.y)
	if not _position_blocked(target_y, PLAYER_RADIUS):
		player_position.y = target_y.y


func _position_blocked(point: Vector2, radius: float) -> bool:
	for rect in walls:
		if _circle_rect(point, radius, rect):
			return true
	for rect in boxes:
		if _circle_rect(point, radius, rect):
			return true
	for door in doors:
		if _door_blocks_circle(door, point, radius):
			return true
	return false


func _random_walkable_position(
	radius: float, avoid_position: Vector2 = Vector2.ZERO, minimum_distance: float = 0.0
) -> Vector2:
	for attempt in range(160):
		var candidate := Vector2(
			randf_range(
				ORIGIN.x + WALL_THICKNESS + radius,
				ORIGIN.x + world_size.x - WALL_THICKNESS - radius
			),
			randf_range(
				ORIGIN.y + WALL_THICKNESS + radius,
				ORIGIN.y + world_size.y - WALL_THICKNESS - radius
			)
		)
		if _blocked_by_static_geometry(candidate, radius):
			continue
		if _position_blocked(candidate, radius):
			continue
		if candidate.distance_to(avoid_position) < minimum_distance:
			continue
		return candidate
	return player_position


func _circle_rect(point: Vector2, radius: float, rect: Rect2) -> bool:
	var closest := Vector2(
		clampf(point.x, rect.position.x, rect.end.x), clampf(point.y, rect.position.y, rect.end.y)
	)
	return point.distance_squared_to(closest) <= radius * radius


func _door_segment(door: Dictionary) -> Array[Vector2]:
	var a: Vector2 = door.a
	var b: Vector2 = door.b
	return [a, a.lerp(b, 1.0 - float(door.progress))]


func _door_blocks_circle(door: Dictionary, point: Vector2, radius: float) -> bool:
	if bool(door.get("broken", false)):
		return false
	if float(door.progress) >= 0.75:
		return false
	var segment := _door_segment(door)
	return _distance_to_segment(point, segment[0], segment[1]) <= radius + 2.5


func _distance_to_segment(point: Vector2, start: Vector2, end: Vector2) -> float:
	var segment := end - start
	var length_squared := segment.length_squared()
	if length_squared < 0.000001:
		return point.distance_to(start)
	var t := clampf((point - start).dot(segment) / length_squared, 0.0, 1.0)
	return point.distance_to(start + t * segment)


func _update_doors(delta: float) -> void:
	for door in doors:
		if bool(door.get("broken", false)):
			door.progress = 1.0
			door.open = true
			continue
		var open_trigger := (
			maxf(float(door.trigger), 95.0)
			if level_index == MOMMY_LEVEL_INDEX
			else float(door.trigger)
		)
		if bool(door.get("glass", false)) and bool(door.get("quiet_opening", false)):
			door.open = true
		elif bool(door.get("glass", false)):
			var player_at_door := (
				player_position.distance_to((door.a + door.b) * 0.5) <= float(door.trigger)
			)
			var enemy_at_door := false
			for enemy in enemies:
				if (
					enemy.alive
					and (bool(enemy.get("mommy", false)) or bool(enemy.get("boss", false)))
					and (Vector2(enemy.pos).distance_to((door.a + door.b) * 0.5) <= open_trigger)
				):
					enemy_at_door = true
					break
			if player_at_door or enemy_at_door:
				_shatter_glass_door(door)
				continue
		var should_open := (
			bool(door.get("quiet_opening", false))
			or player_position.distance_to((door.a + door.b) * 0.5) <= open_trigger
		)
		for enemy in enemies:
			if (
				enemy.alive
				and (bool(enemy.get("mommy", false)) or bool(enemy.get("boss", false)))
				and Vector2(enemy.pos).distance_to((door.a + door.b) * 0.5) <= open_trigger
			):
				should_open = true
				break
		if should_open != bool(door.open):
			door.open = should_open
			if not bool(door.get("glass", false)):
				_play_sfx("door")
		var target := 1.0 if should_open else 0.0
		var open_speed := 1.1 if bool(door.get("quiet_opening", false)) else 7.2
		door.progress = move_toward(float(door.progress), target, open_speed * delta)
		if bool(door.get("quiet_opening", false)) and float(door.progress) >= 1.0:
			door.quiet_opening = false


func _interact_with_glass_door() -> void:
	var closest_door: Dictionary = {}
	var closest_distance := 110.0
	for door in doors:
		if not bool(door.get("glass", false)) or bool(door.get("broken", false)):
			continue
		var distance: float = player_position.distance_to((door.a + door.b) * 0.5)
		if distance < closest_distance:
			closest_distance = distance
			closest_door = door
	if closest_door.is_empty():
		return
	closest_door.quiet_opening = true
	closest_door.open = true


func _shatter_glass_door(door: Dictionary) -> void:
	if bool(door.get("broken", false)):
		return
	door.broken = true
	door.open = true
	door.quiet_opening = false
	door.progress = 1.0
	var threshold: Vector2 = (door.a + door.b) * 0.5
	glass_debris.append({"pos": threshold, "timer": 0.0, "crunched": false})
	_emit_noise("GLASS_SHATTER", threshold, GLASS_NOISE_INTENSITY, GLASS_NOISE_RADIUS)
	_play_sfx("glass_shatter")


func _update_glass_debris(delta: float) -> void:
	var movement := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var is_moving := sprint_noise or movement.length_squared() > 0.0
	for debris in glass_debris:
		debris.timer = maxf(0.0, float(debris.timer) - delta)
		if (
			is_moving
			and float(debris.timer) <= 0.0
			and player_position.distance_to(debris.pos) <= PLAYER_RADIUS + 24.0
		):
			_emit_noise("GLASS_CRUNCH", player_position, 48.0)
			_play_sfx("glass_crunch")
			debris.timer = 1.0


func _handle_player_attack() -> void:
	if level_index == MOMMY_LEVEL_INDEX:
		return
	if fire_cooldown <= 0.0:
		fire_cooldown = BOLT_COOLDOWN
		var facing := Vector2(cos(player_angle), sin(player_angle))
		var bolt_pos := player_position + facing * 21.0
		player_bolts.append({
			"pos": bolt_pos,
			"velocity": facing * BOLT_SPEED,
			"damage": BOLT_DAMAGE,
			"lifetime": 0.0
		})
		player_attack_time = 0.25
		player_anim = "attack"
		_play_sfx("laser")
	if melee_cooldown <= 0.0:
		_swing_melee()


func _update_player_bolts(delta: float) -> void:
	for index in range(player_bolts.size() - 1, -1, -1):
		var bolt: Dictionary = player_bolts[index]
		var from_pos: Vector2 = bolt.pos
		var to_pos: Vector2 = from_pos + Vector2(bolt.velocity) * delta
		bolt.lifetime = float(bolt.lifetime) + delta
		var obstacle_hit := _first_obstacle_hit(from_pos, to_pos)
		if obstacle_hit.hit:
			player_bolts.remove_at(index)
			continue
		var hit_target := false
		for e_idx in range(enemies.size()):
			var enemy: Dictionary = enemies[e_idx]
			if not enemy.alive or bool(enemy.get("mommy", false)):
				continue
			var is_boss: bool = bool(enemy.get("boss", false))
			var hit_radius: float = (28.0 if is_boss else ENEMY_RADIUS) + BOLT_RADIUS
			var closest: Vector2 = _segment_closest_point(from_pos, to_pos, enemy.pos)
			if closest.distance_to(enemy.pos) <= hit_radius:
				hit_target = true
				if is_boss:
					_damage_enemy(e_idx, float(bolt.damage))
				elif enemy.shielded:
					var facing := Vector2(cos(float(enemy.angle)), sin(float(enemy.angle)))
					var to_bolt := (from_pos - Vector2(enemy.pos)).normalized()
					if facing.dot(to_bolt) > 0.25:
						_damage_enemy(e_idx, float(bolt.damage) * 0.75)
						enemy.flash = 0.12
						enemy.shield_timer = 0.35
						_play_sfx("shield")
					else:
						_damage_enemy(e_idx, float(bolt.damage))
				else:
					_damage_enemy(e_idx, float(bolt.damage))
				player_bolts.remove_at(index)
				break
		if hit_target:
			continue
		if float(bolt.lifetime) >= BOLT_MAX_LIFETIME:
			player_bolts.remove_at(index)
		else:
			bolt.pos = to_pos


func _update_active_lasers(delta: float) -> void:
	for i in range(active_lasers.size() - 1, -1, -1):
		active_lasers[i].timer = float(active_lasers[i].timer) - delta
		if float(active_lasers[i].timer) <= 0.0:
			active_lasers.remove_at(i)


func _swing_melee() -> void:
	melee_cooldown = 0.48
	player_attack_time = 0.62
	melee_flash = 0.28
	player_anim = "attack"
	for index in range(enemies.size()):
		var enemy: Dictionary = enemies[index]
		if not enemy.alive or bool(enemy.get("mommy", false)):
			continue
		var offset: Vector2 = enemy.pos - player_position
		if (
			offset.length() > MELEE_RANGE
			or absf(wrapf(offset.angle() - player_angle, -PI, PI)) > 0.9
		):
			continue
		if not _has_line_of_sight(player_position, enemy.pos):
			continue
		if enemy.shielded:
			var facing := Vector2(cos(float(enemy.angle)), sin(float(enemy.angle)))
			if facing.dot(-offset.normalized()) > 0.25:
				enemy.flash = 0.12
				enemy.shield_timer = 0.35
				_play_sfx("shield")
				continue
		_damage_enemy(index, PLAYER_MELEE_DAMAGE)
	_play_sfx("impact")


func _toggle_hide_spot(mouse_position: Vector2) -> void:
	if exit_rect.has_point(mouse_position):
		return
	if player_hidden:
		if (
			hidden_spot_index >= 0
			and mouse_position.distance_to(hide_spots[hidden_spot_index].pos) <= 56.0
		):
			player_hidden = false
			hidden_spot_index = -1
			hidden_time = 0.0
			mommy_knows_hidden_spot = false
		return
	for index in range(hide_spots.size()):
		var spot: Dictionary = hide_spots[index]
		if (
			mouse_position.distance_to(spot.pos) <= 30.0
			and player_position.distance_to(spot.pos) <= 64.0
		):
			player_position = spot.pos
			player_hidden = true
			hidden_spot_index = index
			hidden_time = 0.0
			mommy_knows_hidden_spot = false
			sprint_noise = false
			player_anim = "idle"
			return


func _update_enemies(delta: float) -> void:
	for index in range(enemies.size()):
		var enemy: Dictionary = enemies[index]
		if not enemy.alive:
			continue
		if bool(enemy.get("boss", false)):
			_update_boss_roaming(enemy, delta)
			continue
		var is_mommy := bool(enemy.get("mommy", false))
		if (
			is_mommy
			and not player_hidden
			and Vector2(enemy.pos).distance_to(player_position) <= ENEMY_RADIUS + PLAYER_RADIUS
		):
			_end_game(false, "MOMMY CAUGHT FREENIGHT")
			return
		var previous_anim := String(enemy.anim)
		enemy.flash = maxf(0.0, float(enemy.flash) - delta)
		enemy.shield_timer = maxf(0.0, float(enemy.shield_timer) - delta)
		enemy.attack_timer = maxf(0.0, float(enemy.attack_timer) - delta)
		enemy.shot_timer = maxf(0.0, float(enemy.shot_timer) - delta)
		if enemy.has("mom_search_cooldown"):
			enemy.mom_search_cooldown = maxf(0.0, float(enemy.mom_search_cooldown) - delta)
		var base_cone_range: float = ENFORCER_CONE_RANGE if enemy.shielded else GUARD_CONE_RANGE
		var cone_range: float = base_cone_range * (1.25 if alarm_active else 1.0)
		var sees_player := false
		if is_mommy:
			sees_player = (
				not player_hidden
				and (
					(
						bool(enemy.get("mom_pursuing", false))
						and _has_line_of_sight(enemy.pos, player_position)
					)
					or (
						Vector2(enemy.pos).distance_to(player_position)
						<= ENEMY_RADIUS + PLAYER_RADIUS + 8.0
						and _has_line_of_sight(enemy.pos, player_position)
					)
				)
			)
		else:
			sees_player = (
				not player_hidden
				and _vision_contains(
					enemy.pos + Vector2(cos(enemy.angle), sin(enemy.angle)) * 14.0,
					enemy.angle,
					GUARD_CONE_FOV,
					cone_range,
					player_position,
					28
				)
				and _has_line_of_sight(enemy.pos, player_position)
			)
		if enemy.shielded and not player_hidden:
			if Vector2(enemy.pos).distance_to(player_position) <= ENEMY_RADIUS + PLAYER_RADIUS:
				var facing := Vector2(cos(float(enemy.angle)), sin(float(enemy.angle)))
				var to_player := (player_position - Vector2(enemy.pos)).normalized()
				if facing.dot(to_player) > 0.0:
					_move_player(facing * ENFORCER_SHOVE_SPEED * delta)
					if float(enemy.get("shove_cooldown", 0.0)) <= 0.0:
						_play_sfx("shield")
						enemy["shove_cooldown"] = 0.35
		if enemy.has("shove_cooldown"):
			enemy.shove_cooldown = maxf(0.0, float(enemy.shove_cooldown) - delta)
		if (
			is_mommy
			and player_hidden
			and mommy_knows_hidden_spot
			and Vector2(enemy.pos).distance_to(mommy_known_hide_position) <= 58.0
		):
			sees_player = true
		if sees_player:
			enemy.last_seen = player_position
			enemy.pursuit_timer = PURSUIT_SECONDS
			if is_mommy:
				enemy.mom_pursuing = true
				enemy.mom_voice_tracking = false
				enemy.mom_was_seen = true
				enemy.mom_searching = false
				enemy.mom_waiting = false
		elif is_mommy and bool(enemy.get("mom_pursuing", false)) and not player_hidden:
			if sees_player:
				enemy.last_seen = player_position
				enemy.pursuit_timer = PURSUIT_SECONDS
			else:
				# Mommy is blind and player made no direct contact/line-of-sight: pursuit timer ticks down toward search
				enemy.pursuit_timer = maxf(0.0, float(enemy.pursuit_timer) - delta)
				if float(enemy.pursuit_timer) <= 0.0:
					enemy.mom_pursuing = false
					enemy.mom_voice_tracking = false
					enemy.mom_searching = true
					enemy.mom_search_index = 0
					enemy.mom_search_timer = 0.0
		else:
			if is_mommy and bool(enemy.get("mom_pursuing", false)) and player_hidden:
				enemy.mom_pursuing = false
				enemy.mom_voice_tracking = false
				enemy.mom_was_seen = false
				enemy.mom_searching = true
				enemy.mom_search_index = 0
				enemy.mom_waiting = false
				enemy.mom_search_timer = 0.0
			elif is_mommy and bool(enemy.mom_was_seen):
				enemy.mom_was_seen = false
				enemy.mom_searching = true
				enemy.mom_waiting = false
			enemy.pursuit_timer = maxf(0.0, float(enemy.pursuit_timer) - delta)
		if (
			sees_player
			and not is_mommy
			and float(enemy.shot_timer) <= 0.0
			and _has_line_of_sight(enemy.pos, player_position)
		):
			var shot_damage: float = 8.0 if enemy.shielded else 10.0
			var shot_cooldown: float = 1.55 if enemy.shielded else 1.35
			enemy.shot_timer = shot_cooldown
			enemy.anim = "shoot"
			var laser_origin: Vector2 = enemy.pos + Vector2(cos(enemy.angle), sin(enemy.angle)) * 25.9
			var obs_hit := _first_obstacle_hit(laser_origin, player_position)
			var target_pos := player_position
			if obs_hit.hit:
				target_pos = obs_hit.point
				active_lasers.append({
					"from": laser_origin,
					"to": target_pos,
					"timer": 0.10,
					"color": Color(1.0, 0.15, 0.3, 0.35),
					"core": Color(1.0, 0.75, 0.8)
				})
			else:
				_damage_player(shot_damage)
				active_lasers.append({
					"from": laser_origin,
					"to": target_pos,
					"timer": 0.12,
					"color": Color(1.0, 0.15, 0.3, 0.45),
					"core": Color(1.0, 0.85, 0.9)
				})
			_play_sfx("laser")
		enemy.alert = (
			float(enemy.pursuit_timer) > 0.0
			or (is_mommy and bool(enemy.mom_pursuing))
			or (is_mommy and bool(enemy.mom_searching))
			or (is_mommy and bool(enemy.get("mom_voice_tracking", false)))
		)
		if enemy.alert:
			var target: Vector2 = enemy.last_seen
			if (
				sees_player
				or (
					is_mommy
					and bool(enemy.mom_pursuing)
					and not player_hidden
				)
			):
				target = player_position
			if is_mommy and bool(enemy.mom_searching) and not sees_player:
				enemy.mom_search_timer = float(enemy.get("mom_search_timer", 0.0)) + delta
				var search_offsets := [
					Vector2.ZERO,
					Vector2(35.0, 0.0),
					Vector2(-35.0, 0.0),
					Vector2(0.0, 35.0),
					Vector2(0.0, -35.0)
				]
				var search_index := int(enemy.get("mom_search_index", 0))
				target = (
					enemy.last_seen + search_offsets[mini(search_index, search_offsets.size() - 1)]
				)
				if Vector2(enemy.pos).distance_to(target) <= ENEMY_RADIUS + PLAYER_RADIUS + 10.0:
					search_index += 1
					enemy.mom_search_index = search_index
				if search_index >= search_offsets.size() or float(enemy.mom_search_timer) >= 3.2:
					enemy.mom_searching = false
					enemy.mom_waiting = false
					enemy.mom_voice_tracking = false
					enemy.mom_pursuing = false
					enemy.pursuit_timer = 0.0
					enemy.alert = false
					enemy.mom_search_cooldown = 5.0
					# Pick a different room immediately so Mommy walks away
					var cur_rm := _house_room_at(enemy.pos)
					var p_order: Array = enemy.get("mom_patrol_order", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
					var p_idx := int(enemy.get("mom_patrol_index", 0))
					for attempt in range(p_order.size()):
						p_idx = (p_idx + 1) % p_order.size()
						if int(p_order[p_idx]) != cur_rm:
							break
					enemy.mom_patrol_index = p_idx
					if not enemy.alert:
						_patrol_mommy(enemy, delta)
						continue
				else:
					target = enemy.last_seen + search_offsets[search_index]
			var target_difference: Vector2 = target - enemy.pos
			var movement_target := _mommy_navigation_target(enemy, target) if is_mommy else target
			var difference: Vector2 = movement_target - enemy.pos
			var reached_waypoint := (
				difference.length() <= (12.0 if is_mommy else ENEMY_RADIUS + PLAYER_RADIUS)
			)
			var reached_target := (
				target_difference.length() <= (ENEMY_RADIUS + PLAYER_RADIUS + 4.0)
				and _house_room_at(enemy.pos) == _house_room_at(target)
			) if is_mommy else difference.length() <= ENEMY_RADIUS + PLAYER_RADIUS
			if not reached_target and (not is_mommy or difference.length() > 6.0):
				var is_fast := is_mommy and (bool(enemy.mom_pursuing) or bool(enemy.get("mom_voice_tracking", false)))
				var turn_speed := deg_to_rad(360.0 if is_fast else 300.0) * delta
				enemy.angle = _turn_toward(float(enemy.angle), difference.angle(), turn_speed)
				var speed := 135.0 if is_fast else float(enemy.speed) * (1.3 if alarm_active else 1.0)
				var prev_pos: Vector2 = enemy.pos
				_move_enemy_toward(enemy, difference.normalized() * speed * delta)
				if is_mommy and Vector2(enemy.pos).distance_to(prev_pos) < 0.2:
					enemy.mom_stuck_timer = float(enemy.get("mom_stuck_timer", 0.0)) + delta
					if float(enemy.mom_stuck_timer) >= 0.2:
						# Nudge toward movement target or portal
						var side := Vector2(-difference.normalized().y, difference.normalized().x)
						_move_enemy_toward(enemy, side * speed * 0.7 * delta)
				else:
					enemy.mom_stuck_timer = 0.0
				enemy.anim = "walk"
			elif (
				sees_player
				and (not player_hidden or (is_mommy and mommy_knows_hidden_spot))
				and (
					Vector2(enemy.pos).distance_to(player_position)
					<= ENEMY_RADIUS + PLAYER_RADIUS + 10.0
				)
				and float(enemy.attack_timer) <= 0.0
			):
				enemy.angle = _turn_toward(
					float(enemy.angle),
					(player_position - enemy.pos).angle(),
					deg_to_rad(360.0) * delta
				)
				enemy.attack_timer = 0.9
				enemy.anim = "attack"
				if is_mommy:
					_end_game(false, "MOMMY CAUGHT FREENIGHT")
					return
				_damage_player(10.0 if enemy.shielded else 8.0)
				_play_sfx("impact")
			else:
				if is_mommy and (bool(enemy.get("mom_voice_tracking", false)) or bool(enemy.get("mom_pursuing", false))):
					enemy.mom_pursuing = false
					enemy.mom_voice_tracking = false
					enemy.mom_searching = true
					enemy.mom_search_index = 0
					enemy.mom_search_timer = 0.0
				enemy.anim = "idle"
		else:
			if is_mommy:
				_patrol_mommy(enemy, delta)
			else:
				_patrol_enemy(enemy, delta)
		if String(enemy.anim) == previous_anim:
			enemy.anim_time = float(enemy.anim_time) + delta
		else:
			enemy.anim_time = 0.0


func _patrol_mommy(enemy: Dictionary, delta: float) -> void:
	var room_waypoints: Array[Vector2] = [
		Vector2(105, 55),
		Vector2(305, 55),
		Vector2(105, 195),
		Vector2(310, 195),
		Vector2(525, 55),
		Vector2(820, 72),
		Vector2(820, 205),
		Vector2(205, 500),
		Vector2(525, 500),
		Vector2(825, 455)
	]
	var patrol_order: Array = enemy.get("mom_patrol_order", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
	var route_index := int(enemy.get("mom_patrol_index", 0)) % patrol_order.size()
	var current_room := _house_room_at(enemy.pos)
	var target_room := int(patrol_order[route_index])
	var target := ORIGIN + room_waypoints[target_room]
	var waypoint := _mommy_navigation_target(enemy, target)
	var difference: Vector2 = waypoint - enemy.pos
	if (target_room == current_room and difference.length() <= 32.0) or (difference.length() <= 22.0 and _house_room_at(enemy.pos) == _house_room_at(target)):
		route_index = (route_index + 1) % patrol_order.size()
		if route_index == 0:
			patrol_order.shuffle()
			enemy.mom_patrol_order = patrol_order
		enemy.mom_patrol_index = route_index
		target_room = int(patrol_order[route_index])
		target = ORIGIN + room_waypoints[target_room]
		waypoint = _mommy_navigation_target(enemy, target)
		difference = waypoint - enemy.pos
	enemy.angle = _turn_toward(float(enemy.angle), difference.angle(), deg_to_rad(300.0) * delta)
	var previous_position: Vector2 = enemy.pos
	var step := minf(float(enemy.speed) * delta, difference.length())
	_move_enemy_toward(enemy, difference.normalized() * step)
	if Vector2(enemy.pos).distance_to(previous_position) < 0.5:
		enemy.mom_stuck_timer = float(enemy.mom_stuck_timer) + delta
		if float(enemy.mom_stuck_timer) >= 0.28:
			enemy.mom_patrol_index = (route_index + 1) % patrol_order.size()
			enemy.mom_stuck_timer = 0.0
	else:
		enemy.mom_stuck_timer = 0.0
	enemy.anim = "walk"


func _mommy_navigation_target(enemy: Dictionary, target: Vector2) -> Vector2:
	var current_room := _house_room_at(enemy.pos)
	var destination_room := _house_room_at(target)
	if current_room == destination_room:
		return target
	var queue: Array[int] = [current_room]
	var previous_room := {current_room: -1}
	var previous_door := {}
	while not queue.is_empty():
		var room: int = queue.pop_front()
		if room == destination_room:
			break
		for door in doors:
			var room_a := int(door.get("room_a", -1))
			var room_b := int(door.get("room_b", -1))
			var next_room: int = room_b if room_a == room else room_a if room_b == room else -1
			if next_room < 0 or previous_room.has(next_room):
				continue
			previous_room[next_room] = room
			previous_door[next_room] = door
			queue.append(next_room)
	if not previous_room.has(destination_room):
		return target
	var route_room := destination_room
	while int(previous_room[route_room]) != current_room:
		route_room = int(previous_room[route_room])
	var door: Dictionary = previous_door[route_room]
	var portal: Vector2 = (door.a + door.b) * 0.5
	var dest_center := _house_room_center(route_room)
	var is_horizontal := is_equal_approx(door.a.y, door.b.y)
	if is_horizontal:
		var dir_y := 1.0 if dest_center.y > portal.y else -1.0
		var approach := Vector2(portal.x, portal.y - dir_y * 18.0)
		var through_point := Vector2(portal.x, portal.y + dir_y * 28.0)
		var crossed_portal: bool = (Vector2(enemy.pos).y - portal.y) * dir_y >= 0.0
		if crossed_portal or Vector2(enemy.pos).distance_to(approach) <= 22.0:
			return through_point
		return approach
	else:
		var dir_x := 1.0 if dest_center.x > portal.x else -1.0
		var approach := Vector2(portal.x - dir_x * 18.0, portal.y)
		var through_point := Vector2(portal.x + dir_x * 28.0, portal.y)
		var crossed_portal: bool = (Vector2(enemy.pos).x - portal.x) * dir_x >= 0.0
		if crossed_portal or Vector2(enemy.pos).distance_to(approach) <= 22.0:
			return through_point
		return approach


func _house_room_center(room_index: int) -> Vector2:
	var centers := [
		Vector2(100, 55),
		Vector2(300, 55),
		Vector2(100, 195),
		Vector2(300, 195),
		Vector2(525, 55),
		Vector2(820, 75),
		Vector2(820, 205),
		Vector2(200, 480),
		Vector2(525, 400),
		Vector2(820, 480)
	]
	return ORIGIN + centers[clampi(room_index, 0, centers.size() - 1)]


func _mommy_discovers_hide_spot() -> void:
	mommy_knows_hidden_spot = true
	mommy_known_hide_position = player_position
	for enemy in enemies:
		if enemy.alive and bool(enemy.get("mommy", false)):
			enemy.last_seen = mommy_known_hide_position
			enemy.pursuit_timer = PURSUIT_SECONDS
			enemy.mom_was_seen = true
			enemy.mom_searching = false
			enemy.mom_waiting = false
			enemy.alert = true
			break


func _house_room_at(position: Vector2) -> int:
	var local_position := position - ORIGIN
	var room_index := 9
	if local_position.x < 410.0:
		if local_position.y < 118.0:
			room_index = 0 if local_position.x < 205.0 else 1
		elif local_position.y < 270.0:
			room_index = 2 if local_position.x < 205.0 else 3
		else:
			room_index = 7
	elif local_position.x < 640.0:
		room_index = 4 if local_position.y < 118.0 else 8
	elif local_position.y < 148.0:
		room_index = 5
	elif local_position.y < 268.0:
		room_index = 6
	return room_index


func _update_boss_roaming(enemy: Dictionary, delta: float) -> void:
	enemy.flash = maxf(0.0, float(enemy.flash) - delta)
	enemy.boss_hit_cooldown = maxf(0.0, float(enemy.boss_hit_cooldown) - delta)
	enemy.shot_timer = maxf(0.0, float(enemy.shot_timer) - delta)
	if float(enemy.boss_relocate_timer) > 0.0:
		enemy.boss_relocate_timer = maxf(0.0, float(enemy.boss_relocate_timer) - delta)
		if float(enemy.boss_relocate_timer) <= 0.0:
			enemy.pos = _random_walkable_position(28.0, player_position, 180.0)
			enemy.boss_roam_target = _random_walkable_position(28.0, enemy.pos, 180.0)
			enemy.boss_run_timer = randf_range(1.2, 2.0)
			enemy.boss_stuck_timer = 0.0
		else:
			enemy.anim = "idle"
			enemy.anim_time = float(enemy.anim_time) + delta
			return
	enemy.boss_run_timer = maxf(0.0, float(enemy.boss_run_timer) - delta)
	var target: Vector2 = enemy.boss_roam_target
	if Vector2(enemy.pos).distance_to(target) <= 28.0:
		target = _random_walkable_position(28.0, enemy.pos, 180.0)
		enemy.boss_roam_target = target
	var direction: Vector2 = target - enemy.pos
	if direction.length_squared() > 0.001:
		enemy.angle = _turn_toward(float(enemy.angle), direction.angle(), deg_to_rad(360.0) * delta)
	if enemy.has("telegraph_timer"):
		enemy.telegraph_timer = maxf(0.0, float(enemy.telegraph_timer) - delta)
	var hp_frac := float(enemy.health) / float(BOSS_MAX_HITS)
	var boss_phase := 1
	var phase_speed := 50.0
	var phase_cooldown := 1.70
	if hp_frac <= 0.33:
		boss_phase = 3
		phase_speed = 84.0
		phase_cooldown = 1.28
	elif hp_frac <= 0.66:
		boss_phase = 2
		phase_speed = 68.0
		phase_cooldown = 1.12
	enemy["boss_phase"] = boss_phase

	var previous_position: Vector2 = enemy.pos
	var base_speed := phase_speed if float(enemy.speed) > 1.0 else float(enemy.speed)
	var speed := 210.0 if float(enemy.boss_run_timer) > 0.0 else base_speed
	_move_enemy_toward(enemy, direction.normalized() * speed * delta, 25.0)
	if Vector2(enemy.pos).distance_to(previous_position) < 0.05:
		enemy.boss_stuck_timer = float(enemy.boss_stuck_timer) + delta
		if float(enemy.boss_stuck_timer) >= 0.8:
			enemy.boss_roam_target = _random_walkable_position(25.0, enemy.pos, 100.0)
			enemy.boss_stuck_timer = 0.0
	else:
		enemy.boss_stuck_timer = 0.0
	var fired := false
	if (
		not player_hidden
		and float(enemy.shot_timer) <= 0.0
		and Vector2(enemy.pos).distance_to(player_position) <= 600.0
		and _has_line_of_sight(enemy.pos, player_position)
	):
		var dist_to_player := Vector2(enemy.pos).distance_to(player_position)
		var shot_direction: Vector2 = (player_position - enemy.pos).normalized()
		_spawn_enemy_bullet(enemy, shot_direction, 25.0, 340.0, false)
		if boss_phase == 3 and dist_to_player <= 76.0:
			_damage_player(16.0)
			_play_sfx("impact")
			enemy["is_slam"] = true
		else:
			enemy["is_slam"] = false
			active_lasers.append({
				"from": enemy.pos,
				"to": player_position,
				"timer": 0.15,
				"color": Color(1.0, 0.2, 0.1, 0.6),
				"core": Color(1.0, 0.9, 0.8)
			})
			_play_sfx("laser")
		enemy.shot_timer = phase_cooldown if float(enemy.speed) > 1.0 else 1.4
		enemy.telegraph_timer = 0.64 if boss_phase == 1 else (0.42 if boss_phase == 2 else 0.86)
		enemy.windup = enemy.telegraph_timer
		fired = true
	enemy.anim = ("attack" if fired else ("run" if float(enemy.boss_run_timer) > 0.0 else "walk"))
	enemy.anim_time = float(enemy.anim_time) + delta


func _spawn_enemy_bullet(
	enemy: Dictionary, direction: Vector2, damage: float, speed: float, shielded: bool
) -> void:
	if direction.length_squared() <= 0.001:
		return
	var shot_direction := direction.normalized()
	enemy_bullets.append(
		{
			"pos": enemy.pos + shot_direction * (ENEMY_RADIUS + 7.0),
			"velocity": shot_direction * speed,
			"damage": damage,
			"shielded": shielded,
			"age": 0.0
		}
	)


func _update_enemy_bullets(delta: float) -> void:
	for index in range(enemy_bullets.size() - 1, -1, -1):
		var bullet: Dictionary = enemy_bullets[index]
		var from: Vector2 = bullet.pos
		var to: Vector2 = from + Vector2(bullet.velocity) * delta
		bullet.age = float(bullet.age) + delta
		var obstacle_hit := _first_obstacle_hit(from, to)
		if obstacle_hit.hit:
			enemy_bullets.remove_at(index)
			continue
		if (
			not player_hidden
			and (
				_segment_closest_point(from, to, player_position).distance_to(player_position)
				<= PLAYER_RADIUS + 4.0
			)
		):
			_damage_player(float(bullet.damage))
			enemy_bullets.remove_at(index)
			if game_state != "playing":
				return
		elif float(bullet.age) >= 2.0:
			enemy_bullets.remove_at(index)
		else:
			bullet.pos = to


func _segment_closest_point(start: Vector2, end: Vector2, point: Vector2) -> Vector2:
	var segment := end - start
	if segment.length_squared() <= 0.000001:
		return start
	return (
		start + segment * clampf((point - start).dot(segment) / segment.length_squared(), 0.0, 1.0)
	)


func _move_enemy_toward(
	enemy: Dictionary, movement: Vector2, collision_radius: float = ENEMY_RADIUS
) -> void:
	var target_x: Vector2 = enemy.pos + Vector2(movement.x, 0.0)
	if not _position_blocked(target_x, collision_radius):
		enemy.pos.x = target_x.x
	var target_y: Vector2 = enemy.pos + Vector2(0.0, movement.y)
	if not _position_blocked(target_y, collision_radius):
		enemy.pos.y = target_y.y


func _patrol_enemy(enemy: Dictionary, delta: float) -> void:
	var path: Array = enemy.path
	if path.size() < 2:
		return
	var waypoint := int(enemy.waypoint)
	var target: Vector2 = path[waypoint]
	var difference: Vector2 = target - enemy.pos
	var step := float(enemy.speed) * (1.35 if alarm_active else 1.0) * delta
	if difference.length() <= step:
		enemy.pos = target
		var next := waypoint + int(enemy.direction)
		if next >= path.size():
			enemy.direction = -1
			enemy.waypoint = path.size() - 2
		elif next < 0:
			enemy.direction = 1
			enemy.waypoint = 1
		else:
			enemy.waypoint = next
		enemy.anim = "idle"
	else:
		enemy.angle = difference.angle()
		enemy.pos += difference.normalized() * step
		enemy.anim = "walk"


func _vision_contains(
	origin: Vector2, angle: float, fov: float, distance: float, target: Vector2, rays: int
) -> bool:
	return CG.point_in_polygon(target, CG.cone_polygon(origin, angle, fov, distance, rays))


func _update_camera(snap: bool = false) -> void:
	var camera := get_node_or_null("Camera2D") as Camera2D
	if camera == null:
		return
	var half_view := get_viewport_rect().size / camera.zoom * 0.5
	var target := player_position
	if world_size.x <= half_view.x * 2.0:
		target.x = ORIGIN.x + world_size.x * 0.5
	else:
		target.x = clampf(
			player_position.x, ORIGIN.x + half_view.x, ORIGIN.x + world_size.x - half_view.x
		)
	if world_size.y <= half_view.y * 2.0:
		target.y = ORIGIN.y + world_size.y * 0.5
	else:
		target.y = clampf(
			player_position.y, ORIGIN.y + half_view.y, ORIGIN.y + world_size.y - half_view.y
		)
	if snap:
		camera.position = target
	else:
		camera.position = camera.position.lerp(
			target, clampf(camera.position_smoothing_speed * get_process_delta_time(), 0.0, 1.0)
		)


func _bresenham_contact(
	hitbox_center: Vector2, hitbox_radius: float, target_center: Vector2, target_radius: float
) -> bool:
	var center_distance := hitbox_center.distance_to(target_center)
	if center_distance > hitbox_radius + target_radius + 4.0:
		return false
	for point in CG.bresenham_circle(
		Vector2i(int(hitbox_center.x), int(hitbox_center.y)), int(hitbox_radius)
	):
		if Vector2(point).distance_to(target_center) <= target_radius:
			return true
	return center_distance + target_radius <= hitbox_radius


func _turn_toward(current: float, target: float, max_step: float) -> float:
	return current + clampf(wrapf(target - current, -PI, PI), -max_step, max_step)


func _propagate_noise(delta: float) -> void:
	for event_index in range(noise_events.size() - 1, -1, -1):
		var sound: Dictionary = noise_events[event_index]
		sound.age = float(sound.age) + delta
		if float(sound.age) > float(sound.duration):
			noise_events.remove_at(event_index)
			continue
		if bool(sound.propagated):
			continue
		sound.propagated = true
		var source: Vector2 = sound.origin
		var source_room := _house_room_at(source) if level_index == MOMMY_LEVEL_INDEX else -1
		for enemy in enemies:
			if not enemy.alive:
				continue
			var distance: float = Vector2(enemy.pos).distance_to(source)
			var global_house_sound := String(sound.kind) in ["GLASS_SHATTER", "MICROPHONE"]
			var same_or_adjacent := (
				global_house_sound
				or level_index != MOMMY_LEVEL_INDEX
				or not bool(enemy.get("mommy", false))
				or source_room == _house_room_at(enemy.pos)
				or _rooms_connected(source_room, _house_room_at(enemy.pos))
			)
			if distance > float(sound.radius) or not same_or_adjacent:
				continue
			var reported_position := source
			enemy.last_seen = reported_position
			enemy.pursuit_timer = maxf(
				float(enemy.pursuit_timer),
				maxf(PURSUIT_SECONDS, distance / maxf(1.0, float(enemy.speed)) + 1.5)
			)
			if bool(enemy.get("mommy", false)):
				if String(sound.kind) == "MICROPHONE":
					# If player is safely hidden and Mommy is already searching or finished searching, do not restart pursuit loop
					if player_hidden and (bool(enemy.get("mom_searching", false)) or float(enemy.get("mom_search_cooldown", 0.0)) > 0.0):
						continue
					enemy.mom_pursuing = not player_hidden
					enemy.mom_voice_tracking = true
					enemy.mom_was_seen = false
					enemy.mom_searching = false
					enemy.mom_waiting = false
					enemy.alert = true
				elif String(sound.kind) == "GLASS_SHATTER":
					if not bool(enemy.get("mom_pursuing", false)):
						enemy.mom_pursuing = false
						enemy.mom_voice_tracking = false
						enemy.mom_was_seen = false
						enemy.mom_searching = false
						enemy.mom_waiting = false
						enemy.alert = true
				else:
					enemy.mom_pursuing = not player_hidden
					enemy.mom_voice_tracking = true
					enemy.mom_was_seen = false
					enemy.mom_searching = false
					enemy.mom_waiting = false
					enemy.alert = true
			else:
				enemy.alert = true


func _emit_noise(kind: String, origin: Vector2, intensity: float, radius: float = -1.0) -> void:
	var effective_radius := radius
	if effective_radius < 0.0:
		effective_radius = intensity * 7.0
	noise_events.append(
		{
			"kind": kind,
			"origin": origin,
			"intensity": intensity,
			"radius": effective_radius,
			"age": 0.0,
			"duration": 1.25,
			"propagated": false
		}
	)


func _rooms_connected(first_room: int, second_room: int) -> bool:
	if first_room == second_room:
		return true
	for door in doors:
		if (
			(
				int(door.get("room_a", -1)) == first_room
				and int(door.get("room_b", -1)) == second_room
			)
			or (
				int(door.get("room_a", -1)) == second_room
				and int(door.get("room_b", -1)) == first_room
			)
		):
			return true
	return false


func _damage_enemy(index: int, amount: float) -> void:
	var enemy: Dictionary = enemies[index]
	if not enemy.alive or amount <= 0.0:
		return
	if bool(enemy.get("boss", false)):
		if float(enemy.get("boss_hit_cooldown", 0.0)) > 0.0:
			return
		if not enemy.has("hp"):
			enemy["hp"] = float(enemy.health) * 100.0
		var effective_damage := amount
		if amount < 50.0:
			effective_damage = 75.0
		enemy.hp = maxf(0.0, float(enemy.hp) - effective_damage)
		if amount >= 100.0:
			enemy.health = maxf(0.0, float(enemy.health) - 1.0)
			enemy.boss_relocate_timer = 1.0
			enemy.boss_hit_cooldown = 0.35
		else:
			var prev_health := float(enemy.health)
			enemy.health = clampf(ceil(float(enemy.hp) / 100.0), 0.0, float(BOSS_MAX_HITS))
			enemy.boss_hit_cooldown = 0.12
			if float(enemy.health) < prev_health and float(enemy.health) > 0.0:
				enemy.boss_relocate_timer = 0.6
		enemy.flash = 0.4
		enemy.anim = "hurt"
		enemy.anim_time = 0.0
		_play_sfx("impact")
		if float(enemy.health) > 0.0:
			enemy.boss_relocating = float(enemy.boss_relocate_timer) > 0.0
			enemy.alert = true
			enemy.last_seen = player_position
			enemy.pursuit_timer = PURSUIT_SECONDS
			return
	else:
		enemy.health = maxf(0.0, float(enemy.health) - amount)
	enemy.flash = 0.18
	enemy.alert = true
	enemy.last_seen = player_position
	enemy.pursuit_timer = PURSUIT_SECONDS
	if float(enemy.health) <= 0.0:
		enemy.alive = false
		score += 500
		session_kills += 1
		career_kills += 1
		career_score += 500
		collectibles.append(
			{
				"pos": enemy.pos,
				"medkit": false,
				"diamond": true,
				"value": 250.0,
				"collected": false,
				"phase": randf() * TAU
			}
		)
		_play_sfx("impact")
		if bool(enemy.get("boss", false)):
			_begin_mommy_transition()
			return
		if _alive_enemy_count() == 0:
			extract_ready = true
		_save_career()


func _begin_mommy_transition() -> void:
	if game_state != "playing" or level_index != DEVIL_LEVEL_INDEX:
		return
	game_state = "transition"
	transition_time_left = 1.15
	alarm_player.stop()
	_stop_level3_audio()
	transition_overlay.visible = true


func _damage_player(amount: float) -> void:
	if player_dead or game_state != "playing":
		return
	player_health = maxf(0.0, player_health - amount)
	player_damage_flash = 0.20
	_play_sfx("impact")
	if player_health <= 0.0:
		player_dead = true
		player_anim = "death"
		_play_sfx("failure")
		_end_game(false, "OPERATIVE ELIMINATED BY HOSTILE FORCES")


func _update_cameras(delta: float) -> void:
	if level_index == DEVIL_LEVEL_INDEX:
		return
	for camera in cameras:
		camera.phase = float(camera.phase) + 1.3 * delta
		camera.angle = float(camera.base_angle) + 0.65 * sin(float(camera.phase))
		if (
			not camera.triggered
			and not player_hidden
			and _vision_contains(
				camera.pos, camera.angle, deg_to_rad(65.0), 230.0, player_position, 16
			)
			and _has_line_of_sight(camera.pos, player_position)
		):
			camera.triggered = true
			_trigger_alarm()


func _trigger_alarm() -> void:
	if alarm_active:
		return
	alarm_active = true
	alarm_timer = alarm_seconds
	alarm_player.stream = sound_streams["alarm"]
	alarm_player.play()


func _update_collectibles(delta: float) -> void:
	for item in collectibles:
		if item.collected:
			continue
		item.phase = float(item.phase) + 4.5 * delta
		var radius := 10.0 * (1.0 + 0.18 * sin(float(item.phase)))
		if _bresenham_contact(player_position, PLAYER_RADIUS, item.pos, radius):
			item.collected = true
			if item.medkit:
				player_health = minf(100.0, player_health + float(item.value))
				_play_sfx("heal")
			else:
				score += int(item.value)
				session_coins += 1
				career_coins += 1
				career_score += int(item.value)
				_play_sfx("coin")
				_save_career()


func _first_obstacle_hit(from: Vector2, to: Vector2) -> Dictionary:
	var best_distance := INF
	var best_point := to
	var hit := false
	for rect in walls + boxes:
		var result := CG.clip_line_cohen_sutherland(from, to, rect)
		if result.hit:
			var distance := from.distance_to(result.from)
			if distance < best_distance:
				best_distance = distance
				best_point = result.from
				hit = true
	for door in doors:
		if float(door.progress) >= 0.75:
			continue
		var segment := _door_segment(door)
		var direction: Vector2 = segment[1] - segment[0]
		var thickness := Vector2(2.5, 2.5)
		var rect := Rect2(
			Vector2(minf(segment[0].x, segment[1].x), minf(segment[0].y, segment[1].y)) - thickness,
			Vector2(absf(direction.x), absf(direction.y)) + thickness * 2.0
		)
		var result := CG.clip_line_cohen_sutherland(from, to, rect)
		if result.hit:
			var distance := from.distance_to(result.from)
			if distance < best_distance:
				best_distance = distance
				best_point = result.from
				hit = true
	return {"hit": hit, "point": best_point}


func _has_line_of_sight(from: Vector2, to: Vector2) -> bool:
	return not bool(_first_obstacle_hit(from, to).hit)


func _vision_polygon(
	origin: Vector2, angle: float, fov: float, distance: float, steps: int, color: Color
) -> void:
	var points := PackedVector2Array([origin])
	for index in range(steps + 1):
		var ray_angle := angle - fov * 0.5 + fov * float(index) / float(steps)
		var end_point := origin + Vector2(cos(ray_angle), sin(ray_angle)) * distance
		var hit := _first_obstacle_hit(origin, end_point)
		points.append(hit.point if hit.hit else end_point)
	var bounds := Rect2(
		ORIGIN + Vector2(WALL_THICKNESS, WALL_THICKNESS),
		world_size - Vector2(WALL_THICKNESS * 2.0, WALL_THICKNESS * 2.0)
	)
	var clipped := CG.clip_polygon_aabb(points, bounds)
	if clipped.size() >= 3:
		draw_colored_polygon(clipped, color)


func _exit_reached() -> bool:
	if level_index == MOMMY_LEVEL_INDEX:
		for door in doors:
			if (
				bool(door.get("glass", false))
				and int(door.get("room_a", -1)) == 8
				and int(door.get("room_b", -1)) == 8
				and not bool(door.get("broken", false))
				and float(door.get("progress", 0.0)) < 0.75
			):
				return false
	var closest := Vector2(
		clampf(player_position.x, exit_rect.position.x, exit_rect.end.x),
		clampf(player_position.y, exit_rect.position.y, exit_rect.end.y)
	)
	return player_position.distance_to(closest) <= PLAYER_RADIUS


func _alive_enemy_count() -> int:
	var count := 0
	for enemy in enemies:
		if enemy.alive:
			count += 1
	return count


func _win(clean: bool, targets_left: int) -> void:
	if game_state != "playing":
		return
	game_state = "victory"
	alarm_player.stop()
	_stop_level3_audio()
	if clean:
		score += 1000
	else:
		score += 300
	carried_score = score
	career_score = maxi(career_score, score)
	if level_index == 0:
		level2_unlocked = true
	_play_sfx("victory")
	_save_career()
	result_title.text = "LEVEL COMPLETE!" if level_index == 0 else "MISSION COMPLETE!"
	if level_index == MOMMY_LEVEL_INDEX:
		result_summary.text = "YOU SURVIVED THE NIGHTMARE"
	else:
		result_summary.text = (
			"ALL TARGETS NEUTRALIZED / EXTRACTION SUCCESSFUL"
			if clean
			else "EXTRACTION SUCCESSFUL / %d TARGET(S) STILL ACTIVE" % targets_left
		)
	result_next_button.visible = level_index < 2


func _end_game(_unused: bool, reason: String) -> void:
	if game_state != "playing":
		return
	game_state = "game_over"
	mommy_restart_time_left = MOMMY_RESTART_DELAY if level_index == MOMMY_LEVEL_INDEX else 0.0
	alarm_player.stop()
	_stop_level3_audio()
	if level_index == 0:
		level2_unlocked = false
	_play_sfx("failure")
	result_title.text = "MISSION FAILED!"
	result_summary.text = reason
	result_next_button.visible = false


func _start_level(index: int, reset_score: bool = true) -> void:
	_stop_level3_audio()
	transition_overlay.visible = false
	transition_time_left = 0.0
	mommy_restart_time_left = 0.0
	if reset_score:
		if game_state == "menu" or index == 0:
			session_kills = 0
			session_coins = 0
		score = 0
		carried_score = 0
	elif index > 0:
		score = carried_score
	_build_level(index)
	game_state = "playing"
	if level_index == MOMMY_LEVEL_INDEX:
		_start_level3_audio()


func _continue_level() -> void:
	if game_state == "victory" and level_index < 2:
		_start_level(level_index + 1, false)


func _retry_level() -> void:
	session_kills = 0
	session_coins = 0
	carried_score = 0
	_start_level(level_index, true)


func _show_menu() -> void:
	game_state = "menu"
	alarm_player.stop()
	_stop_level3_audio()
	_build_level(0)


func _load_career() -> void:
	var config := ConfigFile.new()
	if config.load("user://career.cfg") == OK:
		career_score = int(config.get_value("career", "score", 0))
		career_coins = int(config.get_value("career", "coins", 0))
		career_kills = int(config.get_value("career", "kills", 0))


func _save_career() -> void:
	var config := ConfigFile.new()
	config.set_value("career", "score", career_score)
	config.set_value("career", "coins", career_coins)
	config.set_value("career", "kills", career_kills)
	var error := config.save("user://career.cfg")
	if error != OK:
		push_error("Could not save career statistics: %s" % error_string(error))


func _run_math_checks() -> void:
	assert(CG.rotate_points([Vector2.RIGHT], PI * 0.5)[0].distance_to(Vector2.DOWN) < 0.001)
	assert(CG.clip_line_cohen_sutherland(Vector2(-5, 5), Vector2(15, 5), Rect2(0, 0, 10, 10)).hit)
	assert(CG.bresenham_circle(Vector2i.ZERO, 3).has(Vector2i(0, 3)))
	assert(
		CG.point_in_polygon(
			Vector2(2, 2),
			PackedVector2Array([Vector2(0, 0), Vector2(4, 0), Vector2(4, 4), Vector2(0, 4)])
		)
	)
	_validate_catalog_walkability()
	_build_level(0)


func _validate_catalog_walkability() -> void:
	for index in range(MOMMY_LEVEL_INDEX + 1):
		_build_level(index)
		assert(
			not _blocked_by_static_geometry(player_position, PLAYER_RADIUS),
			"%s player spawn intersects a wall or crate" % level_name
		)
		if index < DEVIL_LEVEL_INDEX:
			assert(
				not _blocked_by_static_geometry(exit_rect.get_center(), 8.0),
				"%s extraction pad intersects a wall or crate" % level_name
			)
		for enemy in enemies:
			for waypoint in enemy.path:
				assert(
					not _blocked_by_static_geometry(waypoint, PLAYER_RADIUS),
					"%s patrol waypoint intersects a wall or crate" % level_name
				)
		for spot in hide_spots:
			assert(
				not _blocked_by_static_geometry(spot.pos, PLAYER_RADIUS),
				"%s hiding spot intersects a wall or crate" % level_name
			)
		for item in collectibles:
			assert(
				not _blocked_by_static_geometry(item.pos, 0.0),
				"%s collectible center is inside a wall or crate" % level_name
			)


func _blocked_by_static_geometry(point: Vector2, radius: float) -> bool:
	for rect in walls + boxes:
		if _circle_rect(point, radius, rect):
			return true
	return false


func _draw() -> void:
	var room := Rect2(ORIGIN, world_size)
	draw_rect(room, Color("#0a101b"))
	var floor_texture: Texture2D = textures.get("Tiles/floor_surface_full.png")
	var interior := Rect2(
		ORIGIN + Vector2(WALL_THICKNESS, WALL_THICKNESS),
		world_size - Vector2(WALL_THICKNESS * 2.0, WALL_THICKNESS * 2.0)
	)
	if floor_texture:
		draw_texture_rect(floor_texture, interior, false)
		draw_rect(interior, Color(0.04, 0.045, 0.05, 0.34))
	if level_index == MOMMY_LEVEL_INDEX:
		_draw_house_room_floor()
	draw_rect(room, Color("#0d1522"), false, 2.0)
	_draw_ambient_lights()
	for camera in cameras:
		var tint := (
			Color(1.0, 0.23, 0.25, 0.34) if camera.triggered else Color(0.28, 0.82, 1.0, 0.24)
		)
		_vision_polygon(camera.pos, camera.angle, deg_to_rad(65.0), 230.0, 24, tint)
	for enemy in enemies:
		if not enemy.alive or bool(enemy.get("mommy", false)):
			continue
		var is_boss: bool = bool(enemy.get("boss", false))
		var hp_frac: float = float(enemy.health) / float(BOSS_MAX_HITS) if is_boss else 1.0
		var cone_range := (
			(270.0 if hp_frac <= 0.33 else (240.0 if hp_frac <= 0.66 else 200.0))
			if is_boss
			else ((ENFORCER_CONE_RANGE if enemy.shielded else GUARD_CONE_RANGE) * (1.25 if alarm_active else 1.0))
		)
		var cone_fov: float = deg_to_rad(78.0) if is_boss else GUARD_CONE_FOV
		var tint := (
			Color(1.0, 0.18, 0.18, 0.32)
			if enemy.alert
			else (Color(0.35, 1.0, 0.55, 0.28) if enemy.shielded else (Color(1.0, 0.45, 0.2, 0.25) if is_boss else Color(1.0, 0.76, 0.28, 0.22)))
		)
		_vision_polygon(
			enemy.pos + Vector2(cos(enemy.angle), sin(enemy.angle)) * (28.0 if is_boss else 14.0),
			enemy.angle,
			cone_fov,
			cone_range,
			28,
			tint
		)
	_draw_player_flashlight()
	if level_index < DEVIL_LEVEL_INDEX or level_index == MOMMY_LEVEL_INDEX:
		_draw_exit()
	_draw_props()
	_draw_obstacles()
	_draw_hide_spots()
	_draw_doors()
	_draw_collectibles()
	_draw_cameras()
	_draw_enemies()
	_draw_active_lasers()
	_draw_player_bolts()
	_draw_enemy_bullets()
	_draw_player()
	_draw_hitboxes()


func _draw_house_room_floor() -> void:
	var rooms := [
		{
			"rect": Rect2(ORIGIN + Vector2(8, 8), Vector2(187, 105)),
			"name": "BEDROOM 1",
			"color": Color("#483b37")
		},
		{
			"rect": Rect2(ORIGIN + Vector2(208, 8), Vector2(195, 105)),
			"name": "BEDROOM 2",
			"color": Color("#483b37")
		},
		{
			"rect": Rect2(ORIGIN + Vector2(8, 128), Vector2(187, 132)),
			"name": "BEDROOM 3",
			"color": Color("#493b34")
		},
		{
			"rect": Rect2(ORIGIN + Vector2(208, 128), Vector2(195, 132)),
			"name": "BEDROOM 4",
			"color": Color("#493b34")
		},
		{
			"rect": Rect2(ORIGIN + Vector2(423, 8), Vector2(210, 105)),
			"name": "STORAGE",
			"color": Color("#38363c")
		},
		{
			"rect": Rect2(ORIGIN + Vector2(653, 8), Vector2(337, 135)),
			"name": "BATHROOM",
			"color": Color("#34434a")
		},
		{
			"rect": Rect2(ORIGIN + Vector2(653, 158), Vector2(337, 102)),
			"name": "LAUNDRY",
			"color": Color("#34434a")
		},
		{
			"rect": Rect2(ORIGIN + Vector2(8, 283), Vector2(395, 410)),
			"name": "LIVING ROOM",
			"color": Color("#3c322f")
		},
		{
			"rect": Rect2(ORIGIN + Vector2(423, 128), Vector2(210, 565)),
			"name": "CENTRAL HALL",
			"color": Color("#3b3030")
		},
		{
			"rect": Rect2(ORIGIN + Vector2(653, 283), Vector2(337, 410)),
			"name": "KITCHEN / DINING",
			"color": Color("#3b4140")
		}
	]
	for room in rooms:
		var rect: Rect2 = room.rect
		draw_rect(rect, room.color)
		draw_rect(rect, Color(0.87, 0.7, 0.52, 0.25), false, 2.0)
		if room.name in ["KITCHEN / DINING", "BATHROOM", "LAUNDRY"]:
			for x in range(int(rect.position.x) + 24, int(rect.end.x), 34):
				draw_line(
					Vector2(x, rect.position.y),
					Vector2(x, rect.end.y),
					Color(0.75, 0.82, 0.8, 0.12),
					1.0
				)
			for y in range(int(rect.position.y) + 24, int(rect.end.y), 34):
				draw_line(
					Vector2(rect.position.x, y),
					Vector2(rect.end.x, y),
					Color(0.75, 0.82, 0.8, 0.12),
					1.0
				)
		else:
			for x in range(int(rect.position.x) + 22, int(rect.end.x), 42):
				draw_line(
					Vector2(x, rect.position.y + 4.0),
					Vector2(x, rect.end.y - 4.0),
					Color(0.13, 0.1, 0.1, 0.12),
					1.0
				)
		draw_string(
			ThemeDB.fallback_font,
			rect.position + Vector2(12.0, 22.0),
			String(room.name),
			HORIZONTAL_ALIGNMENT_LEFT,
			-1,
			11,
			Color(0.94, 0.82, 0.67, 0.62)
		)


func _draw_exit() -> void:
	var ready := extract_ready or alarm_active
	var color := Color(0.08, 0.9, 0.55, 0.35) if ready else Color(0.1, 0.62, 0.85, 0.22)
	draw_rect(exit_rect, color)
	draw_rect(
		exit_rect,
		Color(0.18, 0.95, 0.65, 0.85) if ready else Color(0.25, 0.8, 1.0, 0.7),
		false,
		2.0
	)
	var pad: Texture2D = textures.get("Environment/exit_pad.png")
	if pad:
		draw_texture_rect(
			pad, Rect2(exit_rect.position, exit_rect.size), false, Color(1, 1, 1, 0.8)
		)
	draw_string(
		ThemeDB.fallback_font,
		exit_rect.position + Vector2(8, 22),
		"EXIT",
		HORIZONTAL_ALIGNMENT_LEFT,
		-1,
		12,
		Color.WHITE
	)


func _draw_obstacles() -> void:
	_draw_wall_art()
	for rect in walls:
		var wall_color := Color("#514548") if level_index == MOMMY_LEVEL_INDEX else Color("#334255")
		var edge_color := Color("#9a7772") if level_index == MOMMY_LEVEL_INDEX else Color("#68788b")
		draw_rect(rect, wall_color)
		draw_rect(rect, edge_color, false, 1.0)
	if level_index == MOMMY_LEVEL_INDEX:
		_draw_house_furniture()
		return
	for index in range(boxes.size()):
		var rect := boxes[index]
		draw_rect(Rect2(rect.position + Vector2(6, -8), rect.size * 1.08), Color(0, 0, 0, 0.5))
		draw_rect(rect, Color("#34404c"))
		var half_index := int(index / 2)
		var sprite_index := half_index if index % 2 == 1 else 3 + half_index
		var crate: Texture2D = textures.get("Environment/crate_unique_%d.png" % sprite_index)
		if crate:
			var inset := rect.size * 0.03
			draw_texture_rect(crate, Rect2(rect.position + inset, rect.size - inset * 2.0), false)
		else:
			draw_rect(rect, Color("#8c7252"), false, 3.0)
			draw_line(
				rect.position + Vector2(9, 9), rect.end - Vector2(9, 9), Color("#886746"), 4.0
			)
			draw_line(
				Vector2(rect.position.x + 9, rect.end.y - 9),
				Vector2(rect.end.x - 9, rect.position.y + 9),
				Color("#886746"),
				4.0
			)


func _draw_house_furniture() -> void:
	for furniture in house_furniture:
		var rect: Rect2 = furniture.rect
		var name := String(furniture.name)
		draw_rect(Rect2(rect.position + Vector2(6.0, 8.0), rect.size), Color(0.0, 0.0, 0.0, 0.42))
		match name:
			"BED":
				draw_rect(rect, Color("#563f35"))
				draw_rect(rect.grow(-8.0), Color("#b8a187"))
				draw_rect(
					Rect2(rect.position + Vector2(12, 34), Vector2(rect.size.x - 24, 58)),
					Color("#74675c")
				)
				draw_rect(Rect2(rect.position + Vector2(16, 12), Vector2(54, 28)), Color("#e0d5c2"))
				draw_rect(Rect2(rect.position + Vector2(82, 12), Vector2(54, 28)), Color("#e0d5c2"))
			"DESK":
				draw_rect(rect, Color("#594234"))
				draw_rect(rect.grow(-4.0), Color("#9a7354"))
				draw_rect(Rect2(rect.position + Vector2(8, 5), Vector2(18, 12)), Color("#343d43"))
			"WARDROBE":
				draw_rect(rect, Color("#624c3d"))
				draw_rect(rect.grow(-4.0), Color("#927258"), false, 3.0)
				draw_line(
					Vector2(rect.get_center().x, rect.position.y + 4.0),
					Vector2(rect.get_center().x, rect.end.y - 4.0),
					Color("#4a382e"),
					3.0
				)
			"CLUTTER":
				draw_rect(rect, Color("#38383b"))
				for offset in [
					Vector2(12, 12),
					Vector2(50, 20),
					Vector2(85, 10),
					Vector2(130, 24),
					Vector2(33, 48),
					Vector2(105, 55),
					Vector2(155, 50)
				]:
					draw_rect(Rect2(rect.position + offset, Vector2(22, 16)), Color("#75685c"))
			"TUB":
				draw_rect(rect, Color("#aab8b7"), false, 5.0)
				draw_rect(rect.grow(-7.0), Color("#74a6ad"))
				draw_arc(rect.get_center(), 18.0, 0.0, TAU, 24, Color("#d0e4e0"), 2.0)
			"TOILET":
				draw_rect(Rect2(rect.position + Vector2(12, 2), Vector2(24, 20)), Color("#d4dfdc"))
				draw_circle(rect.get_center(), 16.0, Color("#e0e5df"))
			"SINK":
				draw_rect(rect, Color("#bdc7c2"))
				draw_rect(rect.grow(-7.0), Color("#61777a"))
				draw_arc(rect.get_center(), 10.0, 0.0, TAU, 20, Color("#c8dbd5"), 2.0)
			"FIREPLACE":
				draw_rect(rect, Color("#4f3b35"))
				draw_rect(rect.grow(-7.0), Color("#25232a"))
				draw_rect(
					Rect2(rect.position + Vector2(20, 16), Vector2(rect.size.x - 40, 17)),
					Color("#f58e37")
				)
				draw_circle(rect.get_center(), 9.0, Color("#ffd36b"))
			"CLOCK":
				draw_rect(rect, Color("#593f31"))
				draw_circle(rect.get_center(), 12.0, Color("#d8bf8d"))
				draw_line(
					rect.get_center(), rect.get_center() + Vector2(0, -8), Color("#4a372f"), 2.0
				)
				draw_line(
					rect.get_center(), rect.get_center() + Vector2(7, 1), Color("#4a372f"), 2.0
				)
			"COUNTER":
				draw_rect(rect, Color("#554a44"))
				draw_rect(rect.grow(-5.0), Color("#a19786"))
			"WASHING MACHINE":
				draw_rect(rect, Color("#a4a9a5"))
				draw_rect(rect, Color("#d0d1c9"), false, 3.0)
				draw_rect(
					Rect2(rect.position + Vector2(8, 7), Vector2(rect.size.x - 16, 12)),
					Color("#555d5e")
				)
				draw_circle(
					rect.position + Vector2(rect.size.x * 0.5, 47.0), 22.0, Color("#4b5a5d")
				)
				draw_arc(
					rect.position + Vector2(rect.size.x * 0.5, 47.0),
					17.0,
					0.0,
					TAU,
					24,
					Color("#b3d0d0"),
					3.0
				)
			"FRIDGE":
				draw_rect(rect, Color("#abb3b2"))
				draw_rect(rect, Color("#d2d8d3"), false, 3.0)
				draw_line(
					rect.position + Vector2(3, 48),
					Vector2(rect.end.x - 3, rect.position.y + 48),
					Color("#697778"),
					2.0
				)
				draw_line(
					rect.position + Vector2(rect.size.x - 11, 18),
					Vector2(rect.end.x - 11, rect.position.y + 40),
					Color("#626e6d"),
					3.0
				)
			"CLOSET":
				draw_rect(rect, Color("#624c3d"))
				draw_rect(rect, Color("#a18064"), false, 3.0)
				draw_line(
					Vector2(rect.get_center().x, rect.position.y),
					Vector2(rect.get_center().x, rect.end.y),
					Color("#4a382e"),
					3.0
				)
				draw_circle(rect.position + Vector2(32, 52), 3.0, Color("#d6bd89"))
				draw_circle(rect.position + Vector2(44, 52), 3.0, Color("#d6bd89"))
			"SOFA":
				draw_rect(rect, Color("#76534a"))
				draw_rect(rect.grow(-8.0), Color("#a6796b"))
				draw_line(
					Vector2(rect.position.x + rect.size.x * 0.5, rect.position.y + 8),
					Vector2(rect.position.x + rect.size.x * 0.5, rect.end.y - 8),
					Color("#d1a18b"),
					2.0
				)
			"DINING TABLE":
				draw_rect(rect, Color("#624a3a"))
				draw_rect(rect.grow(-6.0), Color("#9d7656"))
				draw_line(
					Vector2(rect.position.x + 15, rect.end.y - 4),
					Vector2(rect.position.x + 15, rect.end.y + 14),
					Color("#44372f"),
					5.0
				)
				draw_line(
					Vector2(rect.end.x - 15, rect.end.y - 4),
					Vector2(rect.end.x - 15, rect.end.y + 14),
					Color("#44372f"),
					5.0
				)


func _draw_hide_spots() -> void:
	for index in range(hide_spots.size()):
		var spot: Dictionary = hide_spots[index]
		var pos: Vector2 = spot.pos
		var active := player_hidden and hidden_spot_index == index
		if level_index == MOMMY_LEVEL_INDEX:
			draw_circle(pos, 24.0, Color(0.22, 0.53, 0.38, 0.22))
			draw_arc(pos, 24.0, 0.0, TAU, 24, Color("#b5f5bb") if active else Color("#86bf8b"), 2.0)
			draw_string(
				ThemeDB.fallback_font,
				pos + Vector2(-55.0, 40.0),
				"IN " + String(spot.label) if active else "HIDE: " + String(spot.label),
				HORIZONTAL_ALIGNMENT_LEFT,
				140.0,
				10,
				Color("#eef2d5")
			)
			continue
		draw_circle(pos, 27.0, Color(0.14, 0.24, 0.2, 0.68))
		draw_arc(
			pos,
			23.0,
			0.0,
			TAU,
			24,
			Color(0.45, 0.76, 0.59, 0.85) if active else Color(0.49, 0.57, 0.49, 0.5),
			2.0
		)
		var cover := Color("#414a4a")
		var cover_edge := Color("#78817a")
		draw_rect(Rect2(pos + Vector2(-29.0, -31.0), Vector2(58.0, 9.0)), cover)
		draw_rect(Rect2(pos + Vector2(-29.0, -31.0), Vector2(58.0, 9.0)), cover_edge, false, 1.5)
		for side in [-1.0, 1.0]:
			var side_rect := Rect2(pos + Vector2(20.0 * side, -26.0), Vector2(9.0, 22.0))
			if side < 0.0:
				side_rect.position.x -= 9.0
			draw_rect(side_rect, cover)
			draw_rect(side_rect, cover_edge, false, 1.5)
		draw_string(
			ThemeDB.fallback_font,
			pos + Vector2(-18.0, 39.0),
			"CLICK TO EXIT" if active else "CLICK TO HIDE",
			HORIZONTAL_ALIGNMENT_LEFT,
			-1,
			10,
			Color("#c2c5ae")
		)


func _draw_wall_art() -> void:
	var ox := ORIGIN.x
	var oy := ORIGIN.y
	var width := world_size.x
	var height := world_size.y
	var outer := 32.0
	var wall_texture: Texture2D = textures.get("Tiles/wall.png")
	var bounds := [
		Rect2(Vector2(ox - outer, oy - outer), Vector2(width + outer * 2.0, outer + WALL_THICKNESS))
	]
	if level_index == MOMMY_LEVEL_INDEX:
		bounds.append(
			Rect2(
				Vector2(ox - outer, oy + height - WALL_THICKNESS),
				Vector2(outer + 455.0, outer + WALL_THICKNESS)
			)
		)
		bounds.append(
			Rect2(
				Vector2(ox + 545.0, oy + height - WALL_THICKNESS),
				Vector2(width - 545.0 + outer, outer + WALL_THICKNESS)
			)
		)
	else:
		bounds.append(
			Rect2(
				Vector2(ox - outer, oy + height - WALL_THICKNESS),
				Vector2(width + outer * 2.0, outer + WALL_THICKNESS)
			)
		)
	bounds.append(
		Rect2(
			Vector2(ox - outer, oy + WALL_THICKNESS),
			Vector2(outer + WALL_THICKNESS, height - WALL_THICKNESS * 2.0)
		)
	)
	bounds.append(
		Rect2(
			Vector2(ox + width - WALL_THICKNESS, oy + WALL_THICKNESS),
			Vector2(outer + WALL_THICKNESS, height - WALL_THICKNESS * 2.0)
		)
	)
	for rect in bounds:
		if wall_texture:
			draw_texture_rect(wall_texture, rect, true)
		else:
			draw_rect(rect, Color("#334255"))
	if level_index == MOMMY_LEVEL_INDEX:
		return
	var hazard: Texture2D = textures.get("Tiles/hazard.png")
	if hazard:
		var inset := WALL_THICKNESS + 3.0
		draw_texture_rect(
			hazard,
			Rect2(Vector2(ox + inset, oy + inset), Vector2(width - inset * 2.0, 5.0)),
			true,
			Color(1, 1, 1, 0.8)
		)
		draw_texture_rect(
			hazard,
			Rect2(
				Vector2(ox + inset, oy + height - inset - 5.0), Vector2(width - inset * 2.0, 5.0)
			),
			true,
			Color(1, 1, 1, 0.8)
		)
		draw_texture_rect(
			hazard,
			Rect2(Vector2(ox + inset, oy + inset), Vector2(5.0, height - inset * 2.0)),
			true,
			Color(1, 1, 1, 0.8)
		)
		draw_texture_rect(
			hazard,
			Rect2(
				Vector2(ox + width - inset - 5.0, oy + inset), Vector2(5.0, height - inset * 2.0)
			),
			true,
			Color(1, 1, 1, 0.8)
		)


func _draw_ambient_lights() -> void:
	var glow: Texture2D = textures.get("FX/glow.png")
	var fixture: Texture2D = textures.get("Environment/wall_light.png")
	if level_index == MOMMY_LEVEL_INDEX:
		if glow:
			for position in [
				ORIGIN + Vector2(210, 150),
				ORIGIN + Vector2(800, 150),
				ORIGIN + Vector2(200, 470),
				ORIGIN + Vector2(800, 470)
			]:
				draw_texture_rect(
					glow,
					Rect2(position - Vector2(100, 100), Vector2(200, 200)),
					false,
					Color("#edaa72")
				)
		return
	if glow:
		var uses_level_two_layout := level_index in [1, DEVIL_LEVEL_INDEX]
		var columns := 4 if uses_level_two_layout else 3
		var rows := 3 if uses_level_two_layout else 2
		var passage := 88.0 if uses_level_two_layout else 100.0
		var box_size := 110.0 if uses_level_two_layout else 120.0
		for column in range(columns + 1):
			for row in range(rows + 1):
				var crossing := (
					ORIGIN
					+ Vector2(
						WALL_THICKNESS + passage * 0.5 + column * (box_size + passage),
						WALL_THICKNESS + passage * 0.5 + row * (box_size + passage)
					)
				)
				draw_texture_rect(
					glow,
					Rect2(crossing - Vector2.ONE * passage * 1.2, Vector2.ONE * passage * 2.4),
					false,
					Color(0.46, 0.52, 0.53, 0.045)
				)
	if not fixture:
		return
	for index in range(10):
		var x := ORIGIN.x + world_size.x * (float(index) + 0.5) / 10.0
		_draw_texture_actor(
			fixture, Vector2(x, ORIGIN.y + WALL_THICKNESS + 14.0), 0.0, Vector2(26, 26), Color.WHITE
		)
		_draw_texture_actor(
			fixture,
			Vector2(x, ORIGIN.y + world_size.y - WALL_THICKNESS - 14.0),
			PI,
			Vector2(26, 26),
			Color.WHITE
		)
	for index in range(7):
		var y := ORIGIN.y + world_size.y * (float(index) + 0.5) / 7.0
		_draw_texture_actor(
			fixture,
			Vector2(ORIGIN.x + WALL_THICKNESS + 14.0, y),
			-PI * 0.5,
			Vector2(26, 26),
			Color.WHITE
		)
		_draw_texture_actor(
			fixture,
			Vector2(ORIGIN.x + world_size.x - WALL_THICKNESS - 14.0, y),
			PI * 0.5,
			Vector2(26, 26),
			Color.WHITE
		)


func _draw_props() -> void:
	var width := world_size.x
	var height := world_size.y
	var uses_level_two_layout := level_index in [1, DEVIL_LEVEL_INDEX]
	var passage := 88.0 if uses_level_two_layout else 100.0
	var box_size := 110.0 if uses_level_two_layout else 120.0
	if level_index == MOMMY_LEVEL_INDEX:
		var plant: Texture2D = textures.get("Environment/plant.png")
		if plant:
			for position in [
				ORIGIN + Vector2(90, 235),
				ORIGIN + Vector2(380, 625),
				ORIGIN + Vector2(965, 230),
				ORIGIN + Vector2(965, 650)
			]:
				_draw_texture_actor(plant, position, 0.0, Vector2(38, 38), Color.WHITE)
		return
	var props := [
		[
			"Environment/plant.png",
			ORIGIN + Vector2(WALL_THICKNESS + 28, WALL_THICKNESS + 28),
			34.0,
			0.0
		],
		[
			"Environment/barrel.png",
			ORIGIN + Vector2(WALL_THICKNESS + 55, WALL_THICKNESS + 30),
			28.0,
			0.35
		],
		[
			"Environment/barrel.png",
			ORIGIN + Vector2(WALL_THICKNESS + 78, WALL_THICKNESS + 38),
			26.0,
			-0.26
		],
		[
			"Environment/console.png",
			(
				ORIGIN
				+ Vector2(
					WALL_THICKNESS + passage + box_size * 0.5, WALL_THICKNESS + passage * 0.35
				)
			),
			42.0,
			0.0
		],
		[
			"Environment/plant.png",
			(
				ORIGIN
				+ Vector2(WALL_THICKNESS + 2.0 * (box_size + passage) + 20.0, WALL_THICKNESS + 24.0)
			),
			32.0,
			0.0
		],
		[
			"Environment/barrel.png",
			ORIGIN + Vector2(WALL_THICKNESS + 2.5 * (box_size + passage), height * 0.5 - 40.0),
			28.0,
			0.7
		],
		[
			"Environment/plant.png",
			ORIGIN + Vector2(width - WALL_THICKNESS - 30.0, WALL_THICKNESS + 30.0),
			34.0,
			0.0
		],
		[
			"Environment/barrel.png",
			ORIGIN + Vector2(width - WALL_THICKNESS - 55.0, height - WALL_THICKNESS - 35.0),
			28.0,
			0.0
		],
		[
			"Environment/console.png",
			ORIGIN + Vector2(WALL_THICKNESS + passage * 0.4, height - WALL_THICKNESS - 40.0),
			40.0,
			PI * 0.5
		],
		[
			"Environment/plant.png",
			(
				ORIGIN
				+ Vector2(width - WALL_THICKNESS - passage * 0.5, height - WALL_THICKNESS - 28.0)
			),
			30.0,
			0.0
		]
	]
	for prop in props:
		var texture: Texture2D = textures.get(prop[0])
		if texture:
			var size := float(prop[2])
			draw_circle(prop[1] + Vector2(3, -3), size * 0.42, Color(0, 0, 0, 0.35))
			_draw_texture_actor(texture, prop[1], float(prop[3]), Vector2.ONE * size, Color.WHITE)


func _draw_doors() -> void:
	for door in doors:
		if bool(door.get("broken", false)):
			continue
		var segment := _door_segment(door)
		var color: Color = door.color
		var direction: Vector2 = segment[1] - segment[0]
		var midpoint := segment[0].lerp(segment[1], 0.5)
		var door_texture: Texture2D = textures.get("Tiles/door.png")
		var stripe_texture: Texture2D = textures.get("Tiles/door_stripe.png")
		if door_texture:
			_draw_texture_actor(
				door_texture,
				midpoint,
				direction.angle(),
				Vector2(maxf(1.0, direction.length()), 10.0),
				Color.WHITE
			)
		if stripe_texture:
			_draw_texture_actor(
				stripe_texture,
				midpoint,
				direction.angle(),
				Vector2(maxf(1.0, direction.length()), 3.0),
				color
			)
		draw_line(segment[0], segment[1], Color(color.r, color.g, color.b, 0.2), 12.0)
		draw_line(segment[0], segment[1], color, 2.0)
		if float(door.progress) < 0.75:
			var middle := segment[0].lerp(segment[1], 0.5)
			draw_circle(middle, 4.0, Color.WHITE)
	for debris in glass_debris:
		var pos: Vector2 = debris.pos
		for shard_index in range(7):
			var angle := float(shard_index) * TAU / 7.0
			var center := (
				pos + Vector2(cos(angle), sin(angle)) * (8.0 + float(shard_index % 3) * 5.0)
			)
			draw_colored_polygon(
				PackedVector2Array(
					[
						center + Vector2(-3.0, -2.0),
						center + Vector2(4.0, -1.0),
						center + Vector2(0.0, 4.0)
					]
				),
				Color(0.48, 0.84, 0.96, 0.78)
			)


func _draw_collectibles() -> void:
	for item in collectibles:
		if item.collected:
			continue
		var pulse := 1.0 + 0.18 * sin(float(item.phase))
		var pos: Vector2 = item.pos + Vector2(0, sin(float(item.phase) * 0.5) * 1.5)
		var color := (
			Color(0.25, 0.82, 1.0, 0.95)
			if item.get("diamond", false)
			else (Color(0.98, 0.74, 0.1, 0.9) if not item.medkit else Color(0.15, 0.9, 0.45, 0.95))
		)
		draw_circle(pos, 17.0 * pulse, Color(color.r, color.g, color.b, 0.12))
		if item.get("diamond", false):
			var diamond := PackedVector2Array(
				[
					pos + Vector2(0.0, -11.0 * pulse),
					pos + Vector2(8.0 * pulse, 0.0),
					pos + Vector2(0.0, 12.0 * pulse),
					pos + Vector2(-8.0 * pulse, 0.0)
				]
			)
			draw_colored_polygon(diamond, Color("#66d9ff"))
			draw_polyline(
				PackedVector2Array([diamond[0], diamond[1], diamond[2], diamond[3], diamond[0]]),
				Color("#e3fbff"),
				1.5
			)
			draw_line(diamond[0], diamond[2], Color("#1688b5"), 1.0)
			continue
		var texture: Texture2D
		if item.medkit:
			texture = textures.get("Items/medkit.png")
		else:
			var frame := int(elapsed * 10.0) % 6
			texture = textures.get("Items/coin_%d.png" % frame)
		if texture:
			draw_texture_rect(
				texture,
				Rect2(pos - Vector2.ONE * 11.0 * pulse, Vector2.ONE * 22.0 * pulse),
				false,
				Color.WHITE
			)
		else:
			draw_circle(pos, 8.0 * pulse, color)


func _draw_cameras() -> void:
	var texture: Texture2D = textures.get("Environment/security_camera.png")
	for camera in cameras:
		draw_circle(camera.pos, 13.0, Color("#172334"))
		draw_circle(camera.pos, 7.0, Color("#78dff2"))
		if texture:
			_draw_texture_actor(texture, camera.pos, camera.angle, Vector2(25, 25), Color.WHITE)
		var led_color := Color(1.0, 0.2, 0.2) if camera.triggered else Color(0.2, 1.0, 0.65)
		draw_circle(
			camera.pos + Vector2(cos(camera.angle), sin(camera.angle)) * 7.0,
			3.0 + 1.2 * absf(sin(elapsed * 5.0)),
			led_color
		)


func _draw_enemies() -> void:
	for enemy in enemies:
		if not enemy.alive:
			continue
		if (
			bool(enemy.get("boss", false))
			and float(enemy.get("boss_relocate_timer", 0.0)) > 0.0
			and int(elapsed * 12.0) % 2 == 1
		):
			continue
		if bool(enemy.get("mommy", false)):
			draw_circle(enemy.pos + Vector2(0.0, 34.0), 34.0, Color(0.0, 0.0, 0.0, 0.48))
			if enemy.alert:
				draw_circle(
					enemy.pos, 66.0 + 4.0 * sin(elapsed * 5.0), Color(0.5, 0.02, 0.035, 0.11)
				)
			var mommy_state := String(enemy.anim)
			var mommy_frames: Array = art_frames.get("mommy/%s" % mommy_state, [])
			if mommy_frames.is_empty():
				mommy_frames = art_frames.get("mommy/idle", [])
			if not mommy_frames.is_empty():
				var mommy_fps := 8.0 if mommy_state == "idle" else 10.0
				var mommy_frame := (
					int(float(enemy.anim_time) * mommy_fps) % mommy_frames.size()
					if mommy_state in ["idle", "walk"]
					else mini(int(float(enemy.anim_time) * mommy_fps), mommy_frames.size() - 1)
				)
				var bob := sin(elapsed * 3.5) * 2.5
				var tint := Color("#ff7777") if enemy.alert else Color.WHITE
				draw_texture_rect(
					mommy_frames[mommy_frame] as Texture2D,
					Rect2(enemy.pos + Vector2(-82.0, -78.0 + bob), Vector2(164.0, 164.0)),
					false,
					tint
				)
			else:
				_draw_actor_shape(enemy.pos, enemy.angle, Color("#c84c57"))
			continue
		var is_boss := bool(enemy.get("boss", false))
		var actor_kind := (
			"boss"
			if is_boss
			else ("enforcer" if enemy.shielded else "guard")
		)
		var state := String(enemy.anim)
		var texture := _get_enemy_frame(
			actor_kind, state, float(enemy.angle), float(enemy.anim_time)
		)
		var tint := Color(1.0, 0.45, 0.35) if float(enemy.flash) > 0.0 else Color.WHITE
		var shadow_tex: Texture2D = textures.get("FX/shadow_blob.png")

		if is_boss:
			var actor_scale := BOSS_RENDER_SCALE
			var hp_frac := float(enemy.health) / float(BOSS_MAX_HITS)
			var boss_phase := 1
			if hp_frac <= 0.33:
				boss_phase = 3
			elif hp_frac <= 0.66:
				boss_phase = 2
			
			var phase_tint := Color.WHITE
			var glow_alpha := 0.16
			if boss_phase == 2:
				phase_tint = Color(1.0, 0.78, 0.7) # Warm Pink, vents open
				glow_alpha = 0.30
			elif boss_phase == 3:
				phase_tint = Color(1.0, 0.6, 0.52) # Hot Red, final assault
				glow_alpha = 0.40
				
			var boss_tint := Color(1.0, 0.45, 0.35) if float(enemy.flash) > 0.0 else phase_tint

			if shadow_tex:
				draw_texture_rect(
					shadow_tex,
					Rect2(enemy.pos + Vector2(-54.0 * actor_scale, -34.0 * actor_scale), Vector2(108.0, 68.0) * actor_scale),
					false,
					Color(0.0, 0.0, 0.0, 0.5)
				)
			else:
				draw_circle(enemy.pos, 38.0 * actor_scale, Color(0.0, 0.0, 0.0, 0.45))
				
			var glow_tex: Texture2D = textures.get("FX/glow.png")
			if glow_tex:
				var pulse := 0.5 + 0.5 * sin(elapsed * 5.0)
				var g_size := Vector2(80.0, 80.0) * actor_scale
				draw_texture_rect(
					glow_tex,
					Rect2(enemy.pos - g_size * 0.5, g_size),
					false,
					Color(1.0, 0.22, 0.08, glow_alpha * (0.75 + 0.25 * pulse))
				)

			if texture:
				# Unity boss.png head points UP (+Y), rotates by angle - PI*0.5
				draw_set_transform(enemy.pos, float(enemy.angle) - PI * 0.5, Vector2.ONE)
				draw_texture_rect(
					texture,
					Rect2(Vector2(-78.0, -58.0) * actor_scale, Vector2(156.0, 116.0) * actor_scale),
					false,
					boss_tint
				)
				draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
			else:
				_draw_actor_shape(enemy.pos, enemy.angle, Color("#e64352"))

			if float(enemy.get("telegraph_timer", 0.0)) > 0.0 and _has_line_of_sight(enemy.pos, player_position):
				var is_slam := bool(enemy.get("is_slam", false))
				var windup_total := float(enemy.get("windup", 0.64))
				var w_prog := 1.0 - clampf(float(enemy.telegraph_timer) / windup_total, 0.0, 1.0)
				var line_w := 8.0 if is_slam else (3.0 + 5.0 * w_prog)
				var line_col := Color(1.0, 0.85, 0.2, 0.9) if is_slam else Color(1.0, 0.35, 0.05, 0.8)
				draw_line(enemy.pos, player_position, line_col, line_w)

			for pip in range(BOSS_MAX_HITS):
				var pip_rect := Rect2(
					enemy.pos + Vector2(-66.0 + pip * 45.0, -110.0), Vector2(40.0, 10.0)
				)
				draw_rect(pip_rect, Color("#250f18"))
				if float(enemy.health) > float(pip):
					draw_rect(pip_rect, Color("#ff4d61") if boss_phase < 3 else Color("#ff2a42"))

			var boss_callout := "THE WARDEN - PHASE 1"
			if boss_phase == 2:
				boss_callout = "PHASE 2 — VENTS OPEN"
			elif boss_phase == 3:
				boss_callout = "PHASE 3 — FINAL ASSAULT"
			draw_string(
				ThemeDB.fallback_font,
				enemy.pos + Vector2(-75.0, -118.0),
				boss_callout,
				HORIZONTAL_ALIGNMENT_LEFT,
				160.0,
				11,
				Color("#ffe1de") if boss_phase == 1 else (Color("#ffb4a2") if boss_phase == 2 else Color("#ff6b6b"))
			)
			continue

		# Guard & Enforcer (from HunterAssassinUnity)
		if shadow_tex:
			draw_texture_rect(
				shadow_tex,
				Rect2(enemy.pos + Vector2(-26.0, -19.0), Vector2(52.0, 38.0)),
				false,
				Color(0.0, 0.0, 0.0, 0.45)
			)
		else:
			draw_circle(enemy.pos + Vector2(0.0, 4.0), 19.0, Color(0.0, 0.0, 0.0, 0.35))
		if texture:
			draw_set_transform(enemy.pos, float(enemy.angle), Vector2.ONE)
			draw_texture_rect(texture, Rect2(Vector2(-43.0, -43.0), Vector2(86.0, 86.0)), false, tint)
			draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		else:
			_draw_actor_shape(
				enemy.pos, enemy.angle, Color("#ec864c") if enemy.shielded else Color("#e64352")
			)
		if enemy.shielded:
			var shield_radius := ENFORCER_SHIELD_ARC_RADIUS + 5.0
			var facing_angle: float = float(enemy.angle)
			var start_ang: float = facing_angle - ENFORCER_SHIELD_HALF_ANGLE
			var end_ang: float = facing_angle + ENFORCER_SHIELD_HALF_ANGLE
			var shield_color := Color(0.25, 0.95, 0.9, 0.9)
			if float(enemy.shield_timer) > 0.0:
				shield_color = Color(1.0, 1.0, 1.0, 1.0)
			draw_arc(enemy.pos, shield_radius, start_ang, end_ang, 14, shield_color, 3.5)
			draw_arc(enemy.pos, shield_radius - 2.0, start_ang + 0.1, end_ang - 0.1, 12, Color(0.75, 1.0, 0.98, 0.8), 1.5)


func _draw_player() -> void:
	if player_hidden:
		return
	if player_dead:
		var dead_texture := _get_actor_frame(
			"player", "death", _animation_frame("player", "death", elapsed)
		)
		if dead_texture:
			_draw_player_texture(dead_texture, player_position, Vector2(60, 60), Color(0.45, 0.45, 0.45, 0.9))
		else:
			draw_circle(player_position, 12.0, Color("#286f72"))
		return
	var texture := _get_actor_frame(
		"player", player_anim, _animation_frame("player", player_anim, player_anim_time)
	)
	var hop := 0.0
	if player_is_jumping:
		var t := 1.0 - clampf(jump_timer / 0.38, 0.0, 1.0)
		hop = sin(t * PI) * JUMP_HOP_HEIGHT

	var shadow_tex: Texture2D = textures.get("FX/shadow_blob.png")
	if shadow_tex:
		var s := 1.0 - 0.35 * clampf(hop / JUMP_HOP_HEIGHT, 0.0, 1.0)
		draw_texture_rect(
			shadow_tex,
			Rect2(player_position + Vector2(-18.0 * s, -13.0 * s + 3.0), Vector2(36.0 * s, 26.0 * s)),
			false,
			Color(0.0, 0.0, 0.0, 0.45)
		)

	if sprint_noise:
		draw_arc(player_position, SPRINT_NOISE_RADIUS, 0.0, TAU, 64, Color(0.98, 0.8, 0.08, 0.22), 1.5)
	
	var player_tint := Color(1.0, 0.25, 0.25) if player_damage_flash > 0.0 else Color.WHITE
	if texture:
		_draw_player_texture(
			texture, player_position - Vector2(0, hop), Vector2(60, 60), player_tint
		)
	else:
		_draw_actor_shape(player_position - Vector2(0, hop), player_angle, Color("#10b981"))
	if melee_flash > 0.0:
		draw_arc(
			player_position + Vector2(cos(player_angle), sin(player_angle)) * 27.0,
			MELEE_RANGE * 0.48,
			player_angle - 0.8,
			player_angle + 0.8,
			18,
			Color(0.9, 0.85, 0.68, melee_flash / 0.18),
			3.0
		)


func _draw_player_flashlight() -> void:
	if game_state != "playing" or player_dead or player_hidden or level_index == MOMMY_LEVEL_INDEX:
		return
	_vision_polygon(player_position, player_angle, FLASHLIGHT_FOV, FLASHLIGHT_RANGE, 26, Color(1.0, 1.0, 0.85, 0.12))
	var forward := Vector2(cos(player_angle), sin(player_angle))
	draw_circle(player_position + forward * 10.0, 4.0, Color(1.0, 1.0, 0.85, 0.35))


func _draw_active_lasers() -> void:
	for laser in active_lasers:
		var alpha: float = clampf(float(laser.timer) / 0.12, 0.0, 1.0)
		var col: Color = laser.color
		var core_col: Color = laser.core
		draw_line(laser.from, laser.to, Color(col.r, col.g, col.b, col.a * alpha), 7.0)
		draw_line(laser.from, laser.to, Color(core_col.r, core_col.g, core_col.b, alpha), 1.8)


func _draw_player_bolts() -> void:
	for bolt in player_bolts:
		var direction: Vector2 = Vector2(bolt.velocity).normalized()
		draw_line(bolt.pos - direction * 14.0, bolt.pos + direction * 4.0, Color(1.0, 0.1, 0.15, 0.45), 10.0)
		draw_line(bolt.pos - direction * 10.0, bolt.pos + direction * 3.0, Color(1.0, 0.55, 0.45), 3.2)
		draw_circle(bolt.pos, 4.0, Color(1.0, 0.2, 0.25, 0.9))
		draw_circle(bolt.pos, 2.0, Color(1.0, 0.85, 0.85))


func _draw_player_texture(
	texture: Texture2D, position: Vector2, size: Vector2, tint: Color
) -> void:
	draw_set_transform(position, player_angle, Vector2.ONE)
	draw_texture_rect(texture, Rect2(-size * 0.5, size), false, tint)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _draw_enemy_bullets() -> void:
	for bullet in enemy_bullets:
		var direction: Vector2 = Vector2(bullet.velocity).normalized()
		var color := Color("#ff654f") if bullet.shielded else Color("#ffc15a")
		draw_line(
			bullet.pos - direction * 12.0,
			bullet.pos + direction * 4.0,
			Color(color.r, color.g, color.b, 0.6),
			7.0
		)
		draw_circle(bullet.pos, 5.0, color)
		draw_circle(bullet.pos, 2.0, Color("#fff5d7"))


func _get_enemy_frame(kind: String, state: String, angle: float, time: float) -> Texture2D:
	return _get_actor_frame(kind, state, _animation_frame(kind, state, time))


func _direction_name(angle: float) -> String:
	var direction := Vector2.RIGHT.rotated(angle)
	if absf(direction.x) > absf(direction.y):
		return "right" if direction.x > 0.0 else "left"
	return "front" if direction.y > 0.0 else "back"


func _draw_actor_shape(position: Vector2, angle: float, color: Color) -> void:
	var local := PackedVector2Array(
		[Vector2(16, 0), Vector2(-12, -11), Vector2(-6, 0), Vector2(-12, 11)]
	)
	var points := PackedVector2Array()
	for point in local:
		points.append(position + point.rotated(angle))
	draw_colored_polygon(points, color)
	draw_polyline(
		PackedVector2Array([points[0], points[1], points[2], points[3], points[0]]),
		Color(0.88, 0.96, 1.0, 0.9),
		1.2
	)


func _draw_texture_actor(
	texture: Texture2D, position: Vector2, angle: float, size: Vector2, tint: Color
) -> void:
	draw_set_transform(position, angle, Vector2.ONE)
	draw_texture_rect(texture, Rect2(-size * 0.5, size), false, tint)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _draw_hitboxes() -> void:
	if not debug_overlay:
		return
	var points := CG.bresenham_circle(
		Vector2i(int(player_position.x), int(player_position.y)), int(PLAYER_RADIUS)
	)
	for point in points:
		draw_circle(Vector2(point), 1.0, Color("#38bdf8"))
	var player_body := PackedVector2Array(
		[
			player_position + Vector2(16, 0).rotated(player_angle),
			player_position + Vector2(-12, -11).rotated(player_angle),
			player_position + Vector2(-6, 0).rotated(player_angle),
			player_position + Vector2(-12, 11).rotated(player_angle)
		]
	)
	draw_polyline(
		PackedVector2Array(
			[player_body[0], player_body[1], player_body[2], player_body[3], player_body[0]]
		),
		Color.CYAN,
		1.0
	)


func _animation_frame(kind: String, state: String, time: float) -> int:
	var frames: Array = art_frames.get("%s/%s" % [kind, state], [])
	if frames.is_empty():
		return 0
	var fps := 16.0 if kind == "player" and state == "attack" else 10.0
	if state not in ["idle", "walk", "run", "attack", "alert"]:
		fps = 8.0
	if state in ["idle", "walk", "run"]:
		return int(time * fps) % frames.size()
	return mini(int(time * fps), frames.size() - 1)


func _get_actor_frame(kind: String, state: String, index: int) -> Texture2D:
	var frames: Array = art_frames.get("%s/%s" % [kind, state], [])
	if frames.is_empty() and state == "alert":
		frames = art_frames.get("%s/idle" % kind, [])
	return frames[index % frames.size()] if not frames.is_empty() else null


func _build_ui() -> void:
	ui_layer = CanvasLayer.new()
	add_child(ui_layer)
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_PASS
	ui_layer.add_child(root)
	menu_overlay = ColorRect.new()
	menu_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	menu_overlay.color = Color(0.02, 0.035, 0.07, 0.86)
	menu_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(menu_overlay)
	hud_panel = PanelContainer.new()
	hud_panel.anchor_right = 1.0
	hud_panel.offset_bottom = 48.0
	hud_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.04, 0.07, 0.12, 0.96)))
	root.add_child(hud_panel)
	level3_timer_label = _make_label("", 24, Color("#ffd7a3"))
	level3_timer_label.anchor_left = 0.5
	level3_timer_label.anchor_right = 0.5
	level3_timer_label.offset_left = -125.0
	level3_timer_label.offset_right = 125.0
	level3_timer_label.offset_top = 52.0
	level3_timer_label.offset_bottom = 88.0
	level3_timer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	level3_timer_label.add_theme_color_override("font_outline_color", Color("#351c21"))
	level3_timer_label.add_theme_constant_override("outline_size", 5)
	level3_timer_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(level3_timer_label)
	boss_status_label = _make_label("", 17, Color("#ff8a75"))
	boss_status_label.anchor_left = 0.5
	boss_status_label.anchor_right = 0.5
	boss_status_label.offset_left = -200.0
	boss_status_label.offset_right = 200.0
	boss_status_label.offset_top = 88.0
	boss_status_label.offset_bottom = 114.0
	boss_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	boss_status_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(boss_status_label)
	microphone_toggle = CheckButton.new()
	microphone_toggle.text = "MIC"
	microphone_toggle.position = Vector2(14.0, 53.0)
	microphone_toggle.tooltip_text = ("Opt in to live microphone level detection. Audio is analyzed in memory only.")
	microphone_toggle.toggled.connect(_set_microphone_enabled)
	root.add_child(microphone_toggle)
	microphone_meter = ProgressBar.new()
	microphone_meter.position = Vector2(75.0, 57.0)
	microphone_meter.custom_minimum_size = Vector2(180.0, 22.0)
	microphone_meter.size = Vector2(180.0, 22.0)
	microphone_meter.max_value = 100.0
	microphone_meter.show_percentage = true
	microphone_meter.tooltip_text = "Mommy is alerted when the meter reaches 3%."
	microphone_meter.add_theme_stylebox_override("background", _panel_style(Color("#26313d")))
	var microphone_fill := StyleBoxFlat.new()
	microphone_fill.bg_color = Color("#53c98b")
	microphone_fill.set_corner_radius_all(4)
	microphone_meter.add_theme_stylebox_override("fill", microphone_fill)
	root.add_child(microphone_meter)
	var microphone_threshold_marker := ColorRect.new()
	microphone_threshold_marker.position = Vector2(80.4, 55.0)
	microphone_threshold_marker.size = Vector2(2.0, 26.0)
	microphone_threshold_marker.color = Color("#ff4655")
	microphone_threshold_marker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(microphone_threshold_marker)
	var microphone_threshold_label := _make_label("3%", 9, Color("#ff8b94"))
	microphone_threshold_label.position = Vector2(68.0, 79.0)
	microphone_threshold_label.size = Vector2(28.0, 14.0)
	microphone_threshold_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	microphone_threshold_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(microphone_threshold_label)
	microphone_status_label = _make_label("OFF", 12, Color("#cbd5e1"))
	microphone_status_label.position = Vector2(262.0, 57.0)
	microphone_status_label.size = Vector2(145.0, 22.0)
	root.add_child(microphone_status_label)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	hud_panel.add_child(row)
	hud_values["title"] = _add_hud_label(row, "SHADOW HUNT  [L1/2]", 17, Color("#10b981"))
	hud_values["hp"] = _add_hud_label(row, "HP 100", 15, Color.WHITE)
	health_bar = ProgressBar.new()
	health_bar.custom_minimum_size = Vector2(105, 17)
	health_bar.max_value = 100
	health_bar.value = 100
	row.add_child(health_bar)
	hud_values["score"] = _add_hud_label(row, "SCORE 0", 15, Color("#facc15"))
	hud_values["kills"] = _add_hud_label(row, "KILLS 0", 14, Color("#ffd166"))
	hud_values["targets"] = _add_hud_label(row, "TARGETS 0/0", 14, Color("#ef4444"))
	hud_values["items"] = _add_hud_label(row, "COINS 0", 14, Color("#cbd5e1"))
	hud_values["status"] = _add_hud_label(row, "STATUS SECURE", 14, Color("#38bdf8"))
	footer_label = Label.new()
	footer_label.anchor_left = 0.0
	footer_label.anchor_right = 1.0
	footer_label.anchor_top = 1.0
	footer_label.anchor_bottom = 1.0
	footer_label.offset_top = -28.0
	footer_label.offset_bottom = -2.0
	footer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	footer_label.add_theme_color_override("font_color", Color("#94a3b8"))
	root.add_child(footer_label)
	menu_panel = _make_overlay_panel(root)
	var menu_box := VBoxContainer.new()
	menu_box.add_theme_constant_override("separation", 11)
	menu_panel.add_child(menu_box)
	var title := _make_label("SHADOW HUNT", 34, Color("#40d9e5"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	menu_box.add_child(title)
	var subtitle := _make_label("Stealth Assassin — Facility Sweep", 17, Color("#cbd5e1"))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	menu_box.add_child(subtitle)
	menu_stats = _make_label("", 17, Color("#facc15"))
	menu_stats.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	menu_box.add_child(menu_stats)
	_add_button(menu_box, "PLAY LEVEL 1", _start_level.bind(0, true))
	_add_button(menu_box, "PLAY LEVEL 2  (DIRECT ENTRY)", _start_level.bind(1, true))
	_add_button(
		menu_box, "PLAY LEVEL 3  (FINAL HUNT → NIGHTMARE)", _start_level.bind(DEVIL_LEVEL_INDEX, true)
	)
	_add_button(menu_box, "QUIT  [ESC]", get_tree().quit)
	result_panel = _make_overlay_panel(root)
	var result_box := VBoxContainer.new()
	result_box.add_theme_constant_override("separation", 14)
	result_panel.add_child(result_box)
	result_title = _make_label("", 28, Color("#35e5a5"))
	result_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	result_box.add_child(result_title)
	result_summary = _make_label("", 15, Color.WHITE)
	result_summary.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	result_box.add_child(result_summary)
	var result_line := _make_label("", 15, Color("#facc15"))
	result_line.name = "ResultLine"
	result_line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	result_box.add_child(result_line)
	result_next_button = Button.new()
	result_next_button.text = "NEXT LEVEL  [ENTER]"
	result_next_button.pressed.connect(_continue_level)
	result_box.add_child(result_next_button)
	_add_button(result_box, "RETRY  [R]", _retry_level)
	_add_button(result_box, "MAIN MENU", _show_menu)
	alarm_overlay = ColorRect.new()
	alarm_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	alarm_overlay.color = Color(0.82, 0.015, 0.02, 0.24)
	alarm_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(alarm_overlay)
	alarm_warning = Label.new()
	alarm_warning.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	alarm_warning.offset_left = 80.0
	alarm_warning.offset_right = -80.0
	alarm_warning.offset_top = -90.0
	alarm_warning.offset_bottom = 90.0
	alarm_warning.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	alarm_warning.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	alarm_warning.add_theme_font_size_override("font_size", 54)
	alarm_warning.add_theme_color_override("font_color", Color("#fff4f4"))
	alarm_warning.add_theme_color_override("font_outline_color", Color("#4b0000"))
	alarm_warning.add_theme_constant_override("outline_size", 8)
	alarm_warning.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(alarm_warning)
	transition_overlay = ColorRect.new()
	transition_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	transition_overlay.color = Color.BLACK
	transition_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	transition_overlay.visible = false
	transition_overlay.z_index = 100
	root.add_child(transition_overlay)


func _make_overlay_panel(root: Control) -> PanelContainer:
	var panel := PanelContainer.new()
	panel.anchor_left = 0.5
	panel.anchor_right = 0.5
	panel.anchor_top = 0.5
	panel.anchor_bottom = 0.5
	panel.offset_left = -280
	panel.offset_right = 280
	panel.offset_top = -225
	panel.offset_bottom = 225
	panel.add_theme_stylebox_override("panel", _panel_style(Color(0.025, 0.045, 0.08, 0.97)))
	panel.add_theme_constant_override("margin_left", 26)
	panel.add_theme_constant_override("margin_right", 26)
	panel.add_theme_constant_override("margin_top", 22)
	panel.add_theme_constant_override("margin_bottom", 22)
	root.add_child(panel)
	return panel


func _panel_style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = Color(0.16, 0.35, 0.46, 0.9)
	style.set_border_width_all(2)
	style.set_corner_radius_all(8)
	style.set_content_margin_all(10)
	return style


func _make_label(text: String, size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	return label


func _add_hud_label(parent: Control, text: String, size: int, color: Color) -> Label:
	var label := _make_label(text, size, color)
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	parent.add_child(label)
	return label


func _add_button(parent: Control, text: String, callback: Callable) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = Vector2(0, 38)
	button.pressed.connect(callback)
	parent.add_child(button)
	return button


func _update_ui() -> void:
	if not is_instance_valid(ui_layer):
		return
	hud_panel.visible = game_state != "menu"
	menu_overlay.visible = game_state == "menu"
	menu_panel.visible = game_state == "menu"
	result_panel.visible = game_state in ["victory", "game_over"]
	alarm_overlay.visible = alarm_active and game_state == "playing"
	alarm_warning.visible = alarm_active and game_state == "playing"
	level3_timer_label.visible = level_index == MOMMY_LEVEL_INDEX and game_state == "playing"
	level3_timer_label.text = "SURVIVE  %02d" % int(ceil(level3_time_left))
	boss_status_label.visible = level_index == DEVIL_LEVEL_INDEX and game_state == "playing"
	var boss: Dictionary = {}
	for enemy in enemies:
		if bool(enemy.get("boss", false)):
			boss = enemy
			break
	var boss_hit_marks := ""
	for pip in range(BOSS_MAX_HITS):
		boss_hit_marks += " [---]" if float(boss.get("health", 0.0)) > pip else " [   ]"
	boss_status_label.text = "FINAL HUNT BOSS" + boss_hit_marks if not boss.is_empty() else ""
	microphone_toggle.visible = level_index == MOMMY_LEVEL_INDEX and game_state == "playing"
	microphone_meter.visible = microphone_toggle.visible
	microphone_status_label.visible = microphone_toggle.visible
	microphone_meter.value = voice_level_percent
	microphone_status_label.text = (
		"ALERT >3%"
		if suspense_alert_active
		else ("LIVE: %d%%" % int(voice_level_percent) if microphone_enabled else "OFF")
	)
	microphone_status_label.add_theme_color_override(
		"font_color", Color("#ff6060") if suspense_alert_active else Color("#cbd5e1")
	)
	transition_overlay.visible = game_state == "transition"
	alarm_overlay.color = Color(0.82, 0.015, 0.02, 0.2 + 0.08 * absf(sin(elapsed * 5.0)))
	alarm_warning.text = "LOCKDOWN\n%.1f" % alarm_timer if alarm_active else ""
	footer_label.text = (
		"WASD Move | Ctrl/J Jump | Shift Sprint | "
		+ "Space Attack | E Quiet Glass | Click Hide | H Debug | R Retry | Esc Menu"
	)
	var displayed_level := mini(level_index + 1, 3)
	hud_values.title.text = "SHADOW HUNT  [L%d/3]" % displayed_level
	hud_values.hp.text = "HP %d%%" % int(player_health)
	health_bar.value = player_health
	hud_values.score.text = "SCORE %d" % score
	hud_values.kills.text = "KILLS %d" % session_kills
	hud_values.targets.text = "TARGETS %d/%d" % [_alive_enemy_count(), enemies.size()]
	hud_values.items.text = (
		"COINS %d | MEDKITS %d" % [_remaining_items(false), _remaining_items(true)]
	)
	if level_index == DEVIL_LEVEL_INDEX and game_state == "playing":
		hud_values.status.text = "DEFEAT THE BOSS 3 TIMES"
		hud_values.status.add_theme_color_override("font_color", Color("#ff7777"))
	elif level_index == MOMMY_LEVEL_INDEX and game_state == "playing":
		if mommy_knows_hidden_spot:
			hud_values.status.text = "RELOCATE: MOMMY KNOWS YOUR SPOT"
		elif player_hidden:
			hud_values.status.text = "MOVE IN %.1f S" % maxf(0.0, HIDE_LIMIT_SECONDS - hidden_time)
		else:
			hud_values.status.text = "HIDE FROM MOMMY"
		hud_values.status.add_theme_color_override("font_color", Color("#ffb38a"))
	elif alarm_active:
		hud_values.status.text = "ALARM %.1fs" % alarm_timer
		hud_values.status.add_theme_color_override("font_color", Color("#ff4545"))
	elif extract_ready:
		hud_values.status.text = "TARGETS DOWN - EXTRACT"
		hud_values.status.add_theme_color_override("font_color", Color("#24d98a"))
	else:
		hud_values.status.text = "STATUS SECURE"
		hud_values.status.add_theme_color_override("font_color", Color("#38bdf8"))
	menu_stats.text = (
		"TOTAL SCORE  %d     COINS  %d     KILLS  %d" % [career_score, career_coins, career_kills]
	)
	if result_panel.visible:
		var result_line := result_panel.find_child("ResultLine", true, false) as Label
		if result_line:
			result_line.text = (
				"%s   |   SCORE %d   |   KILLS %d   |   COINS %d"
				% [level_name, score, session_kills, session_coins]
			)
	result_next_button.visible = game_state == "victory" and level_index < 2


func _remaining_items(medkit: bool) -> int:
	var count := 0
	for item in collectibles:
		if not item.collected and bool(item.medkit) == medkit:
			count += 1
	return count
