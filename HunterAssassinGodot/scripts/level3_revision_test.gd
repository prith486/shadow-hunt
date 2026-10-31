extends SceneTree


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var game := (load("res://Main.tscn") as PackedScene).instantiate()
	root.add_child(game)
	await process_frame

	game.call("_build_level", 1)
	var level_two_world: Vector2 = game.get("world_size")
	var level_two_box_count := (game.get("boxes") as Array).size()
	var level_two_wall_count := (game.get("walls") as Array).size()
	var level_two_door_count := (game.get("doors") as Array).size()
	var cleared_path_points := [
		Vector2(208.0, 125.0), Vector2(516.0, 370.0), Vector2(96.0, 604.0), Vector2(802.0, 116.0)
	]
	for point in cleared_path_points:
		if not _check(
			game.call("_position_blocked", point, 2.0),
			"Level 2 baseline contains the path barricade at %s" % point
		):
			return
	game.call("_build_level", 2)
	if not _check(
		game.get("world_size") == level_two_world, "Level 3 boss world size matches Level 2"
	):
		return
	if not _check(
		(game.get("boxes") as Array).size() == level_two_box_count,
		"Level 2 crate layout is preserved"
	):
		return
	if not _check(
		(game.get("walls") as Array).size() == level_two_wall_count - 4,
		"Level 3 clears the four short path barricades from the Level 2 layout"
	):
		return
	if not _check(
		(game.get("doors") as Array).size() == level_two_door_count,
		"Level 2 door layout is preserved"
	):
		return
	game.call("_start_level", 2, true)
	var camera := game.get_node("Camera2D") as Camera2D
	var expected_camera_center := Vector2(60.0, 60.0) + level_two_world * 0.5
	if not _check(
		is_equal_approx(camera.zoom.x, 1.5) and is_equal_approx(camera.zoom.y, 1.5),
		"Level 3 camera uses the wider scrolling zoom"
	):
		return
	game.set("player_position", expected_camera_center)
	game.call("_update_camera", true)
	if not _check(
		camera.position.is_equal_approx(expected_camera_center),
		"Level 3 camera follows the player inside the arena bounds"
	):
		return
	var camera_half_view: Vector2 = game.get_viewport_rect().size / camera.zoom * 0.5
	game.set("player_position", Vector2(65.0, 65.0))
	game.call("_update_camera", true)
	if not _check(
		camera.position.is_equal_approx(Vector2(60.0, 60.0) + camera_half_view),
		"Level 3 camera clamps to the arena boundary"
	):
		return
	for point in cleared_path_points:
		if not _check(
			not game.call("_position_blocked", point, 2.0), "Level 3 path is clear at %s" % point
		):
			return
	var enemies: Array = game.get("enemies")
	if not _check(enemies.size() == 4, "Boss stage has three guards and one boss"):
		return
	var boss_index := 3
	var boss: Dictionary = enemies[boss_index]
	if not _check(float(boss.health) == 3.0, "Boss starts with three hit marks"):
		return
	var constants: Dictionary = game.get_script().get_script_constant_map()
	if not _check(
		is_equal_approx(float(constants["BOSS_RENDER_SCALE"]), 1.5),
		"Devil Leader renders at 1.5 times normal enemy size"
	):
		return
	if not _check(
		not game.call("_blocked_by_static_geometry", boss.pos, 25.0),
		"Boss starts in an open location"
	):
		return
	var shot_target := Vector2.ZERO
	for direction_index in range(16):
		var candidate: Vector2 = (
			boss.pos + Vector2.RIGHT.rotated(TAU * float(direction_index) / 16.0) * 120.0
		)
		if (
			not game.call("_position_blocked", candidate, 15.0)
			and game.call("_has_line_of_sight", boss.pos, candidate)
		):
			shot_target = candidate
			break
	if not _check(shot_target != Vector2.ZERO, "Boss has a clear firing lane for the test"):
		return
	game.set("player_position", shot_target)
	game.set("player_health", 100.0)
	boss.shot_timer = 0.0
	boss.speed = 0.1
	boss.boss_run_timer = 0.0
	boss.boss_roam_target = Vector2(boss.pos) + Vector2(0.0, 50.0)
	var bullet_count_before := (game.get("enemy_bullets") as Array).size()
	game.call("_update_boss_roaming", boss, 0.01)
	var bullets: Array = game.get("enemy_bullets")
	if not _check(
		(
			bullets.size() == bullet_count_before + 1
			and is_equal_approx(float(bullets.back().damage), 25.0)
		),
		"Devil Leader fires projectiles that deal 25 health points"
	):
		return
	bullets.back().pos = shot_target - Vector2(5.0, 0.0)
	bullets.back().velocity = Vector2.ZERO
	game.call("_update_enemy_bullets", 0.01)
	if not _check(
		is_equal_approx(float(game.get("player_health")), 75.0),
		"Boss projectile collision reduces player health by 25"
	):
		return
	boss.speed = 92.0
	var boss_start: Vector2 = boss.pos
	for frame in range(80):
		game.call("_update_doors", 0.05)
		game.call("_update_boss_roaming", boss, 0.05)
	if not _check(Vector2(boss.pos).distance_to(boss_start) > 5.0, "Boss moves while roaming"):
		return
	game.call("_damage_enemy", boss_index, 100.0)
	if not _check(float(boss.health) == 2.0, "First hit removes one boss mark"):
		return
	if not _check(float(boss.boss_relocate_timer) == 1.0, "Boss blinks for one second after a hit"):
		return
	var before_teleport: Vector2 = boss.pos
	for frame in range(20):
		game.call("_update_doors", 0.05)
		game.call("_update_boss_roaming", boss, 0.05)
	if not _check(
		Vector2(boss.pos).distance_to(before_teleport) > 5.0, "Boss relocates after blinking"
	):
		return
	for frame in range(60):
		game.call("_update_boss_roaming", boss, 0.05)
	game.call("_damage_enemy", boss_index, 100.0)
	if not _check(float(boss.health) == 1.0, "Second hit removes the second mark"):
		return
	for frame in range(60):
		game.call("_update_boss_roaming", boss, 0.05)
	game.call("_damage_enemy", boss_index, 100.0)
	if not _check(game.get("game_state") == "transition", "Third hit starts the Mommy transition"):
		return

	game.call("_build_level", 3)
	game.call("_start_level", 3, false)
	if not _check(
		is_equal_approx(camera.zoom.x, 1.5) and is_equal_approx(camera.zoom.y, 1.5),
		"Mommy stage keeps the wider scrolling zoom"
	):
		return
	var house_center := Vector2(560.0, 410.0)
	game.set("player_position", house_center)
	game.call("_update_camera", true)
	if not _check(
		camera.position.is_equal_approx(house_center),
		"Mommy stage camera follows the player through the house"
	):
		return
	if not _check(
		(game.get("doors") as Array).size() == 16, "House has all blueprint room and exit passages"
	):
		return
	game.call("_update_ui")
	var art_frames: Dictionary = game.get("art_frames")
	var mommy_idle_frames: Array = art_frames.get("mommy/idle", [])
	var mommy_walk_frames: Array = art_frames.get("mommy/walk", [])
	var mommy_attack_frames: Array = art_frames.get("mommy/attack", [])
	if not _check(
		(
			mommy_idle_frames.size() == 12
			and mommy_walk_frames.size() == 12
			and mommy_attack_frames.size() == 12
		),
		"Mommy uses the supplied Wraith_03 idle, walking, and attack frames"
	):
		return
	var meter: ProgressBar = game.get("microphone_meter")
	if not _check(
		meter.visible and is_equal_approx(meter.max_value, 100.0),
		"Mommy stage shows the live microphone scale"
	):
		return
	var threshold_level: float = game.call(
		"_measure_voice_level", PackedVector2Array([Vector2(0.0075, 0.0075)])
	)
	if not _check(
		is_equal_approx(threshold_level, 3.0),
		"Microphone level calibration reaches the visible 3% alert marker"
	):
		return
	var test_mommy: Dictionary = (game.get("enemies") as Array)[0]
	test_mommy.pos = Vector2(650, 480)
	game.set("player_position", Vector2(790, 510))
	game.set("voice_level_percent", 3.1)
	game.set("mic_was_loud", false)
	game.get("noise_events").clear()
	game.call("_update_voice_detection")
	game.call("_propagate_noise", 0.05)
	if not _check(
		(
			bool(test_mommy.alert)
			and bool(test_mommy.mom_pursuing)
			and bool(test_mommy.mom_voice_tracking)
			and Vector2(test_mommy.last_seen).distance_to(game.get("player_position")) < 35.0
		),
		"3% microphone noise sends Mommy toward the player's approximate location"
	):
		return
	game.set("voice_level_percent", 0.0)
	game.set("mic_was_loud", false)
	game.get("noise_events").clear()
	(game.get("glass_debris") as Array).clear()
	test_mommy.pos = Vector2(160, 560)
	test_mommy.alert = false
	test_mommy.mom_pursuing = false
	test_mommy.mom_voice_tracking = false
	test_mommy.mom_searching = false
	test_mommy.pursuit_timer = 0.0
	var expected_rooms := [
		Vector2(160, 100),
		Vector2(360, 100),
		Vector2(160, 220),
		Vector2(360, 220),
		Vector2(590, 100),
		Vector2(800, 100),
		Vector2(800, 230),
		Vector2(160, 500),
		Vector2(590, 500),
		Vector2(800, 500)
	]
	for room_index in range(expected_rooms.size()):
		if not _check(
			game.call("_house_room_at", expected_rooms[room_index]) == room_index,
			"Blueprint room %d has its own navigation region" % room_index
		):
			return
	if not _check(
		(game.get("boxes") as Array).is_empty(),
		"Mommy house furniture stays non-blocking for both characters"
	):
		return
	var house_doors: Array = game.get("doors")
	var bedroom_passage: Dictionary = {}
	for door in house_doors:
		if int(door.get("room_a", -1)) == 2 and int(door.get("room_b", -1)) == 7:
			bedroom_passage = door
			break
	if not _check(not bedroom_passage.is_empty(), "The lower bedroom passage exists"):
		return
	var bedroom_doorway: Vector2 = (bedroom_passage.a + bedroom_passage.b) * 0.5
	if not _check(
		game.call("_position_blocked", bedroom_doorway, 15.0),
		"A closed widened doorway blocks the player"
	):
		return
	bedroom_passage.progress = 1.0
	game.set("player_position", bedroom_doorway + Vector2(0.0, -18.0))
	game.call("_move_player", Vector2(0.0, 36.0))
	if not _check(
		is_equal_approx(Vector2(game.get("player_position")).y, bedroom_doorway.y + 18.0),
		"The player can pass through the widened bedroom doorway when open"
	):
		return
	var glass_doors: Array[Dictionary] = []
	for door in house_doors:
		if bool(door.get("glass", false)):
			glass_doors.append(door)
	if not _check(glass_doors.size() == 7, "All seven mapped blue glass doors are interactive"):
		return
	var test_door: Dictionary = glass_doors[0]
	var door_center: Vector2 = (test_door.a + test_door.b) * 0.5
	game.set("player_position", door_center + Vector2(0, 25))
	game.call("_interact_with_glass_door")
	game.call("_update_doors", 0.05)
	if not _check(
		(
			not bool(test_door.broken)
			and bool(test_door.quiet_opening)
			and float(test_door.progress) > 0.0
		),
		"E quietly opens a glass door without breaking it"
	):
		return
	test_mommy.pos = Vector2(160, 560)
	test_mommy.mom_pursuing = false
	test_mommy.mom_searching = false
	test_mommy.mom_voice_tracking = false
	test_mommy.pursuit_timer = 0.0
	game.call("_shatter_glass_door", test_door)
	game.call("_propagate_noise", 0.05)
	if not _check(
		(
			bool(test_door.broken)
			and (game.get("glass_debris") as Array).size() == 1
			and (game.get("noise_events") as Array).back().get("kind") == "GLASS_SHATTER"
		),
		(
			"Breaking glass creates debris and a GLASS_SHATTER noise event: broken=%s debris=%d noises=%s"
			% [
				test_door.broken,
				(game.get("glass_debris") as Array).size(),
				game.get("noise_events")
			]
		)
	):
		return
	if not _check(
		(
			bool(test_mommy.alert)
			and not bool(test_mommy.mom_pursuing)
			and Vector2(test_mommy.last_seen).is_equal_approx(door_center)
		),
		"Glass shattering interrupts Mommy's patrol and sends her to the broken door"
	):
		return
	var mommy_before_investigating: Vector2 = test_mommy.pos
	var distance_to_broken_door := mommy_before_investigating.distance_to(door_center)
	for frame in range(20):
		game.call("_update_enemies", 0.05)
	if not _check(
		Vector2(test_mommy.pos).distance_to(door_center) < distance_to_broken_door,
		"Mommy moves off her patrol route toward the broken glass door"
	):
		return
	var main_exit_door: Dictionary = glass_doors.back()
	var exit_rect: Rect2 = game.get("exit_rect")
	game.set("player_position", exit_rect.get_center())
	if not _check(
		not game.call("_exit_reached"),
		"The main exit remains unavailable while its glass door is closed"
	):
		return
	game.call("_shatter_glass_door", main_exit_door)
	if not _check(
		game.call("_exit_reached"), "The player can leave only through the main entrance"
	):
		return
	game.call("_start_level", 3, false)
	var mommy: Dictionary = (game.get("enemies") as Array)[0]
	var visited_rooms := {}
	var stationary_time := 0.0
	var longest_stationary_time := 0.0
	var longest_stationary_frame := 0
	var longest_stationary_route := 0
	for frame in range(1800):
		visited_rooms[game.call("_house_room_at", mommy.pos)] = true
		var previous_position: Vector2 = mommy.pos
		game.call("_update_doors", 0.05)
		game.call("_patrol_mommy", mommy, 0.05)
		if mommy.pos.distance_to(previous_position) < 0.05:
			stationary_time += 0.05
			if stationary_time > longest_stationary_time:
				longest_stationary_time = stationary_time
				longest_stationary_frame = frame
				longest_stationary_route = mommy.mom_patrol_index
		else:
			stationary_time = 0.0
	for room_index in range(10):
		if not _check(visited_rooms.has(room_index), "Mommy did not patrol room %d" % room_index):
			return
	if not _check(
		longest_stationary_time <= 1.0,
		(
			"Mommy's longest patrol pause is %.2f seconds at frame %d route %d position %s"
			% [
				longest_stationary_time,
				longest_stationary_frame,
				longest_stationary_route,
				mommy.pos
			]
		)
	):
		return
	game.set("player_hidden", false)
	mommy.pos = Vector2(230.0, 520.0)
	mommy.angle = PI
	game.set("player_position", Vector2(270.0, 520.0))
	game.call("_update_enemies", 0.05)
	if not _check(
		bool(mommy.mom_pursuing) and mommy.last_seen == game.get("player_position"),
		"Mommy notices and pursues a nearby player even outside her facing direction"
	):
		return
	mommy.angle = PI
	game.set("player_position", mommy.pos + Vector2(180.0, 0.0))
	game.call("_update_enemies", 0.05)
	if not _check(
		bool(mommy.mom_pursuing) and mommy.last_seen == game.get("player_position"),
		"Mommy continues following the player after losing direct line of sight"
	):
		return
	game.set("player_hidden", true)
	game.call("_update_enemies", 0.05)
	if not _check(
		not bool(mommy.mom_pursuing) and bool(mommy.mom_searching),
		"Mommy switches from pursuit to searching when the player hides"
	):
		return
	game.set("player_hidden", false)
	var caught_position: Vector2 = game.get("player_position")
	mommy.pos = caught_position - Vector2(25.0, 0.0)
	mommy.attack_timer = 0.0
	game.call("_update_enemies", 0.05)
	if not _check(
		game.get("game_state") == "game_over",
		"Mommy catches the player when she reaches attack range"
	):
		return
	game.call("_process", 2.0)
	if not _check(
		game.get("game_state") == "playing" and int(game.get("level_index")) == 3,
		"Being caught automatically restarts the Nightmare level"
	):
		return
	mommy = (game.get("enemies") as Array)[0]
	game.set("player_hidden", true)
	mommy.last_seen = mommy.pos
	mommy.mom_was_seen = false
	mommy.mom_pursuing = false
	mommy.mom_searching = true
	mommy.mom_waiting = false
	mommy.mom_search_timer = 0.0
	mommy.pursuit_timer = 0.0
	var search_end_position: Vector2 = mommy.pos
	for frame in range(140):
		game.call("_update_doors", 0.05)
		game.call("_update_enemies", 0.05)
	if not _check(
		Vector2(mommy.pos).distance_to(search_end_position) > 10.0,
		"Mommy moves while searching the player's last-seen position"
	):
		return
	print("Level 3 revision regression checks passed.")
	quit(0)


func _check(condition: bool, message: String) -> bool:
	if condition:
		return true
	push_error("Regression check failed: %s" % message)
	quit(1)
	return false
