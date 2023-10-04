RELEASE_TYPE = ["Major", "Minor", "Patch", "Repackage"]
CONFIG_DEFAULT = {
    "packs": [
        {
            "packaged_name": "OUTPUT_NAME_FOR_THIS_PACK",
            "path_bp": "FULL_PATH_TO_BEHAVIOR_PACK",
            "path_rp": "FULL_PATH_TO_RESOURCE_PACK",
            "outputs": [
                {
                    "packaged_suffix": "_Public",
                    "post_processing": {
                        "minify_js": "esbuild",
                        "obscure_json": True
                    }
                },
                {
                    "packaged_suffix": "_Private",
                    "post_processing": {}
                }
            ]
        }
    ],
    "releases_path": "FULL_PATH_TO_RELEASES_DIRECTORY",
    "notes": {
        "type_major": "🎉 Major Release 🎉",
        "type_minor": "✨ Minor Release ✨",
        "type_patch": "💻 Patch 💻",
        "type_repackage": "📁 Repackage 📁",
        "header_whats_new": "🚀 What's New",
        "header_bug_fixes": "🔧 Bug Fixes",
        "header_other_notes": "📚 Other Notes",
        "include_ctime": True
    }
}