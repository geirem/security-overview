import configparser
import json
import os
import subprocess

import requests
from lib.PomParser import PomParser
from lib.FetchArtifact import FetchArtifact
from urllib3 import PoolManager

API_KEY = os.environ['TRACK_API_KEY']
API_BASE_PATH = 'http://localhost:8080/api/v1'

headers = {
    'x-api-key': API_KEY,
    'content-type': 'application/json',
}

data = {
    'name': 'sdc-broker-rest-api',
    'version': '1.0.0',
    'description': 'SDC Broking',
    'tags': [
        {'name': 'happy'}
    ],
    'active': True,
}

r = requests.put(API_BASE_PATH + '/project', headers=headers, data=json.dumps(data))
print(r.status_code if r.status_code != 200 else r.text)
r = requests.get(API_BASE_PATH + '/project', headers=headers)
print(r.status_code if r.status_code != 200 else r.text)
exit(0)
pom = '../resources/pom.xml'
pp = PomParser(pom)
pp.gather()
for p in pp.get_dependencies():
    print(p)
exit(0)

FILES_PATH = '../resources/deployments/'
FILES = [
    'server_deployment_stage-p.txt',
]


# g = git.cmd.Git(git_dir)
# g.pull()

def parse_docker_config(section):
    return {
        'name': section['resource.docker.name'],
        'tag': section['resource.docker.version'],
        'type': 'docker',
    }


def parse_artifact_config(section):
    return {
        'groupId': section['resource.maven.war.groupId'],
        'artifactId': section['resource.maven.war.artifactId'],
        'version': section['resource.maven.war.version'],
        'type': section['resource.maven.war.type'],
        'static': True if 'resource.maven.war.isStatic' in section else False,
    }


# https://repo1.maven.org/maven2/struts/struts/1.2.2/struts-1.2.2.jar


def handle_artifact(pool_manager: PoolManager, config: dict) -> None:
    artifact_fetcher = FetchArtifact(pool_manager, config)
    artifact_fetcher.fetch()
    result = subprocess.run(
        ['..\\resources\\dependency-check\\bin\\dependency-check.bat', '-s', '..\\work\\*.jar'],
        capture_output=False  # , cwd='..'
    )
    print(result.stdout)


def main():
    pool_manager = PoolManager()
    for file in FILES:
        config = configparser.ConfigParser(strict=False)
        with open(FILES_PATH + file, 'r') as inimage:
            config.read_string(inimage.read())
        description = {
            'category': config['DEFAULT']['category'],
            'stage': config['DEFAULT']['stage.url.prefix'],
            'repo_url': config['DEFAULT']['repo.release'],
        }
        for section in config.sections():
            if section == 'DEFAULT':
                continue
            if 'resource.maven.war.groupId' in config[section]:
                config = {**description, **(parse_artifact_config(config[section]))}
                handle_artifact(pool_manager, config)
                continue
            if 'resource.docker.name' in config[section]:
                print({**description, **(parse_docker_config(config[section]))})
                continue
            print(f'[NOPE for {section}!')


main()
