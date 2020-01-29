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

# g = git.cmd.Git(git_dir)
# g.pull()

# def load_file(pool: HTTPSConnectionPool, path: str) -> str:
#     result = pool.request('GET', path)
#     if result.status == 200:
#         return result.data.decode('utf-8')
#     raise Exception


def handle_docker_image(config, section):
    print(config[section]['resource.docker.name'])


def handle_artifact(config, section):
    print(config[section]['resource.maven.war.groupId'])


def main():
    # pool = HTTPSConnectionPool(HOST, maxsize=1)
    for file in FILES:
        config = configparser.ConfigParser(strict=False)
        # config.read_string(load_file(pool, FILES_PATH + file))
        with open(FILES_PATH + file, 'r') as inimage:
            config.read_string(inimage.read())
        # config.read_file(FILES_PATH + file)
        for section in config.sections():
            if 'resource.maven.war.groupId' in config[section]:
                handle_artifact(config, section)
                continue
            if 'resource.docker.name' in config[section]:
                handle_docker_image(config, section)
                continue
            print(f'[NOPE for {section}!')


main()
