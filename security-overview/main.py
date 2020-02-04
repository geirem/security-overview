import configparser
import subprocess
from lib.FetchArtifact import FetchArtifact

# import git
# HOST = 'git.stb.intra'
from urllib3 import PoolManager

FILES_PATH = '../resources/deployments/'
FILES = [
    'server_deployment_client-p.txt',
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
        capture_output=False#, cwd='..'
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
