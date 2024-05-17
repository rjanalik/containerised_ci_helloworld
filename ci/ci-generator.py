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

def generate_job(template, os, osver, spackver, target, targetver=None):
    if target == "cpu":
        spack_target = "alps-zen2"
    elif target == "cuda":
        spack_target = "alps-a100"
    elif target == "rocm":
        spack_target = "alps-mi200"
    else:
        print(f"Error: undnouwn target {target}")
        exit(1)

    data = config | {
            "os": os,
            "osver": osver,
            "spackver": spackver,
            "cudaver": targetver if target == "cuda" else None,
            "rocmver": targetver if target == "rocm" else None,
            "arch": target,
            "spack_target": spack_target,
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

with open('ci/templates/base_image.yml.j2') as f:
    template = f.read()
for os in config["os"].keys():
    for osver in config["os"][os]:
        for spackver in config["spackver"]:
            target = "cpu"
            pipeline.append(generate_job(template, os, osver, spackver, target))

            for cudaver in config["cudaver"]:
                target = "cuda"
                targetver = cudaver
                pipeline.append(generate_job(template, os, osver, spackver, target, targetver))

            for rocmver in config["rocmver"]:
                target = "rocm"
                targetver = rocmver
                pipeline.append(generate_job(template, os, osver, spackver, target, targetver))

with open('ci/templates/helper_image.yml.j2') as f:
    template = f.read()
spackver = None
for os in config["os"].keys():
    for osver in config["os"][os]:
        target = "cpu"
        pipeline.append(generate_job(template, os, osver, spackver, target))

        for cudaver in config["cudaver"]:
            target = "cuda"
            targetver = cudaver
            pipeline.append(generate_job(template, os, osver, spackver, target, targetver))

        for rocmver in config["rocmver"]:
            target = "rocm"
            targetver = rocmver
            pipeline.append(generate_job(template, os, osver, spackver, target, targetver))

with open('ci/templates/test_image.yml.j2') as f:
    template = f.read()
for os in config["os"].keys():
    for osver in config["os"][os]:
        for spackver in config["spackver"]:
            target = "cpu"
            pipeline.append(generate_job(template, os, osver, spackver, target))

            for cudaver in config["cudaver"]:
                target = "cuda"
                targetver = cudaver
                pipeline.append(generate_job(template, os, osver, spackver, target, targetver))

            for rocmver in config["rocmver"]:
                target = "rocm"
                targetver = rocmver
                pipeline.append(generate_job(template, os, osver, spackver, target, targetver))

print("\n\n".join(pipeline))
