class_name CGMath
extends RefCounted


static func translate_points(points: Array, offset: Vector2) -> Array:
	var result: Array = []
	for point in points:
		result.append(point + offset)
	return result


static func rotate_points(points: Array, angle: float, center: Vector2 = Vector2.ZERO) -> Array:
	var result: Array = []
	for point in points:
		result.append(center + (point - center).rotated(angle))
	return result


static func scale_points(
	points: Array, scale_factor: float, center: Vector2 = Vector2.ZERO
) -> Array:
	var result: Array = []
	for point in points:
		result.append(center + (point - center) * scale_factor)
	return result


static func bresenham_circle(center: Vector2i, radius: int) -> Array[Vector2i]:
	var result: Array[Vector2i] = []
	var unique: Dictionary = {}
	if radius <= 0:
		result.append(center)
		return result

	var x := 0
	var y := radius
	var decision := 1 - 2 * radius
	while x <= y:
		var octants := [
			Vector2i(center.x + x, center.y + y),
			Vector2i(center.x - x, center.y + y),
			Vector2i(center.x + x, center.y - y),
			Vector2i(center.x - x, center.y - y),
			Vector2i(center.x + y, center.y + x),
			Vector2i(center.x - y, center.y + x),
			Vector2i(center.x + y, center.y - x),
			Vector2i(center.x - y, center.y - x)
		]
		for point in octants:
			unique[point] = true
		if decision < 0:
			decision += 2 * x + 3
			x += 1
		else:
			decision += 2 * (x - y) + 5
			x += 1
			y -= 1
	for point in unique:
		result.append(point)
	return result


static func point_in_polygon(point: Vector2, polygon: PackedVector2Array) -> bool:
	if polygon.size() < 3:
		return false
	var inside := false
	var previous := polygon[polygon.size() - 1]
	for current in polygon:
		if min(previous.y, current.y) < point.y and point.y <= max(previous.y, current.y):
			if point.x <= max(previous.x, current.x):
				var intersection := previous.x
				if not is_equal_approx(previous.y, current.y):
					intersection = (
						(point.y - previous.y) * (current.x - previous.x) / (current.y - previous.y)
						+ previous.x
					)
				if is_equal_approx(previous.x, current.x) or point.x <= intersection:
					inside = not inside
		previous = current
	return inside


static func cone_polygon(
	origin: Vector2, facing: float, fov: float, length: float, arc_steps: int = 16
) -> PackedVector2Array:
	var points := PackedVector2Array([origin])
	for index in range(arc_steps + 1):
		var angle := facing - fov * 0.5 + fov * float(index) / float(arc_steps)
		points.append(origin + Vector2(cos(angle), sin(angle)) * length)
	return points


static func clip_line_cohen_sutherland(from: Vector2, to: Vector2, bounds: Rect2) -> Dictionary:
	var x_min := bounds.position.x
	var y_min := bounds.position.y
	var x_max := bounds.end.x
	var y_max := bounds.end.y
	var x1 := from.x
	var y1 := from.y
	var x2 := to.x
	var y2 := to.y
	var code1 := _out_code(x1, y1, x_min, y_min, x_max, y_max)
	var code2 := _out_code(x2, y2, x_min, y_min, x_max, y_max)

	while true:
		if (code1 | code2) == 0:
			return {"hit": true, "from": Vector2(x1, y1), "to": Vector2(x2, y2)}
		if (code1 & code2) != 0:
			return {"hit": false}

		var code_out: int = code1 if code1 != 0 else code2
		var x := 0.0
		var y := 0.0
		if (code_out & 4) != 0:
			x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1) if not is_equal_approx(y2, y1) else x1
			y = y_max
		elif (code_out & 8) != 0:
			x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1) if not is_equal_approx(y2, y1) else x1
			y = y_min
		elif (code_out & 2) != 0:
			y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1) if not is_equal_approx(x2, x1) else y1
			x = x_max
		else:
			y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1) if not is_equal_approx(x2, x1) else y1
			x = x_min

		if code_out == code1:
			x1 = x
			y1 = y
			code1 = _out_code(x1, y1, x_min, y_min, x_max, y_max)
		else:
			x2 = x
			y2 = y
			code2 = _out_code(x2, y2, x_min, y_min, x_max, y_max)
	return {"hit": false}


static func clip_polygon_aabb(polygon: PackedVector2Array, bounds: Rect2) -> PackedVector2Array:
	var output := polygon
	for edge in range(4):
		var clipped := PackedVector2Array()
		if output.is_empty():
			return clipped
		var previous := output[output.size() - 1]
		for current in output:
			var previous_inside := _inside_edge(previous, edge, bounds)
			var current_inside := _inside_edge(current, edge, bounds)
			if current_inside:
				if not previous_inside:
					clipped.append(_edge_intersection(previous, current, edge, bounds))
				clipped.append(current)
			elif previous_inside:
				clipped.append(_edge_intersection(previous, current, edge, bounds))
			previous = current
		output = clipped
	return output


static func _out_code(
	x: float, y: float, x_min: float, y_min: float, x_max: float, y_max: float
) -> int:
	var code := 0
	if x < x_min:
		code |= 1
	elif x > x_max:
		code |= 2
	if y < y_min:
		code |= 8
	elif y > y_max:
		code |= 4
	return code


static func _inside_edge(point: Vector2, edge: int, bounds: Rect2) -> bool:
	if edge == 0:
		return point.x >= bounds.position.x
	if edge == 1:
		return point.x <= bounds.end.x
	if edge == 2:
		return point.y >= bounds.position.y
	return point.y <= bounds.end.y


static func _edge_intersection(from: Vector2, to: Vector2, edge: int, bounds: Rect2) -> Vector2:
	var delta := to - from
	if edge < 2:
		var x := bounds.position.x if edge == 0 else bounds.end.x
		var y := (
			from.y + delta.y * (x - from.x) / delta.x if not is_zero_approx(delta.x) else from.y
		)
		return Vector2(x, y)
	var y := bounds.position.y if edge == 2 else bounds.end.y
	var x := from.x + delta.x * (y - from.y) / delta.y if not is_zero_approx(delta.y) else from.x
	return Vector2(x, y)
