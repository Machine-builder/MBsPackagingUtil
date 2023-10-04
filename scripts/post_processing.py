import os
import subprocess
import shutil
import jstyleson

def minify_js_terser(folder_path:str):
    scripts_path = os.path.join(folder_path, "scripts")
    if not os.path.exists(scripts_path): return False
    for root, dirs, files in os.walk(scripts_path, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            _, ext = os.path.splitext(filepath)
            if ext == ".js":
                command = f'terser --compress --mangle -- "{filepath}"'
                output = subprocess.getoutput(command)
                with open(filepath, "w") as f:
                    f.write(output)

def minify_js_esbuild(folder_path:str):
    scripts_path = os.path.join(folder_path, "scripts")
    main_js_path = os.path.join(scripts_path, "main.js")
    main_js_path_tmp = os.path.join(folder_path, "tmp_main.js")
    command = f'esbuild "{main_js_path}" --minify '\
        f'--bundle --target=es2020 --format=esm '\
        f'--outfile="{main_js_path_tmp}" '\
        f'--external:@minecraft/server '\
        f'--external:@minecraft/server-ui '\
        f'--external:@minecraft/server-admin '\
        f'--external:@minecraft/server-editor '\
        f'--external:@minecraft/server-net '\
        f'--external:@minecraft/server-gametest '\
        f'--external:@minecraft/vanilla-data'
    esbuild_output = subprocess.getoutput(command)
    if os.path.exists(main_js_path_tmp):
        shutil.rmtree(scripts_path)
        os.mkdir(scripts_path)
        with open(main_js_path, "wb") as f:
            with open(main_js_path_tmp, "rb") as f2:
                f.write(f2.read())
        os.remove(main_js_path_tmp)
    else:
        print("ERROR esbuild failed to process code. Command and output:")
        print(command)
        print(esbuild_output)

def recursive_json_encode(data):
    if type(data) == dict:
        newdata = {}
        for k,v in list(data.items()):
            k2 = recursive_json_encode(k)
            v2 = recursive_json_encode(v)
            newdata[k2] = v2
        return newdata
    elif type(data) == list:
        return [recursive_json_encode(i) for i in data]
    elif type(data) == str:
        return "".join([
            "\\u"+hex(ord(character))[2:].rjust(4, "0")
            for character in data])
    return data

def obscure_json(folder_path:str):
    skip_filenames = [
        "manifest.json"
    ]
    for root, _, files in os.walk(folder_path, topdown=False):
        for name in files:
            if name in skip_filenames:
                continue
            filepath = os.path.join(root, name)
            _, ext = os.path.splitext(filepath)
            if ext == ".json":
                try:
                    with open(filepath, "r") as f:
                        data = jstyleson.load(f)
                except:
                    print("Failed to read file", filepath)
                    continue
                encoded_data = recursive_json_encode(data)
                try:
                    with open(filepath, "wb") as f:
                        out = jstyleson.dumps(
                            encoded_data,
                            separators=(",", ":"),
                            ensure_ascii=False).encode().replace(b"\\\\", b"\\")
                        f.write(out)
                except:
                    print("Failed to write file", filepath)
                    continue