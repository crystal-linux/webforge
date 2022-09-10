import os, yaml, contextlib
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
                newd = "foo"
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
                "subdirs": subdirs,
            }
            with open("config.yml", "w") as f:
                f.write(yaml.dump(settings))

        self.config = yaml.safe_load(open("config.yml").read())
        self.init_workspace()

    def init_workspace(self):
        if not os.path.exists(self.config["dst"]):
            os.system(f"git clone {self.config['src']} {self.config['dst']}")
            if not self.config["has_subdirs"]:
                os.system(f"cd {self.config['dst']} && mlc init")
            else:
                for subdir in self.config["subdirs"]:
                    os.system(
                        f"cd {self.config['dst']} && cd {subdir} && mlc init && cd ../"
                    )

    def pull_all(self):
        if self.config["has_subdirs"]:
            for subdir in self.config["subdirs"]:
                os.system(
                    f"cd {self.config['dst']} && cd {subdir} && mlc pull && cd ../"
                )
        else:
            os.system(f"cd {self.config['dst']} && mlc pull && cd ../")
        return "Done"

    def get_info(self, subdir=None):
        extra = self.config["dst"]
        if subdir is not None:
            extra += "/" + subdir

        with pushd(extra):
            out = subprocess.check_output(["mlc", "info"]).decode("utf-8")
        return out

    def list_packages(self, subdir=None):
        extra = self.config["dst"]
        if subdir is not None:
            extra += "/" + subdir

        all_files = os.listdir(extra)
        bad = ["mlc.toml", "README.md"]
        for thing in bad:
            if thing in all_files:
                all_files.remove(thing)
        return all_files

    def build(self, package, subdir=None):
        p = self.config["dst"]
        if subdir is not None:
            p += "/" + subdir
        with pushd(p):
            os.system(f"mlc build {package}")

    def gen_repo(self, subdir=None):
        p = self.config["dst"]
        if subdir is not None:
            p += "/" + subdir
        with pushd(p):
            os.system("mlc repo-gen")

    def html_list_packages(self, subdir=None):
        raw = self.list_packages(subdir)
        html = "<ul>"
        for pkg in raw:
            html += f"<li><p>- <a class='slicklink' href='/packages/{subdir+'/' if subdir is not None else ''}{pkg}'>{pkg}</a></p></li><br/>"
        html += "</ul>"
        return html

    def dump_pkgbuild(self, package, subdir=None):
        p = self.config["dst"]
        if subdir is not None:
            p += "/" + subdir
        p += "/" + package
        with pushd(p):
            return open("PKGBUILD").read()

    def pkg_info(self, package, subdir=None):
        p = self.config["dst"]
        if subdir is not None:
            p += "/" + subdir
        p += "/" + package
        with pushd(p):
            pkgbuild = open("PKGBUILD").read()
            pkgbuild_lines = pkgbuild.split("\n")
        info = {}
        for line in pkgbuild_lines:
            if "=" in line:
                info[line.split("=")[0]] = line.split("=")[1]
        return info

    def pkg_page(self, package, subdir=None):
        info = self.pkg_info(package, subdir)
        html = f"<h2>pkgname: <code>{info['pkgname']}</code></h2>"
        html += f"<p>Version: <code>{info['pkgver']}</code></p>"
        html += f"<p>Rel: <code>{info['pkgrel']}</code></p>"
        html += f"<p>Desc: <code>{info['pkgdesc']}</code></p>"
        s_url = info["url"].replace("'", "").replace('"',"").replace("$pkgname", info['pkgname'])
        html += f"<p>URL: <a class='slicklink' href='{s_url}'>{s_url}</a></p>"
        html += f"<p>You can view the whole pkgbuild <a href='/pkgbuild/{subdir}/{package}'>here</a></p>"
        return html

    def list_repos(self):
        if not self.config['has_subdirs']:
            return []
        else:
            return self.config['subdirs']

    def html_repo_list(self):
        repos = self.list_repos()
        html = "<ul>"
        for repo in repos:
            html += f"<li><p><a class='slicklink' href='/repos/{repo}'>{repo}</a></p></li><br/>"
        html += "</ul>"
        return html

if __name__ == "__main__":
    mlc = mlcmgr()
    # mlc.pull_all()
    # mlc.build("base", "any")
    print(mlc.pkg_info("base", "any"))
