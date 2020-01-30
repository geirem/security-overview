# from urllib3 import HTTPSConnectionPool, HTTPResponse
import configparser
# import git

# HOST = 'git.stb.intra'
FILES_PATH = '../../deployment-prod/'
# FILES_PATH = '/projects/OPS/repos/deployment-prod/raw/'
FILES = [
    'alp-stb-004fp_deployment_client-p.txt',
    # 'alp-stb-005fp_deployment_client-p.txt',
    # 'alp-stb-004fp_deployment_cms-prod.txt',
    # 'alp-stb-005fp_deployment_client-beta.txt',
    # 'alp-stb-005fp_deployment_cms-prod.txt',
    # 'alp-stb-006fp_deployment_client-p.txt',
    # 'alp-stb-006fp_deployment_cms-prod.txt',
]


# pool = HTTPSConnectionPool(HOST, maxsize=1)

# g = git.cmd.Git(git_dir)
# g.pull()

# def load_file(pool: HTTPSConnectionPool, path: str) -> str:
#     result = pool.request('GET', path)
#     if result.status == 200:
#         return result.data.decode('utf-8')
#     raise Exception


def handle_docker_image(section):
    return {
        'name': section['resource.docker.name'],
        'tag': section['resource.docker.version'],
        'type': 'docker',
    }


def handle_artifact(section):
    return {
        'groupId': section['resource.maven.war.groupId'],
        'artifactId': section['resource.maven.war.artifactId'],
        'version': section['resource.maven.war.version'],
        'type': section['resource.maven.war.type'],
        'static': True if 'resource.maven.war.isStatic' in section else False,
    }


def main():
    for file in FILES:
        environment = file.split('_')[2].replace('.txt', '')
        config = configparser.ConfigParser(strict=False)
        with open(FILES_PATH + file, 'r') as inimage:
            config.read_string(inimage.read())
        description = {
            'environment': environment,
            'repo_url': config['DEFAULT']['repo.release']
        }
        for section in config.sections():
            if section == 'DEFAULT':
                continue
            if 'resource.maven.war.groupId' in config[section]:
                print({**description, **(handle_artifact(config[section]))})
                continue
            if 'resource.docker.name' in config[section]:
                print({**description, **(handle_docker_image(config[section]))})
                continue
            print(f'[NOPE for {section}!')


main()
