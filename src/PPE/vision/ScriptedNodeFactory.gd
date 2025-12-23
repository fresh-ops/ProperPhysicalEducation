class_name ScriptedNodeFactory
extends Node


static func create(script: ScriptExtension) -> Node:
	var node := Node.new()
	node.set_script(script)
	return node
