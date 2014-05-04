#!/usr/bin/python

import sys
import os
import shutil
import subprocess
import json
from pprint import pprint
from mod_pbxproj import XcodeProject

PROJECT_EXTENSION = ".xcodeproj"

Project = None

def main(argv):
	if len(argv) < 2:
		print "You have to specify the path to xcodeproj file"
		sys.exit(0)

	path_in = argv[1]
	if not path_in.endswith(PROJECT_EXTENSION):
		path_in += PROJECT_EXTENSION

	try:
		path_out = argv[2]
	except:
		path_out = path_in + "_export"

	export_project(path_in, path_out)

def export_project(proj_path, export_path):
	global Project

	proj_file = os.path.join(proj_path, "project.pbxproj")
	Project = XcodeProject.Load(proj_file)

	pbx_projects = objects_by_isa('PBXProject')
	for pbx_project in pbx_projects:
		main_id = pbx_project['mainGroup']
		list = [[proj_path, proj_path]]
		recursive_paths(list, ["", ""], main_id, "")
		copy_list_to_dir(list, export_path)

def recursive_paths(list, path, id, addpath):
	elem = Project.objects[id]

	src_path = path[0]
	elem_path = path[1]

	if elem["isa"] != "PBXVariantGroup":
		if "path" in elem:
			src_path = os.path.join(src_path, elem["path"])
			elem_path = os.path.join(elem_path, elem["path"])
			list.append([src_path, elem_path])
			elem["name"] = elem["path"]
			elem["path"] = os.path.join(addpath, elem["path"])
		elif "name" in elem:
			addpath = os.path.join(addpath, elem["name"])
			elem_path = os.path.join(elem_path, elem["name"])

	if "children" in elem:
		for child in elem["children"]:
			recursive_paths(list, [src_path, elem_path], child, addpath)

def ensure_dir_exists(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)

def copy_list_to_dir(list, dir):
	if os.path.exists(dir):
		shutil.rmtree(dir)

	os.makedirs(dir)

	for file in list:
		src_file = file[0]
		dst_file = os.path.join(dir, file[1])

		ensure_dir_exists(os.path.dirname(dst_file))
		if os.path.exists(src_file):
			if not os.path.isdir(src_file):
				shutil.copyfile(src_file, dst_file)
			elif src_file.endswith(PROJECT_EXTENSION):
				shutil.copytree(src_file, dst_file)
				save_pbxproj(dst_file)

def save_pbxproj(path):
	path = os.path.join(path, "project.pbxproj")
	Project.save(path)

def objects_by_isa(isa):
	return [obj for key, obj in Project.objects.iteritems() if obj['isa'] == isa]

if __name__ == "__main__":
	main(sys.argv)
