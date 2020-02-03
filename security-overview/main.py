import configparser
import subprocess

import urllib3

# import git
# HOST = 'git.stb.intra'
from urllib3 import PoolManager

FILES_PATH = '../resources/deployments/'
FILES = [
    'server_deployment_client-p.txt',
]


# g = git.cmd.Git(git_dir)
# g.pull()

# def load_file(pool: HTTPSConnectionPool, path: str) -> str:
#     result = pool.request('GET', path)
#     if result.status == 200:
#         return result.data.decode('utf-8')
#     raise Exception


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


#https://repo1.maven.org/maven2/struts/struts/1.2.2/struts-1.2.2.jar

def handle_artifact(pool_manager: PoolManager, config: dict) -> None:
    (group_id, artifact_id, version, extension) = (
        config['groupId'], config['artifactId'], config['version'], config['type']
    )
    file_name = f'{artifact_id}-{version}.{extension}'
    sha1_file_name = f'{artifact_id}-{version}.sha1'
    base_url = f'{config["repo_url"]}{group_id}/{artifact_id}/{version}'
    file_url = f'{base_url}/{file_name}'
    sha1_url = f'{base_url}/{sha1_file_name}'
    r = pool_manager.request('GET', file_url, preload_content=False)
    fq_file_name = f'../work/{file_name}'
    with open(fq_file_name, 'wb') as outimage:
        while True:
            data = r.read(1024*64)
            if not data:
                break
            outimage.write(data)
    r.release_conn()
    result = subprocess.run(['../resources/dependency-check/bin/dependency-check.bat', fq_file_name], capture_output=True)
    print(result.stdout)

def main():
    pool_manager = urllib3.PoolManager()
    # shutil.e('work')
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
