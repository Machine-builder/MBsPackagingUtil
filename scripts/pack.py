import os, shutil
import jstyleson

from . import post_processing

class Pack():
    def __init__(self, path:str):
        self.path = path
        self.manifest_path = os.path.join(self.path, "manifest.json")
        self.reload()
    
    def reload(self):
        self.manifest = self.get_manifest()

    def save_changes(self):
        self.set_manifest(self.manifest)
    
    def get_manifest(self):
        return jstyleson.load(open(self.manifest_path, "r"))
    
    def set_manifest(self, data:object):
        return jstyleson.dump(data, open(self.manifest_path, "w"), indent=4)

    def get_pack_version(self) -> list:
        return self.manifest["header"]["version"]

    def set_pack_version(self, version:list):
        self.manifest["header"]["version"] = version
        for dependency in self.manifest.get("dependencies", []):
            uuid = dependency.get("uuid", None)
            if uuid is None: continue
            dependency["version"] = version
    
    def pack_to(self, filepath:str):
        """Packs this pack to a zip with the .mcpack
        extension, and saves to some filepath

        Args:
            filepath (str): Filepath to pack to. Omit the .mcpack extension.
        """
        shutil.make_archive(filepath, "zip", self.path)
        os.rename(filepath+".zip", filepath+".mcpack")

def pack_bp_and_rp(dir_file:str, bp:Pack, rp:Pack, filepath:str, post_processing_info:dict):
    tmp_folder = os.path.join(dir_file, "releases/tmp")
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)
    os.mkdir(tmp_folder)
    bp_path_tmp = os.path.join(dir_file, "releases/tmp/BP")
    rp_path_tmp = os.path.join(dir_file, "releases/tmp/RP")
    shutil.copytree(bp.path, bp_path_tmp)
    shutil.copytree(rp.path, rp_path_tmp)

    post_processing_minify = post_processing_info.get("minify_js", False)
    if post_processing_minify == "terser":
        post_processing.minify_js_terser(bp_path_tmp)
    elif post_processing_minify == "esbuild":
        post_processing.minify_js_esbuild(bp_path_tmp)
    post_processing_obscure = post_processing_info.get("obscure_json", False)
    if post_processing_obscure:
        post_processing.obscure_json(bp_path_tmp)
        post_processing.obscure_json(rp_path_tmp)

    shutil.make_archive(filepath, "zip", tmp_folder)
    os.rename(filepath+".zip", filepath+".mcaddon")
    shutil.rmtree(tmp_folder)