import json

def load_config(config_file='config.json'):
    with open(config_file, 'r') as file:
        return json.load(file)

def generate_requirements():
    import pkg_resources
    import subprocess

    installed_packages = [d for d in pkg_resources.working_set]
    requirements = [f"{package.key}=={package.version}" for package in installed_packages]

    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))

    print("requirements.txt has been generated.")
