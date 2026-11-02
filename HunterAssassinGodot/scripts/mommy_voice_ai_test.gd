extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _check(condition: bool, message: String) -> bool:
	if condition:
		return true
	push_error("[FAIL] " + message)
	print("[FAIL] " + message)
	quit(1)
	return false

func _run() -> void:
	print("[TEST] Starting Mommy Room Navigation & Blind AI Verification...")
	var game := (load("res://Main.tscn") as PackedScene).instantiate()
	root.add_child(game)
	await process_frame

	game.call("_build_level", 3)
	game.call("_start_level", 3, false)
	if not _check(game.get("level_index") == 3, "Level 3 active"): return

	var mommy: Dictionary = (game.get("enemies") as Array)[0]
	var origin: Vector2 = game.get("ORIGIN")

	print("[TEST 1] Blind Mommy: Player is silent; Mommy must not approach...")
	var kitchen_pos := origin + Vector2(750, 480)
	var corridor_pos := origin + Vector2(580, 460)
	game.set("player_position", kitchen_pos)
	game.set("player_hidden", false)
	game.set("voice_level_percent", 0.0)
	game.set("mic_was_loud", false)

	mommy.pos = corridor_pos
	mommy.mom_patrol_order = [7, 8, 4, 1, 0]
	mommy.mom_patrol_index = 0
	mommy.alert = false
	mommy.mom_pursuing = false
	mommy.mom_voice_tracking = false
	mommy.mom_searching = false
	mommy.pursuit_timer = 0.0

	for frame in range(60):
		game.call("_update_doors", 0.05)
		game.call("_update_enemies", 0.05)

	if not _check(not bool(mommy.mom_pursuing), "Mommy must not pursue silent player without noise"): return
	if not _check(not bool(mommy.alert), "Mommy must not alert without noise"): return
	print("[PASS] Test 1: Blind Mommy ignores silent player across the room/doorway.")

	print("[TEST 2] Screenshot Scenario: Player speaks inside Kitchen -> Mommy enters room...")
	mommy.pos = corridor_pos
	mommy.mom_patrol_order = [7, 8, 4, 1, 0]
	mommy.mom_patrol_index = 0
	mommy.alert = false
	mommy.mom_pursuing = false
	mommy.mom_voice_tracking = false
	mommy.mom_searching = false
	mommy.pursuit_timer = 0.0

	game.set("voice_level_percent", 9.0)
	game.set("mic_was_loud", false)
	(game.get("noise_events") as Array).clear()
	game.call("_update_voice_detection", 0.016)
	game.call("_propagate_noise", 0.05)

	if not _check(bool(mommy.alert), "Mommy alerted by 9% voice"): return
	if not _check(bool(mommy.mom_pursuing), "Mommy pursuing player"): return

	for frame in range(120):
		game.call("_update_doors", 0.05)
		game.call("_update_enemies", 0.05)
		if game.get("game_state") == "game_over":
			break

	if not _check(game.get("game_state") == "game_over", "Mommy must navigate through the door and catch open player"): return
	print("[PASS] Test 2: Mommy entered room through door and caught player!")

	print("[TEST 3] Player hides -> Mommy enters room, searches for 3-4s, then goes away...")
	game.call("_start_level", 3, false)
	mommy = (game.get("enemies") as Array)[0]
	mommy.pos = corridor_pos
	mommy.mom_patrol_order = [7, 8, 4, 1, 0]
	mommy.mom_patrol_index = 0
	mommy.alert = false
	mommy.mom_pursuing = false
	mommy.mom_voice_tracking = false
	mommy.mom_searching = false
	mommy.pursuit_timer = 0.0

	game.set("player_position", kitchen_pos)
	game.set("player_hidden", true)
	game.set("hidden_time", 1.0)
	game.set("voice_level_percent", 9.0)
	game.set("mic_was_loud", false)
	(game.get("noise_events") as Array).clear()
	game.call("_update_voice_detection", 0.016)
	game.call("_propagate_noise", 0.05)

	for frame in range(100):
		game.call("_update_doors", 0.05)
		game.call("_update_enemies", 0.05)

	for frame in range(80):
		game.call("_update_doors", 0.05)
		game.call("_update_enemies", 0.05)

	if not _check(not bool(mommy.mom_searching), "Mommy must finish search after 3-4 seconds"): return
	if not _check(not bool(mommy.alert), "Mommy alert must clear"): return
	if not _check(game.get("game_state") == "playing", "Player must remain alive in hiding spot"): return
	print("[PASS] Test 3: Mommy searched room and walked away after 3-4 seconds without finding hidden player!")

	print("[ALL VERIFICATIONS PASSED SUCCESSFULLY!]")
	quit(0)

