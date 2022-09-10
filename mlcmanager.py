import os,yaml,contextlib
import subprocess


# https://stackoverflow.com/a/13847807
@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)


class mlcmgr:
    def __init__(self):
        if not os.path.exists("config.yml"):
            src = input("Git url for configs repo: ")
            dst = input("Where would you like the root to be (dir): ")
            subdirs = []
            has_subdirs = input("Does your repo have subdirs? (Y/n): ")
            if has_subdirs != "n":
                newd = 'foo'
                while newd != "done":
                    newd = input("Subdir (or 'done'): ")
                    if newd == "done":
                        break
                    else:
                        subdirs.append(newd)
                has_subdirs = True
            else:
                has_subdirs = False

            settings = {
                "src": src,
                "dst": dst,
                "has_subdirs": has_subdirs,
                "subdirs": subdirs
            }
            with open("config.yml", "w") as f:
                f.write(yaml.dump(settings))

        self.config = yaml.safe_load(open("config.yml").read())
        self.init_workspace()

    def init_workspace(self):
        if not os.path.exists(self.config["dst"]):
            os.system(f"git clone {self.config['src']} {self.config['dst']}")
            if not self.config['has_subdirs']:
                os.system(f"cd {self.config['dst']} && mlc init")
            else:
                for subdir in self.config['subdirs']:
                    os.system(f"cd {self.config['dst']} && cd {subdir} && mlc init && cd ../")

    def pull_all(self):
        if self.config['has_subdirs']:
            for subdir in self.config['subdirs']:
                os.system(f"cd {self.config['dst']} && cd {subdir} && mlc pull && cd ../")
        else:
            os.system(f"cd {self.config['dst']} && mlc pull && cd ../")
        return "Done"

    def get_info(self, subdir=None):
        extra = self.config['dst']
        if subdir is not None:
            extra += "/" + subdir

        with pushd(extra):
            out = subprocess.check_output(["mlc","info"]).decode('utf-8')
        return out

    def list_packages(self, subdir=None):
        extra = self.config['dst']
        if subdir is not None:
            extra += "/" + subdir

        return os.listdir(extra)

    def build(self, package, subdir=None):
        p = self.config['dst']
        if subdir is not None:
            p += "/" + subdir
        with pushd(p):
            os.system(f"mlc build {package}")

    def gen_repo(self, subdir=None):
        p = self.config['dst']
        if subdir is not None:
            p += "/" + subdir
        with pushd(p):
            os.system("mlc repo-gen")


if __name__ == "__main__":
    mlc = mlcmgr()
    #mlc.pull_all()
    mlc.build("base", "any")