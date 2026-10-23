#!/bin/sh
# usage: gen.sh name ref "prompt"
name=$1; ref=$2; prompt=$3
echo "Use your image generation tool to create ONE image, then save it as the file out/$name.png in the current directory. $prompt Use the attached image only as a STYLE reference: semi-realistic painterly Chinese wuxia digital illustration with fine textured brushwork, warm muted earthy palette, soft cinematic light. No text, no watermark, no border. After saving, verify the file exists and report its pixel size and mode. Do not modify any other files." | timeout 900 codex exec --skip-git-repo-check -s workspace-write -C . -i "$ref" - > "out/$name.log" 2>&1
echo "$name done: $(ls -la out/$name.png 2>&1)"
