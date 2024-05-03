#!/usr/local/bin/python

import jinja2
import yaml

config_file = 'ci/config.yaml'

with open(config_file) as f:
    config = yaml.safe_load(f)

jinja_env = jinja2.Environment(loader=jinja2.BaseLoader())

def recursive_render(tpl, values):
     prev = tpl
     while True:
         curr = jinja_env.from_string(prev).render(**values)
         if curr != prev:
             prev = curr
         else:
             return curr

def generate_job(template, image_type, os, osver, spackver, target, targetver=None):
    if target == "cpu":
        spack_target = "alps-zen2"
    elif target == "cuda":
        spack_target = "alps-a100"
    elif target == "rocm":
        spack_target = "alps-mi200"
    else:
        print(f"Error: undnouwn target {target}")
        exit(1)

    data = {
            "image_type": image_type,
            "os": os,
            "osver": osver,
            "spackver": spackver,
            "cudaver": targetver if target == "cuda" else None,
            "rocmver": targetver if target == "rocm" else None,
            "spack_target": spack_target,
            "registry_path": config["registry_path"],
            "deploy_path": config["deploy_path"],
            "basedockerfile": config["basedockerfile"],
            "helperdockerfile": config["helperdockerfile"],
            "registry_base_image_name_tag": config["registry_base_image_name_tag"],
            "deploy_base_image_name_tag": config["deploy_base_image_name_tag"],
            "registry_helper_image_name_tag": config["registry_helper_image_name_tag"],
            "deploy_helper_image_name_tag": config["deploy_helper_image_name_tag"],
            "baseimg": config["baseimg"][target],
            "arch": target,
            "archstr": config["archstr"][target],
            "docker_build_args_base": config["docker_build_args_base"][target],
            "docker_build_args_helper": config["docker_build_args_helper"][target],
            "container_builder": config["container_builder"][target],
            "container_runner": config["container_runner"][target],
            "container_deploy": config["container_deploy"],
            "deploy_runner_image": config["deploy_runner_image"],
            }

    return recursive_render(template, data)

pipeline = []

# Add header (include)
pipeline.append(
"""include:
  - remote: 'https://gitlab.com/cscs-ci/recipes/-/raw/master/templates/v2/.ci-ext.yml'

stages:
  - build_base_image
  - test_base_image
  - build_test_image
  - test_test_image
  - deploy_base_image"""
)

image_type = "base"
with open('ci/templates/base_image.yml.j2') as f:
    template = f.read()
for os in config["os"].keys():
    for osver in config["os"][os]:
        for spackver in config["spackver"]:
            target = "cpu"
            pipeline.append(generate_job(template, image_type, os, osver, spackver, target))

            for cudaver in config["cudaver"]:
                target = "cuda"
                targetver = cudaver
                pipeline.append(generate_job(template, image_type, os, osver, spackver, target, targetver))

            for rocmver in config["rocmver"]:
                target = "rocm"
                targetver = rocmver
                pipeline.append(generate_job(template, image_type, os, osver, spackver, target, targetver))

image_type = "helper"
with open('ci/templates/helper_image.yml.j2') as f:
    template = f.read()
spackver = None
for os in config["os"].keys():
    for osver in config["os"][os]:
        target = "cpu"
        pipeline.append(generate_job(template, image_type, os, osver, spackver, target))

        for cudaver in config["cudaver"]:
            target = "cuda"
            targetver = cudaver
            pipeline.append(generate_job(template, image_type, os, osver, spackver, target, targetver))

        for rocmver in config["rocmver"]:
            target = "rocm"
            targetver = rocmver
            pipeline.append(generate_job(template, image_type, os, osver, spackver, target, targetver))

image_type = "test"
with open('ci/templates/test_image.yml.j2') as f:
    template = f.read()
for os in config["os"].keys():
    for osver in config["os"][os]:
        for spackver in config["spackver"]:
            target = "cpu"
            pipeline.append(generate_job(template, image_type, os, osver, spackver, target))

            for cudaver in config["cudaver"]:
                target = "cuda"
                targetver = cudaver
                pipeline.append(generate_job(template, image_type, os, osver, spackver, target, targetver))

            for rocmver in config["rocmver"]:
                target = "rocm"
                targetver = rocmver
                pipeline.append(generate_job(template, image_type, os, osver, spackver, target, targetver))

#print("\n\n--------------------\n\n".join(pipeline))
print("\n\n".join(pipeline))
